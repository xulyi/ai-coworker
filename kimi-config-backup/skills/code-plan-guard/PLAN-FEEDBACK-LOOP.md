# Plan Feedback Loop — 反馈循环排查指南

> 本文档同时存在于两个 skill 目录,内容相同:
> - `~/.claude/skills/code-plan-guard/PLAN-FEEDBACK-LOOP.md`
> - `~/.claude/skills/planning-with-files/PLAN-FEEDBACK-LOOP.md`
>
> 任一目录都能完整查看。出现 plan 相关问题时,从这里开始排查。

---

## 1. 这个机制为什么存在

**问题背景**:AI 看到"plan"关键词时,**不会自觉调用** code-plan-guard / planning-with-files。导致:

- 复杂任务跳过 plan 直接动手
- `task_plan.md` 不被创建,`/clear` 后无法恢复
- 用户写在 CLAUDE.md 里的硬规则空转

**解决思路**:用 hook + 日志构建**双层"信任但验证"** 闭环:

- **第一层(用户可见层)**:UserPromptSubmit hook 命令 AI 调 skill,AI 必须 tail 日志并把内容贴在回答**最顶部(对话第一页)**。用户能直接看到验证结果,出问题立刻能发现。
- **第二层(代码兜底层)**:Stop hook 在 AI 试图结束响应时独立检查日志 60 秒窗口,缺哪个 skill 就 block,要求 AI 重调。代码判断,不依赖 AI 自觉。

两层都缺失 skill 时,Stop 会反复 block 直到补齐;两层都通过时,放行。

---

## 2. 整体流程图

```
[用户输入含 plan 关键词]
        ↓
[UserPromptSubmit hook]                 ← 第一层(用户可见)
~/.claude/hooks/plan-trigger.sh
检测关键词 → 注入 systemMessage 指令
        ↓
[AI 必须按指令调]
Skill code-plan-guard
Skill planning-with-files
        ↓
[PostToolUse(matcher:Skill) hook]
~/.claude/hooks/log-skill-call.sh
写一行 [时间戳] skill_name 到日志
        ↓
[AI 必须 Bash 验证]
tail -10 ~/.claude/logs/plan-skill-calls.log
        ↓
[AI 必须展示]
回答最顶部贴日志(对话第一页)
        ↓
[AI 必须验证]
60 秒内两个 skill 都有记录?
   ✅ 通过 → 进入正式响应
   ❌ 缺失 → 返工(重调缺失 skill,再 tail 再展示)
        ↓
[AI 完成响应,试图结束]
        ↓
[Stop hook]                            ← 第二层(代码兜底)
~/.claude/hooks/plan-stop-verify.sh
1. 读 transcript_path 取最后用户 prompt
2. 跑同一份 plan 关键词正则
3. 命中 → 查日志 60 秒窗口
4. 缺哪个 → {"decision":"block","reason":"请先调用 X"} 拦截
5. 齐了 → exit 0 静默放行
        ↓
[若被 block]
AI 在同一轮继续:用 Skill 工具补调缺失 skill
重新触发 Stop hook,直到齐全
```

---

## 3. 涉及文件清单

| 文件 | 作用 | 修改入口 |
|------|------|---------|
| `~/.claude/hooks/plan-trigger.sh` | UserPromptSubmit hook,关键词检测 + 注入指令(第一层) | 改关键词列表 / 改注入文案 |
| `~/.claude/hooks/log-skill-call.sh` | PostToolUse(Skill) hook,写日志 | 改 skill 白名单 / 改字段提取 jq |
| `~/.claude/hooks/plan-stop-verify.sh` | **Stop hook,代码侧兜底验证(第二层)** | 改关键词正则 / 调 60 秒窗口 / 改 block 文案 |
| `~/.claude/settings.json` | 注册以上三个 hook | 不要轻易改结构 |
| `~/.claude/logs/plan-skill-calls.log` | 调用日志(自动生成) | 偶尔人工清理 |

⚠️ **关键词正则双份维护**:`plan-trigger.sh` 和 `plan-stop-verify.sh` 各自内嵌一份 `KEYWORDS_CN` / `KEYWORDS_EN`,改一处必须同步另一处。两处不一致会导致"UserPromptSubmit 命中但 Stop 不验证"或反之。

