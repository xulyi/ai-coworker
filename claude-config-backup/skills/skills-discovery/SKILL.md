---
name: skills-discovery
description: Search for and install Agent Skills that give you specialized capabilities. Before starting work, ask might a skill exist that handles this better than my base knowledge? If the task involves specific technologies, frameworks, file formats, or expert domains. Search proactively, even if the user doesn't mention skills. Skills encode best practices, tools, and techniques you wouldn't otherwise have. Also use when users explicitly ask to find, install, or manage skills.
metadata:
  version: "1.1.0"
  author: "Claude"
  language: "en"
  domain: "skill-management"
  trigger_keywords:
    - find skills
    - search skills
    - install skill
    - skill registry
    - discover skills
    - list skills
    - uninstall skill
    - manage skills
    - skill marketplace
---

# Skills Discovery

You can extend your capabilities by discovering and installing Agent Skills from the claude-plugins.dev registry. Skills provide specialized knowledge, tools, and techniques for specific technologies, frameworks, and domains.

---

## Trigger Conditions

- User asks to find, search, or discover skills
- User wants to install or manage skills
- Before starting non-trivial work (proactive search)
- When existing skills don't cover the task

---

## When to search for skills

First, check if an installed skill matches the task. If not, search the registry—specialized skills may exist that you haven't installed yet.

Before starting any non-trivial task, ask yourself:

1. Do I have a skill for this? → Use it
2. Might one exist that I don't have? → Search the registry

Search proactively when:

- The task involves specific technologies, frameworks, or file formats
- You're about to do something where best practices matter (testing, deployment, APIs, documentation)
- The domain is specialized (PDF processing, data pipelines, ML workflows)
- You notice yourself about to give generic advice where expert patterns would help

Also search when users explicitly ask to find, install, or manage skills.

---

## Discovery workflow

