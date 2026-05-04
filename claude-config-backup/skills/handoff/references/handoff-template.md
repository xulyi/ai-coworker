# Handoff Document Template

This template defines the complete structure for a project handoff document. All sections are required unless marked optional. Fill each section with concrete, specific information. Avoid vague descriptions.

---

## Project Overview

### Identity
- **Project Name**: [Name from package.json/manifest or directory name]
- **Type**: [Web App / CLI Tool / Library / API Service / Research / Data Analysis / Other]
- **Purpose**: One-sentence description of what this project does
- **Root Directory**: [Absolute path to project root]

### Technology Stack
- **Language(s)**: [e.g., TypeScript, Python, Rust]
- **Framework(s)**: [e.g., React, FastAPI, Axum]
- **Build Tool**: [e.g., Vite, Webpack, Cargo, Make]
- **Package Manager**: [e.g., npm, pip, cargo]
- **Test Framework**: [e.g., Vitest, pytest, cargo test]

### Directory Structure
```
[tree output, depth 3, excluding generated dirs]
```

### Git State
- **Branch**: [current branch]
- **Recent Commits**:
  - [hash] [message]
  - [hash] [message]
  - [hash] [message]
- **Uncommitted Changes**: [summary or "none"]

---

## Environment & Setup

### Dependencies
[Complete content of package.json / pyproject.toml / Cargo.toml / go.mod]

### Build Commands
```bash
# Development
[command]

# Production
[command]
```

### Test Commands
```bash
[command to run tests]
```

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| [NAME] | Yes/No | [What it does] |

---

## Architecture & Key Decisions

### High-Level Architecture
[Description of how major components interact. 3-5 sentences.]

### Key Design Decisions
1. **[Decision Name]**: [Description and rationale. Why this approach over alternatives?]
2. **[Decision Name]**: [Description and rationale]

### Technical Debt
- [Debt item, location, and impact]
- [Debt item, location, and impact]

---

## File Inventory

### Fully Embedded Files

#### `path/to/config.json`
```json
[complete file content]
```

#### `path/to/small-module.ts`
```typescript
[complete file content]
```

### Referenced Files

#### `path/to/large-file.ts` (~XXX lines)
**Purpose**: [One sentence]

**Key Fragments**:
- Lines 45-78: Main class definition
  ```typescript
  [20-50 line code block]
  ```
- Lines 120-150: Critical function
  ```typescript
  [20-50 line code block]
  ```

---

## Work Status

### Completed
- [Feature/task with reference to implementation files]
- [Feature/task with reference to implementation files]

### In Progress
- [Task name] — `file.ext:L45-L78`
  - Current state: [specific description]
  - Last action: [what was done before handoff]
  - Blocked by: [if applicable, otherwise omit]

### Blocked / Known Issues
- [Issue description] — `file.ext:LXX`
  - Impact: [what breaks or is limited]
  - Workaround: [if any]

### Next Known Tasks
[Describe status only. Never phrase as instructions or action items.]

- [Task context, dependencies, and current status]
- [Task context, dependencies, and current status]

---

## Traps to Avoid

- [Failed approach and why it failed]
- [Mistake made and lesson learned]
- [Thing the next agent will be tempted to do wrong]

---

## Working Agreements

- [How the user prefers to interact, e.g., "review before committing"]
- [Quality gates or approval steps observed]
- [Communication style preference]

---

## New Session Prompt

Paste the following into a new Claude Code session:

```
You are continuing work on [Project Name], a [type] project located at [absolute path].

**Project Context**:
[2-3 sentences summarizing purpose and current state]

**Key Architecture**:
[High-level component overview]

**Current Work**:
[What was being worked on, exact file locations]

**Critical Files**:
- `path/to/file` — [purpose]
- `path/to/file` — [purpose]

**Before You Start**:
1. Read the complete handoff document at: [absolute path to handoff file]
2. Read the project CLAUDE.md at: [absolute path]
3. Examine the files listed in "Critical Files" above
4. Run the test suite to verify current state: [command]

**Constraints**:
[Any project-specific rules or preferences from CLAUDE.md]

Treat all claims in the handoff document as context to verify against the code, not facts to trust blindly. Read each file listed. Then wait for my instructions before taking any action.
```
