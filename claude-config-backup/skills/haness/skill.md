---
name: haness
description: This skill should be used when the user asks to "haness", "打包本次对话", "对话移交", "session handoff", "export session", "保存对话", "对话快照", or when the user wants to compress the current conversation and its artifacts for a new AI session. Unlike `handoff` which captures the entire project state, haness only captures the current conversation's summary and artifacts produced during this session.
hooks:
  UserPromptSubmit:
    - hooks:
        - type: command
          command: "sh \"${CLAUDE_SKILL_DIR}/scripts/detect-unloaded-haness.sh\" 2>/dev/null || sh \"$HOME/.claude/skills/haness/scripts/detect-unloaded-haness.sh\" 2>/dev/null"
  Stop:
    - hooks:
        - type: command
          command: "sh \"${CLAUDE_SKILL_DIR}/scripts/check-haness-pending.sh\" 2>/dev/null || sh \"$HOME/.claude/skills/haness/scripts/check-haness-pending.sh\" 2>/dev/null"
---

# Haness — Conversation Snapshot

Generate a lightweight, self-contained snapshot of the **current conversation** and its **artifacts** for transfer to a new Claude Code session.

Unlike `handoff` (project-level, heavy, captures entire workspace), `haness` is **conversation-level, lightweight, and focused**. It answers: "What did we do in this conversation, and what files did we produce?"

## When to Use

Use this skill when:
- The user says "haness", "打包本次对话", "对话移交", "session handoff", "export session"
- The user wants to start a new session but carry over the current conversation's context and artifacts
- The current conversation has produced files (code, docs, configs) that need to be preserved with context
- `handoff` is too heavy — the user doesn't need the entire project, just this session

Do NOT use this skill when:
- The user wants a full project snapshot (use `handoff` instead)
- The conversation has no meaningful decisions, artifacts, or next steps to preserve

## File Output

Write the haness document to a markdown file at `.claude/haness/<YYYYMMDD-HHMMSS>-<topic-slug>.md` (relative to the project root or current working directory). Create the directory if it does not exist.

If artifact copies are needed, store them in `.claude/haness/artifacts/<timestamp>-<filename>`.

After writing the file, output the following to the user. Do NOT print the full haness content. You MUST replace all placeholders with actual values from the generated file.

```
========================================
Haness 已生成
========================================

文件路径: <ABSOLUTE_PATH_TO_FILE>

----------------------------------------
使用说明
----------------------------------------

方式一：在新会话中加载
直接复制下面整行命令，粘贴到新 Claude Code 会话即可：

  加载 haness <FILENAME>

方式二：手动复制提示词（从 haness 文件中）
打开上面的文件，复制 "New Session Prompt" 区块
的内容，粘贴到新 Claude Code 会话即可

以上两种方式任选其一。

方式三：产物文件
本 haness 关联的产物已记录在文件中，新 AI 会
自动读取它们

----------------------------------------
新会话提示词（直接复制使用）
----------------------------------------
<PASTE_THE_FULL_CONTENT_OF_THE_New_Session_Prompt_BLOCK_HERE>

========================================
```

**Placeholder replacement rules:**
- `<ABSOLUTE_PATH_TO_FILE>` → the absolute path of the generated haness file
- `<FILENAME>` → just the filename (e.g. `20260503-101500-calf-muscle-sim-v3.md`), no path
- `<PASTE_THE_FULL_CONTENT_OF_THE_New_Session_Prompt_BLOCK_HERE>` → read the generated haness file, extract the entire content between the triple-backticks under `## New Session Prompt`, and paste it here verbatim

## Artifact Discovery Strategy (4-tier fallback)

The AI does not naturally know which files were created during a conversation. Use this fallback chain, **prioritizing automated tracking over human memory**:

### Tier 1: Auto-tracked session log (most reliable)
A `PostToolUse` hook automatically records git status after every Write/Edit tool call.
1. Check if `.claude/haness/session-artifacts.log` exists in the project root
2. If yes, read and parse it. Each entry looks like:
   ```
   [2026-01-15T10:30:00] git-changes
    M src/main.js
   A  src/utils.js
   ?? config/new.json
   ```
3. Extract all file paths, **deduplicate** (keep the latest status per file)
4. Map git status codes to actions: `A`/`??` → created, `M` → modified, `D` → deleted
5. **Clean up**: After reading, delete or clear the log file so the next session starts fresh

