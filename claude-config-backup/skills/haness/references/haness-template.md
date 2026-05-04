---
haness_version: "1.0"
created_at: "YYYY-MM-DDTHH:MM:SS"
topic: "One-sentence conversation theme"
artifacts:
  - path: "relative/path/to/file.py"
    type: "code"
    description: "What this file does and why it was created/modified"
  - path: "relative/path/to/doc.md"
    type: "doc"
    description: "What this document contains"
---

## Conversation Goal

1-3 sentences describing what problem this conversation was solving.

## Key Decisions

1. **Decision name**: What was chosen and why.
2. **Decision name**: What was chosen and why.

## TODO / Next Steps

- [ ] First remaining task
- [ ] Second remaining task
- [ ] Third remaining task

## Artifact Inventory

| File | Action | Description |
|------|--------|-------------|
| `path/to/file.py` | Created | Brief description |
| `path/to/file.py` | Modified | What changed |

> If no artifacts were produced, state explicitly:
> **No artifacts produced in this conversation.**

## New Session Prompt

```
You are continuing the following conversation: <topic>.

Key context:
- Context point 1
- Context point 2
- Context point 3

Artifacts to review:
- `path/to/file.py` — description
- `path/to/doc.md` — description

Please read the listed artifacts first, then continue with the TODO items above.

Then wait for my instructions.
```
