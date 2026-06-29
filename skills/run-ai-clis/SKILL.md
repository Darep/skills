---
name: run-ai-clis
description: >
  Use when the user asks an agent to call local AI coding CLIs from the
  terminal, including `codex`, `opencode`, or Claude Code's `claude` CLI.
  Contains exact local command templates, model IDs, effort flags, and
  cross-tool execution rules so the agent can run the requested CLI directly
  instead of rediscovering syntax.
---

# Run AI CLIs

Use these mappings directly. Do not spend time rediscovering flags unless the
user asks for a different model or the command fails.

Prefer `claude` if available, over opencode, for Claude models such as Opus.
Prefer `codex exec` when calling Codex from another agent such as Claude Code.

If user mentions "ultracode" it means `xhigh` effort and asking Opus to use
dynamic workflows.


## Shorthand Map

- Codex CLI
  - interactive -> `codex`
  - non-interactive -> `codex exec`
  - non-interactive review -> `codex review` or `codex exec review`
  - set repo root -> `--cd <dir>`
  - allow edits -> `--sandbox workspace-write`
  - machine-readable stream -> `--json`
  - save final answer -> `--output-last-message <file>`
- OpenCode
  - `kimi k2.6` -> `opencode/kimi-k2.6`
  - `opus 4.8` -> `opencode/claude-opus-4-8`
  - `opus effort` -> `--variant [xhigh|max]`
  - Always use thinking with opus -> `--thinking`
- Claude Code CLI
  - `opus 4.8` -> `claude-opus-4-8`
  - plain `opus` can stay `opus` if the user did not pin a version
  - if user mentions `ultracode`, preserve the literal word
    `ultracode` in the prompt when practical; Claude uses it as a
    dynamic-workflow trigger keyword

## Command Templates

### Codex CLI

Non-interactive:

```bash
codex exec "<prompt>"
```

Non-interactive from a specific repo:

```bash
codex exec --cd <repo-dir> "<prompt>"
```

Allow Codex to edit files in the workspace:

```bash
codex exec --sandbox workspace-write --cd <repo-dir> "<prompt>"
```

Pass command output or logs as context:

```bash
<command> 2>&1 | codex exec "analyze this output and recommend the smallest fix"
```

Machine-readable event stream:

```bash
codex exec --json "<prompt>"
```

Write the final message to a file:

```bash
codex exec --output-last-message codex-result.md "<prompt>"
```

Review uncommitted changes:

```bash
codex review --uncommitted "<review instructions>"
```

Review against a base branch:

```bash
codex review --base main "<review instructions>"
```

Interactive:

```bash
codex
```

### OpenCode

Non-interactive:

```bash
opencode run -m opencode/kimi-k2.6 "<prompt>"
```

Non-interactive with "thinking xhigh effort":

```bash
opencode run -m opencode/claude-opus-4-8 --variant xhigh --thinking "<prompt>"
```


Interactive:

```bash
opencode -m opencode/kimi-k2.6
```


If the user explicitly asks for OpenCode reasoning effort, the flag is:

```bash
--variant <level>
```

If the user explicitly asks to see reasoning blocks, add:

```bash
--thinking
```

### Claude Code CLI

Non-interactive:

```bash
claude -p --model claude-opus-4-8 --effort xhigh "<prompt>"
```

JSON output:

```bash
claude -p --output-format json --model claude-opus-4-8 --effort xhigh "<prompt>"
```

Interactive:

```bash
claude --model claude-opus-4-8 --effort xhigh
```

## Execution Rules

- If the user names multiple CLIs, run them as separate commands and label outputs
  clearly.
- Prefer non-interactive commands (`codex exec`, `opencode run`, `claude -p`)
  unless the user explicitly wants an interactive session.
- When calling Codex from Claude Code, use `codex exec`; do not launch the
  interactive TUI unless the user explicitly asks for it.
- Keep the user prompt materially the same across tools unless the user
  asked for different roles.
- For Codex edits, add `--sandbox workspace-write`; otherwise leave Codex in
  its default read-only mode for analysis and review.
- Use `codex review` for review-only tasks when the user asks Codex to review
  repository changes.
- Do not guess OpenCode `--variant` values unless the user explicitly asked for
  extra reasoning.
- If the user explicitly asks for Claude `max` effort, use `--effort max`
  instead of `xhigh`.
- Do not use Codex `--dangerously-bypass-approvals-and-sandbox` unless the user
  explicitly requests it and the run is inside an externally controlled sandbox.