---

## 4. 触发条件

`plan-trigger.sh` 和 `plan-stop-verify.sh` 共用同一份关键词,触发当且仅当:

1. prompt 长度 ≥ 6 字符(避免单字 "plan" 误触发,仅 plan-trigger.sh 检查)
2. prompt 包含以下任一关键词(大小写不敏感):
   - **中文**: `分析|建模|清洗|模拟|设计|重构|开发|架构|方案|规划|搭建|改造|生成数据|训练数据|创建系统|做X流程|做X计划|绩效|项目|实施|路线图`
   - **英文**: `(^|[^a-zA-Z])plan([^a-zA-Z]|$)` — 词边界匹配,避免 explain/airplane/replant 误命中

Stop hook 取的是 transcript 中最后一条 `type:"user"` 且 content 是字符串的消息(排除 tool_result 这类 array content),保证拿到真实用户输入。

---

## 5. 验证标准

`tail -10 ~/.claude/logs/plan-skill-calls.log` 末尾 10 行内,**必须同时**包含:

- `code-plan-guard` 至少一条
- `planning-with-files` 至少一条
- 两条时间戳都在**最近 60 秒**内

任一缺失 → 第一层 AI 必须返工;若 AI 偷懒跳过返工,第二层 Stop hook 会自动 block,要求继续调用。

---

## 6. 排查清单(出错时按症状查)

### 症状 A: 关键词命中了,但 AI 没调 skill

**自查命令**:
```bash
echo '{"prompt":"先plan,帮我做 X"}' | bash ~/.claude/hooks/plan-trigger.sh | jq .
```
期望: 输出包含 `systemMessage` 和 `additionalContext`。

**可能原因**:
1. `settings.json` 不合法 → `jq . ~/.claude/settings.json`
2. AI 上下文里没收到 hook 输出 → 重启会话
3. AI 看到了指令但偷懒不调 → 第二层 Stop hook 应自动 block;若没 block 看症状 F

### 症状 B: AI 调了 skill 但日志空

**自查命令**:
```bash
echo '{"tool_input":{"skill":"code-plan-guard"}}' | bash ~/.claude/hooks/log-skill-call.sh
cat ~/.claude/logs/plan-skill-calls.log
```
期望: 日志多一行 `[YYYY-MM-DD HH:MM:SS] code-plan-guard`。

**可能原因**:
1. `.tool_input.skill` 字段名变了(Claude Code 升级) → 改 `log-skill-call.sh` 里的 jq 表达式
2. `~/.claude/logs/` 不存在或无写权限 → `mkdir -p ~/.claude/logs`
3. `settings.json` 里 `matcher: "Skill"` 没注册 → 检查 PostToolUse 数组

### 症状 C: 日志有内容,但 AI 没在第一页展示

**根因**: AI 没遵守 hook 的 additionalContext 指令(服从度问题)。

**修复**:
- 检查 plan-trigger.sh 的指令措辞是否够强
- 在 `~/.claude/CLAUDE.md` 加硬规则:"看到日志验证标题,必须放回答顶部"
- 注:即使第一层失守,第二层 Stop hook 仍会兜底拦截;首页展示主要是给用户看的,不影响功能正确性

### 症状 D: 验证不通过,但 AI 没返工

**自查**:
- AI 的回答里有没有"60 秒内两个 skill 都有"这种检查文字?
- 没有 → 第一层失守;但 Stop hook 应该 block 掉响应,看症状 F

### 症状 E: hook 误触发(用户不想要 plan)

**根因**: 关键词列表覆盖太广。

**修复方案**:
- 用户在 prompt 里加 "skip-plan" 标识,plan-trigger.sh 和 plan-stop-verify.sh 都加白名单跳过
- 或精简关键词列表(两处都要改)

### 症状 F: Stop hook 行为异常(新增)

**F-1: Stop hook 应该 block 但没 block**

