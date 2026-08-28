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
If the `claude` CLI is unavailable, OpenCode Zen can run Claude models; OpenCode
Go cannot. Never switch between Zen and Go silently.
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
  - Zen provider prefix -> `opencode/`
  - Go provider prefix -> `opencode-go/`
  - `kimi k3` on Zen -> `opencode/kimi-k3`
  - `kimi k3` on Go -> `opencode-go/kimi-k3`
  - `opus 5` on Zen -> `opencode/claude-opus-5`
  - `glm 5.3 fast` or `glm 5.3 flash` on Go -> `opencode-go/glm-5.3-flash`
  - OpenCode Go has no Opus/Claude model
  - reasoning effort -> `--variant <level>`; valid levels are model-specific
  - show reasoning blocks -> `--thinking`
- Claude Code CLI
  - `opus 5` -> `claude-opus-5`
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

When the user does not name a model, choose the best fit for the task from
`opencode/kimi-k3`, `opencode-go/glm-5.3-flash`, and
`opencode/gemini-3.6-flash`. Treat them as peer candidates rather than using a
fixed default. Consider the task, expected speed and depth, and model
availability. Honor an explicit user choice.

Non-interactive with the chosen model:

```bash
opencode run -m <chosen-model> "<prompt>"
```

Non-interactive with a selected provider and model:

```bash
opencode run -m opencode-go/kimi-k3 "<prompt>"
opencode run -m opencode/kimi-k3 "<prompt>"
```

Interactive with the chosen model:

```bash
opencode -m <chosen-model>
```

If the user explicitly asks for OpenCode reasoning effort, the flag is:

```bash
--variant <level>
```

If the user explicitly asks to see reasoning blocks, add:

```bash
--thinking
```

OpenCode model names are `provider/model`: `opencode/...` uses Zen and
`opencode-go/...` uses Go. If the user names one, use it. If they do not name a
provider or model, omit `-m` rather than guessing which subscription is current.
If a requested model fails or appears stale, discover live IDs and variants
with:

```bash
opencode models opencode --verbose
opencode models opencode-go --verbose
```

Do not rediscover models on every run; use this only after a model-related
failure or when the user requests a model not mapped above.

### Claude Code CLI

Non-interactive:

```bash
claude -p --model claude-opus-5 --effort xhigh "<prompt>"
```

JSON output:

```bash
claude -p --output-format json --model claude-opus-5 --effort xhigh "<prompt>"
```

Interactive:

```bash
claude --model claude-opus-5 --effort xhigh
```

## Execution Rules

- If the user names multiple CLIs, run them as separate commands and label outputs
  clearly.
- Prefer non-interactive commands (`codex exec`, `opencode run`, `claude -p`)
  unless the user explicitly wants an interactive session.
- Treat OpenCode Go and OpenCode Zen as separate providers. Honor the provider
  the user names; otherwise omit `-m` and preserve OpenCode's active default.
- Do not fall back between `opencode/...` and `opencode-go/...` without the
  user's approval because that changes which subscription pays.
- If the `claude` CLI is unavailable, use `opencode/claude-*` only when Zen is
  selected. Go currently has no Claude models.
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
