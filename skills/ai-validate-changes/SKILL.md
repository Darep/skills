---
name: ai-validate-changes
description: >
  Validate current repository changes with an AI-assisted workflow inspired by
  kunchenguid/no-mistakes, with pinned source notes in
  references/no-mistakes-validation.md: infer intent, review diffs, run focused
  tests/evidence checks, check docs and lint risk, call one read-only external
  AI CLI for an independent pass when available, apply only safe fixes, and
  report structured findings. Use when the user asks to validate, AI-review,
  no-mistakes-style check, multi-agent review, test evidence, docs/lint
  validation, or safe-fix current code changes without using a git proxy, push
  gate, PR automation, or CI monitor.
---

# AI Validate Changes

Validate the current diff, not the repository in the abstract. Borrow only the
AI-validation ideas from `kunchenguid/no-mistakes` that are documented in
[no-mistakes-validation.md](references/no-mistakes-validation.md); ignore git
proxy, push gate, PR automation, and CI monitoring.

## Scope

1. Find the repository root and capture `git status --short --branch`.
2. Prefer uncommitted changes. If there are none, validate the current branch
   against its upstream or the default base branch. If there is no diff, report
   that there is nothing to validate and stop.
3. Treat staged, unstaged, and untracked files as in scope unless the user
   narrows the request.
4. Record the exact diff basis in the final report so repeat runs validate the
   same surface unless the worktree changed.

## Workflow

1. Infer intent from the user request, branch name, changed files, and diff.
   Ask only when product intent or acceptance criteria are too ambiguous to
   review safely.
2. Do a primary review pass over the scoped diff. Look for correctness,
   regressions, missing tests, docs drift, lint/type risks, security footguns,
   and behavior that contradicts the inferred intent.
3. Run focused local evidence checks. Prefer existing project commands from
   package scripts, Makefiles, task files, CI config, or repo docs. Keep checks
   proportional to the diff.
4. Call one read-only external AI reviewer when available. Prefer `claude`,
   then `opencode`, then `codex review`. Use the `run-ai-clis` skill if exact
   local CLI syntax is needed.
5. Merge duplicate findings from the primary and external passes by stable
   `file:line:category` or by finding IDs. A repeat run should update the same
   finding rather than create another copy.
6. Apply only safe fixes. After each fix pass, rerun the smallest check that
   proves or disproves the fix.
7. Stop when safe fixes are exhausted, tests/evidence are clean enough for the
   stated scope, or a finding needs user judgment.

## External AI Pass

Use external agents only for review, not mutation.

- Snapshot `git status --short` before and after the external command. If it
  changes, stop and report the unexpected mutation.
- Do not pass write-enabled flags such as `--sandbox workspace-write`, and do
  not ask external agents to edit files.
- Prefer passing a captured diff and relevant command output to the external
  agent. If a CLI cannot be constrained to read-only behavior, skip it.
- Give the external agent the same scope and ask for structured findings with
  severity, file, line, description, and suggested action.
- If no external CLI is installed or it fails quickly, continue with the
  primary pass and note the absence in the report.

## Finding Actions

Classify every finding with one action:

- `auto-fix`: deterministic, local, and directly supported by the diff or
  failing evidence.
- `ask-user`: requires product judgment, API semantics, broad refactoring, or
  acceptance criteria not present in the repo.
- `no-op`: valid observation that does not require a code change for this
  validation scope.

Safe `auto-fix` examples include syntax/type/import errors, local lint or
format violations, clear deterministic test failures, missing error handling
introduced by the diff, and direct docs mismatch caused by the diff.

Never auto-fix product ambiguity, public API semantics, broad refactors,
intentional deletion/restoration, test expectation changes that alter behavior,
or anything classified as `ask-user`.

## Report Format

End with a concise report. Use this shape when more than one finding exists:

```yaml
scope:
  basis:
  files:
intent:
external_agent:
risk_level:
risk_rationale:
findings:
  - id:
    source:
    category:
    severity:
    action:
    file:
    line:
    description:
    status:
tested:
  - command_or_check:
testing_summary:
artifacts:
  - kind:
    label:
    path:
    url:
    content:
fixes:
  - finding_ids:
    summary:
    files:
remaining_decisions:
  - finding_id:
    question:
skipped:
  - check:
    reason:
```

For small validations, prose is fine, but still include scope, external-agent
status, risk, fixes applied, tested checks, testing summary, artifacts, and
remaining decisions.

Do not add separate `evidence` or `verification` fields to the report. Put proof
of behavior in `tested`, `testing_summary`, and `artifacts`; put rationale for a
finding in its `description` and `status`.

Do not create persistent report files unless the user asks. If a report file is
requested, overwrite the same named file on repeat runs instead of appending.