**自查命令**:
```bash
# 模拟 plan 关键词 + 缺失日志,期望输出 block JSON
echo '{"transcript_path":"/tmp/fake-plan.jsonl"}' > /tmp/fake-input.json
echo '{"type":"user","message":{"role":"user","content":"先 plan 一下重构"}}' > /tmp/fake-plan.jsonl
PLAN_SKILL_LOG=/tmp/empty-log.txt touch /tmp/empty-log.txt
echo '{"transcript_path":"/tmp/fake-plan.jsonl"}' | PLAN_SKILL_LOG=/tmp/empty-log.txt bash ~/.claude/hooks/plan-stop-verify.sh
```
期望: 输出 `{"decision":"block","reason":"..."}`。

**可能原因**:
1. transcript JSONL 字段格式变了(`.type` 或 `.message.content`)→ 改 plan-stop-verify.sh 的 jq 表达式
2. settings.json 里 Stop hook 没注册 → `jq '.hooks.Stop' ~/.claude/settings.json`
3. plan-stop-verify.sh 没可执行权限 → `chmod +x`
4. 关键词正则两处不一致 → diff 两个脚本的 KEYWORDS_CN / KEYWORDS_EN

**F-2: Stop hook 误 block 普通查询**

**根因**: 用户 prompt 偶然命中关键词(如"plan-trigger.sh 怎么改"中的 plan)。

**修复**:
- 临时绕过:在 prompt 里避免使用关键词(如改成 "ptg 脚本怎么改")
- 长期方案:在 plan-stop-verify.sh 加 skip-plan 白名单

**F-3: Stop hook 死循环 block**

**自查**: 日志里 60 秒窗口持续没有 skill 调用记录,但 AI 又不调用 skill。

**可能原因**:
1. PostToolUse(Skill) hook 没生效 → AI 调了 skill 但没写日志 → 看症状 B
2. AI 的服从度极低,反复忽略 block reason → Claude Code 自身有最大迭代次数,会自动放行;手动 Ctrl-C 中断也行

---

## 7. 手动验证命令

```bash
# 测试 UserPromptSubmit hook 触发
echo '{"prompt":"先plan,帮我做 X"}' | bash ~/.claude/hooks/plan-trigger.sh | jq .

# 测试日志写入
echo '{"tool_input":{"skill":"code-plan-guard"}}' | bash ~/.claude/hooks/log-skill-call.sh
echo '{"tool_input":{"skill":"planning-with-files"}}' | bash ~/.claude/hooks/log-skill-call.sh
tail ~/.claude/logs/plan-skill-calls.log

# 测试 Stop hook(全场景)
mkdir -p /tmp/plan-test && cd /tmp/plan-test
echo '{"type":"user","message":{"role":"user","content":"先 plan 一下重构"}}' > t-plan.jsonl
echo '{"type":"user","message":{"role":"user","content":"读一下文件"}}' > t-noplan.jsonl
NOW=$(date +'%Y-%m-%d %H:%M:%S')
printf '[%s] code-plan-guard\n[%s] planning-with-files\n' "$NOW" "$NOW" > log-both.txt
printf '[%s] code-plan-guard\n' "$NOW" > log-onlyguard.txt
# 场景 B:齐全 → 期望 exit 0 无输出
echo '{"transcript_path":"/tmp/plan-test/t-plan.jsonl"}' | PLAN_SKILL_LOG=/tmp/plan-test/log-both.txt bash ~/.claude/hooks/plan-stop-verify.sh
# 场景 C:缺 planning-with-files → 期望 block JSON
echo '{"transcript_path":"/tmp/plan-test/t-plan.jsonl"}' | PLAN_SKILL_LOG=/tmp/plan-test/log-onlyguard.txt bash ~/.claude/hooks/plan-stop-verify.sh
# 场景 D:非 plan 任务 → 期望 exit 0
echo '{"transcript_path":"/tmp/plan-test/t-noplan.jsonl"}' | PLAN_SKILL_LOG=/tmp/plan-test/log-both.txt bash ~/.claude/hooks/plan-stop-verify.sh
cd ~ && rm -rf /tmp/plan-test

# 测试 settings.json 合法
jq . ~/.claude/settings.json > /dev/null && echo "✅ settings.json OK"
jq '.hooks.Stop' ~/.claude/settings.json    # 确认 Stop hook 注册了

# 测试无关 skill 不被记录(应该日志不增长)
echo '{"tool_input":{"skill":"random-skill"}}' | bash ~/.claude/hooks/log-skill-call.sh

# 清理日志(慎用,会丢失历史)
> ~/.claude/logs/plan-skill-calls.log
```

