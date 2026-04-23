# Codex ↔ Kimi 协议适配层

解决 **Codex CLI（OpenAI Responses API）与 Kimi（仅兼容 Chat Completions API）** 的协议不匹配问题。

## 原理

Codex CLI 默认调用 `/v1/responses`（OpenAI Responses API），而 Kimi 只支持 `/v1/chat/completions`。

本适配层作为本地代理：

```
Codex CLI → localhost:3456/v1/responses → 适配层转换 → Kimi /v1/chat/completions
                ↑                                    ↓
           返回 Responses 格式 ←─── 转换响应格式 ────┘
```

## 快速开始

### 1. 准备环境

需要 Node.js 18+（内置 `fetch` 支持，但本脚本使用原生 `http/https` 模块，零依赖）。

### 2. 设置环境变量

```bash
export KIMI_API_KEY="sk-你的Kimi密钥"
# 默认已指向 Kimi For Coding 端点，无需额外设置：
# https://api.kimi.com/coding/v1
# 如需覆盖（例如使用 Moonshot 主站或其他代理）：
# export KIMI_BASE_URL="https://api.moonshot.cn/v1"
```

### 3. 启动适配层

```bash
cd /Users/leyixu/Ai\ cowork/coding
node src/codex-kimi-adapter.js
```

默认监听 `http://localhost:3456`。

### 4. 让 Codex 走适配层

```bash
export OPENAI_BASE_URL="http://localhost:3456"
export OPENAI_API_KEY="dummy-key"  # Codex 需要这个环境变量，值随意，真实请求会走 KIMI_API_KEY
codex
```

## 支持的转换

| Responses API 字段 | Chat Completions 映射 |
|-------------------|----------------------|
| `input` (string / array) | `messages` |
| `model` | 直接透传 |
| `temperature`, `top_p`, `max_tokens`, `stop`, `presence_penalty`, `frequency_penalty`, `seed` | 直接透传 |
| `tools` / `tool_choice` | 直接透传 |
| `stream` | 直接透传 |

### 响应转换

- **非流式**：将 `choices[0].message` 转换为 Responses API 的 `output[0].content`（`output_text` / `tool_call`）
- **流式**：将 Kimi 的 SSE 事件转换为 Responses API 的 SSE 事件（`response.created` / `output_text.delta` / `response.completed`）

## 已知限制

1. **Responses API 特有功能未支持**：
   - `instructions`（系统提示）—— 如有需要可手动拼接到 messages 前
   - `previous_response_id`（多轮上下文）—— 需要客户端自行维护 messages
   - `reasoning` / `reasoning_effort`（推理模型参数）—— Kimi 侧不支持
   - `web_search` / `file_search` 等内置工具 —— 未做转换

2. **流式事件不完整**：
   - 当前只实现了核心文本增量事件。Codex CLI 若依赖其他边缘事件（如 `response.output_item.done`），可能需要补充。

3. **工具调用流式增量**：
   - 简单透传了 `tool_calls` delta，但复杂参数拼接场景未充分测试。

## 调试

适配层会打印转发日志：

```
[→ Kimi] model=kimi-k2-0711-preview stream=true
```

如果 Codex 报错，可检查：

1. 适配层是否启动（`curl http://localhost:3456/health`）
2. Kimi API Key 是否有效
3. Codex 的 `OPENAI_BASE_URL` 是否指向了适配层地址
4. 模型名称是否在 Kimi 侧有效（Codex 默认可能带 `gpt-4o` 等模型名，需在 Codex 配置中改为 Kimi 支持的模型，如 `kimi-k2-0711-preview`）

## 扩展思路

如需更强的兼容性，可考虑：

- **集成到 cc-switch**：在路由层根据 `upstream` 类型自动选择是否走转换层（如 `type: "kimi-compat"`）
- **多上游支持**：扩展为通用 OpenAI-Compat 代理，同时支持 Claude / Gemini 等更多后端
