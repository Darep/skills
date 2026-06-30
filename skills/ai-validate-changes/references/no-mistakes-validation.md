# no-mistakes Validation Notes

This skill borrows validation patterns from `kunchenguid/no-mistakes` at commit
`2a73434e762de372e3f13712e0433b773ceec6c3` (`v1.32.2`). It does not reuse the
project's git proxy, push gate, daemon, PR automation, or CI watcher.

## Source Links

- README validation overview:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/README.md#L33-L61>
- Pipeline step order:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/steps/common.go#L124-L140>
- Approval and fix loop:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/executor.go#L313-L450>
- Config trust behavior:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/config/config.go#L587-L622>
- Agent steering caveat:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/agent/steering.go#L10-L24>
- Test and evidence behavior:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/steps/test.go#L85-L210>
- Review step:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/steps/review.go>
- Lint step:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/steps/lint.go>
- Documentation step:
  <https://github.com/kunchenguid/no-mistakes/blob/2a73434e762de372e3f13712e0433b773ceec6c3/internal/pipeline/steps/document.go>

## Borrowed Ideas

- Validate through a fixed sequence: infer intent, review, test/evidence,
  documentation, lint, and a bounded fix loop.
- Represent agent review output as structured findings with severity, file,
  line, description, an action such as `auto-fix`, `ask-user`, or `no-op`, and
  a review-level `risk_level` plus `risk_rationale`.
- Allow automatic fixes only for findings that are clearly local and marked
  safe to fix. User-judgment findings block instead of being silently changed.
- Treat tests as evidence. A configured test command is valuable, but an agent
  may also inspect the diff, intent, artifacts, and command output to determine
  whether the change is sufficiently validated. Preserve that in `tested`,
  `testing_summary`, and `artifacts` instead of a separate verification field.
- Treat agent steering as advisory. Prompting an agent to stay in a scope is
  not a hard sandbox, so this skill keeps external AI CLIs read-only and lets
  the current Codex session apply any approved safe fixes.
- Avoid trusting configuration from the code under validation when it would
  grant broad execution authority. Prefer existing local project commands and
  show what was run.

## Deliberately Omitted

- Local git remote/proxy installation.
- Push interception or branch protection.
- PR creation, PR updates, and CI monitoring.
- Daemons, background services, persistent state, or hooks.
- Generated scripts for this repo. The skill is procedural so repeat runs
  update the same validation surface instead of creating new support files.