---

## 8. 不要做的事

- ❌ **不要相信** SKILL.md frontmatter 里的 hooks 会自动全局注册 — 实测表明真正生效的是 `~/.claude/settings.json` 注册的全局 hooks
- ❌ **不要把关键词列表拉太宽** — 容易在普通查询里误触发
- ❌ **不要赌 AI 自觉调 skill** — 必须靠 hook 注入指令(第一层) + Stop hook 兜底(第二层) + 日志验证
- ❌ **不要在 log-skill-call.sh 记录所有 skill** — 只记录 plan 相关两个,避免日志噪音
- ❌ **不要只改一份关键词正则** — plan-trigger.sh 和 plan-stop-verify.sh 必须同步,否则两层会失配
- ❌ **不要让 Stop hook 跑 async** — Stop 必须同步,Claude Code 才会等待 block 决定;async 会导致 AI 提前结束响应

---

## 9. 历史

| 日期 | 事件 |
|------|------|
| 2026-05-04 | 用户测试发现"先plan,帮我..."中英文混合 prompt **完全没命中** plan-trigger.sh(关键词列表只有中文) |
| 2026-05-04 | 同时验证: AI 看到 `plan` 关键词**不会自觉**调 code-plan-guard / planning-with-files,且 SKILL.md frontmatter hooks 大概率不生效 |
| 2026-05-04 | 加英文 `plan` 关键词,改 systemMessage 显式命令调两个 skill,加 PostToolUse(Skill) 写日志,加 60 秒窗口验证 + 返工流程 |
| 2026-05-04 | 实测 6 项不确定点全部通过(关键词命中 / matcher:"Skill" 真能匹配 / `.tool_input.skill` 字段名对 / 60 秒窗口生效 / AI 服从度足够 / 日志干净) |
| 2026-05-04 | 英文关键词收紧到词边界 `(^\|[^a-zA-Z])plan([^a-zA-Z]\|$)`,避免 explain/airplane/replant 误命中 |
| 2026-05-04 | 加第二层兜底:新增 Stop hook `plan-stop-verify.sh`,代码侧独立检查日志 60 秒窗口,缺 skill 就 `{"decision":"block"}`。第一层 AI 偷懒时第二层会拦截。离线 5/5 场景测试通过 |

---

## 10. 设计哲学

**为什么用日志而不是直接 inline 验证?**

日志是"第三方证据"。如果只让 AI 自己说"我调了",那就是 AI 自我证明。日志由 PostToolUse hook 写入,不依赖 AI,不可被 AI 伪造。

**为什么要求展示在第一页?**

把验证证据放在用户最先看到的位置,出问题时**用户也能立刻发现** — 而不是 AI 偷偷跳过然后给个看似正确的答案。

**为什么 60 秒窗口而不是直接看最后两行?**

避免历史日志干扰。比如用户在 30 分钟前调过一次,如果只看最后两行,可能"看起来通过"实际上本次根本没调。60 秒窗口强制本次会话内的真实调用。

**为什么要双层(UserPromptSubmit + Stop)?**

- 第一层(UserPromptSubmit + AI 展示日志):用户**可见**,出错用户立刻发现;但依赖 AI 服从度,AI 可能跳过展示和返工。
- 第二层(Stop hook):代码判断,**不可被 AI 伪造**;AI 试图结束响应时强制 block,缺 skill 就重来。但用户看不到这一层在工作。

**两者并存**:用户层(可见性)+ 代码层(可靠性)互补。出问题时:第一层失守 → 用户可能没注意到日志缺失 → 第二层兜底拦截。两层都通过 → 真的通过。

**为什么 Stop hook 不抽出共享 lib?**

理论上更优雅,但 plan-trigger.sh 已稳定运行,改它需要重新测试。两脚本各自内嵌正则、文档强调"双份同步",维护成本可控,改动风险更低。
