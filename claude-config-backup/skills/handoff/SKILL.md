---
name: handoff
description: This skill should be used when the user asks to "handoff project", "移交项目", "项目交接", "prepare for next session", "export project context", "项目快照", "完整移交", "生成移交文档", or when the user wants to transfer a complete project state to a new Claude Code session for seamless continuation. It creates a structured, self-contained project snapshot that enables the next AI to immediately understand the full project context and continue working without re-discovery.
---

# Project Handoff

Generate a complete, self-contained project snapshot for transferring full context to a new Claude Code session. Unlike `transfer-context` which compresses session-specific deltas for same-session continuation, this skill captures the entire project state so the next AI can start fresh and immediately continue without re-discovering architecture, dependencies, or work-in-progress.

## When to Use

Use this skill when:
- The current session is approaching context limits and the user wants to continue in a new session
- The user explicitly requests a project handoff or snapshot
- A complex project needs to be transferred to a new Claude instance with full context preserved
- The user says "移交", "交接", "handoff", "snapshot", "export context"

Do NOT use this skill for simple session summaries or when `transfer-context` is sufficient (i.e., when the project state is already well-documented and only session-specific changes need to be captured).

## File Output

Write the handoff document to a markdown file at `.claude/handoffs/<YYYYMMDD-HHMMSS>-<project-name>.md` (relative to the project root). Create the directory if it does not exist.

After writing the file, output ONLY this to the user (nothing else):

```
Project handoff written to: <absolute-path-to-file>

To continue in a new session, paste the "New Session Prompt" from that file.
```

Do NOT print the full handoff content to the conversation.

## Content Strategy

Use a hybrid approach to balance completeness with readability. Every piece of content should be information the next session cannot get from simply reading the code or CLAUDE.md.

### Embed Fully

For files < 200 lines or critical to understanding the project:
- Project configuration files (package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, etc.)
- Core module files that define architecture (entry points, main classes, API definitions)
- Small utility scripts and tools
- Currently failing test files
- The project's CLAUDE.md (if project-specific)

### Reference with Fragments

For files >= 200 lines:
- File path and one-sentence purpose
- Line ranges for key functions, classes, or critical logic blocks
- 20-50 line representative code blocks showing patterns and conventions
- Dependency relationships (what imports this, what this imports)

### List Structurally

For generated or auxiliary files:
- Build artifacts and output directories
- Dependency lock files (list direct dependencies, not full lock content)
- Large data files, asset directories
- Generated documentation

## Generation Workflow

### Phase 0: Read Project Conventions

Read the project's CLAUDE.md first. Do NOT restate anything already covered there (conventions, patterns, rules, preferences). The handoff document should only contain project state and session-specific information that supplements CLAUDE.md.

### Phase 1: Project Discovery

1. Identify the project root: current working directory or nearest parent containing CLAUDE.md, .git, or a package manifest
2. Determine project type by examining manifest files in this order:
   - package.json → JavaScript/TypeScript
   - pyproject.toml, requirements.txt, setup.py → Python
   - Cargo.toml → Rust
   - go.mod → Go
   - pom.xml, build.gradle → Java
   - Makefile, CMakeLists.txt → C/C++
   - Dockerfile, docker-compose.yml → Container-based
   - Fallback: infer from directory structure and file extensions
3. Capture git state:
   - Current branch name
   - Last 3-5 commit messages
   - Summary of uncommitted changes (files modified, added, deleted; not full diffs)
4. Generate project tree:
   - Max depth 3
   - Exclude: node_modules, .git, __pycache__, .venv, venv, target, build, dist, .claude
   - Mark directories vs files clearly

### Phase 2: Content Collection

5. Read all configuration and manifest files completely
6. Identify core source files:
   - Entry points (main, index, app, server, cli)
   - Files referenced in manifests as "main" or "bin"
   - Files with the most imports/references (use grep if needed)
7. For each core source file:
   - If < 200 lines: read complete content
   - If >= 200 lines: extract key fragments (top-level imports/exports, main class/function definitions, critical business logic, error handling patterns)
8. Check for open TODOs, FIXMEs, or known issues:
   - Search for "TODO", "FIXME", "HACK", "XXX" in source files
   - List each with file path and line number
9. Read recently modified files (from git status) that are relevant to current work

### Phase 3: State Synthesis

10. Summarize completed work:
    - Review git log for recent commits
    - List features/tasks that are fully implemented and tested
    - Only include work that is actually done, not attempted
11. Identify work-in-progress:
    - Files with uncommitted changes
    - Partially implemented features
    - Open branches (if relevant)
    - Describe exact file paths and line ranges where work is ongoing
12. Catalog known issues:
    - Failing tests (list test names and failure messages)
    - Build warnings or lint errors
    - Architectural debt or temporary workarounds
    - Performance bottlenecks mentioned in code or conversation
13. Capture working agreements observed during the session:
    - How the user prefers to interact (e.g., "review before committing", "prefer small PRs")
    - Quality gates or approval steps observed
    - Communication style preferences
14. Note traps: failed approaches, mistakes made, things the next agent will be tempted to repeat

### Phase 4: Document Assembly

15. Create `.claude/handoffs/` directory if it does not exist
16. Generate filename: `<YYYYMMDD-HHMMSS>-<project-name>.md`
    - Project name: directory name or name from manifest file
    - Use 24-hour format
17. Assemble the handoff document using the template in `references/handoff-template.md`
18. For embedded file content, use clearly demarcated code blocks with language tags and file paths as headers
19. Ensure all line references are accurate and verifiable

### Phase 5: Validation

20. Verify that the handoff document can be understood without reading source files
21. Confirm all critical paths and file references are correct
22. Check that the "New Session Prompt" is self-contained and actionable
23. Ensure no session-specific abbreviations or undefined terms remain
24. Be concise. Cut anything redundant, explanatory, or obvious. Every sentence should be information the next session cannot get from reading the code or CLAUDE.md.

## Key Constraints

- Frame everything in "Open Work" and "New Session Prompt" as information, not commands. Write "X is partially implemented in file Y" not "Continue implementing X".
- End the "New Session Prompt" with an explicit "wait for instructions" line.
- Do NOT include sections for "Verbatim References", "Important Context", or "Completed Work" — claude-mem captures these automatically from tool observations.
- Do NOT restate CLAUDE.md content. Reference it and supplement with state-specific information only.
- The handoff is for a fresh session. Assume the next AI has NOT read any files in this project.

## Additional Resources

### Reference Files

For the complete handoff document template with all sections and examples:
- **`references/handoff-template.md`** - Full template with section descriptions and formatting guidance
