# Andrej Karpathy Skills

## What

Behavioral guidelines to reduce common LLM coding mistakes. Derived from Andrej Karpathy's observations on LLM coding pitfalls, encoded as a single `CLAUDE.md` file that improves Claude Code (and compatible agents) behavior.

42.8K+ GitHub stars. The entire project is one CLAUDE.md file.

## Where

- Skill path: `~/.openclaw/workspace/skills/andrej-karpathy-skills/`
- Core file: `CLAUDE.md` (the behavioral guidelines)
- Examples: `EXAMPLES.md` (practical demonstrations)
- Source of truth: `https://github.com/forrestchang/andrej-karpathy-skills`

## The Four Principles

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so.
- If something is unclear, stop and ask.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Remove only what YOUR changes made unused.

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan with verification at each step.

## How to Use

### Load into any coding session

```bash
cat ~/.openclaw/workspace/skills/andrej-karpathy-skills/CLAUDE.md
```

### Copy to a project root (for Claude Code)

```bash
cp ~/.openclaw/workspace/skills/andrej-karpathy-skills/CLAUDE.md ./CLAUDE.md
```

When `claw` or `claude code` runs in a directory containing `CLAUDE.md`, it automatically loads these behavioral guidelines.

### Quick reference (single command)

```bash
karpathy-skills        # displays the four principles
```

## Why It Works

These guidelines are working if:
- Fewer unnecessary changes in diffs
- Fewer rewrites due to overcomplication
- Clarifying questions come before implementation rather than after mistakes

## When to Use

- Before any coding task where you want the agent to be cautious, precise, and minimal
- When reviewing agent-generated code that feels overcomplicated
- When you want the agent to ask clarifying questions before jumping into implementation
- When editing existing codebases where surgical precision matters

## Full Content

See `CLAUDE.md` for the complete behavioral specification.
See `EXAMPLES.md` for practical demonstrations.