### Tier 2: Git direct diff (fallback)
If the auto-tracked log is missing or empty, and the project is a git repository:
1. Run `git status --short` to get working directory changes
2. Run `git diff --cached --name-only` to get staged changes
3. Merge both lists, deduplicate

### Tier 3: Git HEAD comparison (deep fallback)
If Tier 2 is inconclusive:
1. Run `git diff HEAD --name-only` to see all changes since the last commit
2. This catches changes that may have been partially staged or committed mid-session

### Tier 4: User confirmation (mandatory final step)
**Always** present the merged artifact list to the user for verification:
- "我检测到以下文件在本次会话中有变更，请确认是否准确："
- List each file with its detected action (created/modified/deleted)
- Ask: "有没有遗漏的文件？有没有误报（未参与本次对话的文件）？"
- Incorporate user feedback before generating the haness document

**Why this matters:** Past versions of haness relied on "AI mental bookkeeping" which frequently missed files, especially when sub-agents created files or when many files were edited across a long conversation. The auto-tracked log eliminates this failure mode.

## Content Strategy

Haness is intentionally minimal. Include only what a new session needs to continue.

### Required Sections

1. **Frontmatter** (YAML)
   - `haness_version`: "1.0"
   - `created_at`: ISO timestamp
   - `topic`: One-sentence summary of the conversation's theme
   - `artifacts`: List of artifact objects with `path`, `type` (code/doc/data/config), `description`

2. **Conversation Goal**
   - What problem were we solving? 1-3 sentences.

3. **Key Decisions**
   - Bullet list of decisions made during the conversation
   - Each decision: what was chosen and why

4. **TODO / Next Steps**
   - Checkbox list of what remains to be done
   - New session should pick from here

5. **Artifact Inventory**
   - Table: File | Action | Description
   - If no artifacts, explicitly state: "No artifacts produced in this conversation"

6. **New Session Prompt**
   - A self-contained prompt block that the user can copy-paste into a new session
   - Must include: what we're continuing, key context, and what to do first
   - End with: "Then wait for my instructions."

### What NOT to Include

- Do NOT embed full file contents (unlike handoff). Just list artifacts with paths.
- Do NOT include project architecture, directory trees, or unrelated files.
- Do NOT restate CLAUDE.md rules or project conventions.
- Do NOT include conversation history or message logs.

## Generation Workflow

### Phase 1: Summarize
1. Extract the conversation's core goal in 1-3 sentences
2. Identify key decisions made (design choices, tradeoffs, agreements)
3. Identify TODOs and next steps

### Phase 2: Discover Artifacts
1. **Read auto-tracked log**: Check `.claude/haness/session-artifacts.log` for hook-recorded changes
2. **Git verification**: Run `git status --short` and `git diff --cached --name-only` to cross-check
3. **Merge and deduplicate**: Combine results from all sources into a single artifact list
4. **User confirmation**: Present the list to the user and ask for verification/corrections
5. **Clean up**: Delete `.claude/haness/session-artifacts.log` after successful haness generation

### Phase 3: Assemble
1. Create `.claude/haness/` directory if missing
2. Generate filename: `<YYYYMMDD-HHMMSS>-<topic-slug>.md`
3. Fill the template from `references/haness-template.md`
4. Write the file

### Phase 4: Validate
1. Verify the New Session Prompt is self-contained
2. Confirm artifact paths are correct and exist
3. Ensure no session-specific abbreviations remain undefined

## Loading a Haness (New Session)

When a user wants to load a haness in a new session:

1. Read the haness file specified by the user (or ask which one)
2. Parse the frontmatter and artifact list
3. Read all artifact files to understand their current state
4. Present the user with:
   - Conversation goal recap
   - TODO list
   - Ask: "Which item should we tackle first?"

## Relationship with Other Skills

| Skill | Scope | Size | Use When |
|-------|-------|------|----------|
| `haness` | Single conversation | Light (~1KB-10KB) | Carry over one session's work |
| `handoff` | Entire project | Heavy (~10KB-500KB) | Transfer full project context |
| `transfer-context` | Session deltas | Medium | Continue same project in new session |

## Key Constraints

- Frame everything as information, not commands. Write "X was decided" not "Do X".
- End the "New Session Prompt" with an explicit "wait for instructions" line.
- Do NOT include sections for "Verbatim References" or "Completed Work" — claude-mem captures these automatically.
- Be concise. Cut redundancy. Every sentence should be information the next session cannot infer from reading artifacts alone.

## Additional Resources

- **`references/haness-template.md`** — The standard haness file format template