Use the registry API for search (the CLI's search command is interactive and not suitable for programmatic use):

```bash
curl "https://claude-plugins.dev/api/skills?q=QUERY&limit=20&offset=0"
```

**Parameters:**

- `q`: Search query (e.g., "frontend", "python", "pdf")
- `limit`: Results per page (max 100)
- `offset`: Pagination offset

**Response structure:**

```json
{
  "skills": [
    {
      "id": "...",
      "name": "skill-name",
      "namespace": "@owner/repo/skill-name",
      "sourceUrl": "https://github.com/...",
      "description": "...",
      "author": "...",
      "installs": 123,
      "stars": 45
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

## Search strategies

The registry indexes skill names, descriptions, and tags. Construct queries that match how skill authors describe their work.

**Query construction:**

- Use 1-3 specific terms (too broad = noise, too narrow = misses)
- Prefer widely-used terminology over project-specific jargon
- Technology + task often outperforms either alone
- If results are poor, broaden or try synonyms

---

## Installation

Determine which client the user is working in before installing. If unclear, ask.

**Supported clients:**

- `claude-code` — Claude Code CLI
- `codex` — Codex
- `cursor` — Cursor editor
- `amp` - amp CLI
- `opencode` - OpenCode CLI
- `goose` - Goose CLI
- `github` — VSCode/ github
- `vscode` — VS Code
- `letta` — Letta CLI
- `gemini` - Gemini CLI
- `windsurf` - Windsurf editor
- `antigravity` - Antigravity
- `trae` - Trae
- `qoder` - Qoder
- `codebuddy` - CodeBuddy

**Client selection:**

```bash
npx skills-installer install @owner/repo/skill-name --client claude-code  # default
npx skills-installer install @owner/repo/skill-name --client cursor
npx skills-installer install @owner/repo/skill-name --client vscode
```

**Scope selection:**

```bash
npx skills-installer install @owner/repo/skill-name  # global (default)
npx skills-installer install @owner/repo/skill-name --local  # project-specific
```

**Combined:**

```bash
npx skills-installer install @owner/repo/skill-name --client cursor --local
```

**Defaults:**

- Client: `claude-code`
- Scope: global

---

## Management

```bash
# List installed skills
npx skills-installer list

# Uninstall a skill
npx skills-installer uninstall @owner/repo/skill-name
```

---

## Presenting results to users

When you find relevant skills:

1. Show 3-5 most relevant results maximum
2. Include: name, namespace, description, stars, installs
3. Explain how each skill helps with their _specific_ task
4. Prioritize those with high installs
5. Always ask for confirmation before installing
6. Offer to help directly if no good skill exists or user declines

---

## ⚠️ Gotchas (Common Pitfalls)

### Pitfall 1: Installing Without User Consent
- **Trap**: Automatically installing skills without asking the user
- **Consequence**: User may not want or trust the skill; violates user autonomy
- **Solution**: Always ask for explicit confirmation before installing any skill

### Pitfall 2: Wrong Client Detection
- **Trap**: Assuming the user's client (e.g., installing for claude-code when they use Cursor)
- **Consequence**: Skill installs in wrong location, doesn't activate
- **Solution**: Always confirm client if unclear; ask "Are you using Claude Code, Cursor, or another client?"

### Pitfall 3: Overwhelming Results
- **Trap**: Showing 10+ skills without curation
- **Consequence**: User can't decide, analysis paralysis
- **Solution**: Filter to 3-5 most relevant; explain why each is a good match

### Pitfall 4: Ignoring Already Installed Skills
- **Trap**: Searching registry without checking currently installed skills first
- **Consequence**: Suggesting installation of skills the user already has
- **Solution**: Always check installed skills list first with `npx skills-installer list`

### Pitfall 5: Installing Untrusted Skills
- **Trap**: Installing skills with few installs, no stars, unknown authors
- **Consequence**: Potential security risk or poor quality
- **Solution**: Prioritize skills with high installs/stars from reputable sources; warn about low-trust skills

### Pitfall 6: Not Offering Direct Help Alternative
- **Trap**: Pushing skill installation as the only option
- **Consequence**: User feels forced; may have good reasons to avoid skills
- **Solution**: Always offer: "Would you like me to install this skill, or help you directly without it?"

---

## Examples

**Example: Proactive suggestion**

User: "I need to create a Django REST API"

```bash
curl "https://claude-plugins.dev/api/skills?q=django&limit=10"
```

Present suggestion:

```
I found some skills that could help:

1. django-rest-framework-expert (@anthropics/claude-code/django-rest-framework-expert)
   Description: Django REST API development with best practices
   ⭐ 234 stars • 1,567 installs

Would you like me to install this, or help you directly without installing a skill?
```

**Example: Explicit search request**

User: "find skills for Python"

```bash
curl "https://claude-plugins.dev/api/skills?q=python&limit=10"
```

Present results and ask which to install.

---

## API reference

| Endpoint                                 | Description       |
| ---------------------------------------- | ----------------- |
| `GET /api/skills/search?q=QUERY`         | Search skills     |
| `GET /api/skills/@owner/repo/skill-name` | Get skill details |

**Web registry:** https://claude-plugins.dev/skills

---

## Troubleshooting

**No results found:**

- Try broader search terms
- Browse web registry: https://claude-plugins.dev/skills

**Installation fails:**

- Verify namespace format: `@owner/repo/skill-name`
- Check skill exists in registry
- Verify directory permissions

**Skill not activating:**

- User may need to restart their client
- Verify correct installation directory
- Confirm SKILL.md exists in installation path

---

## Fallback Strategies

### When registry API is unavailable
- Suggest browsing web registry manually
- Offer to help directly without skill installation

### When no relevant skills exist
- Acknowledge the gap
- Offer to help directly
- Suggest user could create a skill for this use case

### When user declines skill installation
- Respect their decision
- Provide best-effort help using base capabilities
- Don't repeatedly push skill installation

---

## Testing Recommendations

Suggested eval scenarios (create evals/evals.json):

```json
{
  "evals": [
    {
      "name": "proactive-suggestion",
      "prompt": "User says: 'I need to analyze some PDF files'",
      "expected": "Proactively search for PDF-related skills and suggest installation"
    },
    {
      "name": "explicit-search",
      "prompt": "User says: 'find skills for data visualization'",
      "expected": "Search registry and present 3-5 relevant skills with details"
    },
    {
      "name": "ask-before-install",
      "prompt": "User says: 'Install the best Python skill'",
      "expected": "Present options and ask for confirmation, don't auto-install"
    }
  ]
}
```
