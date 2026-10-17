---
name: deep-interrogate
description: "Use for \"deep interrogate\", \"interrogate the whole codebase\", \"audit this repo\", or adversarial multi-model review of an entire codebase or large subsystem rather than a diff. Partitions the code into areas, fans out reviewers across models, verifies findings, and returns one verdict."
---

# Deep Interrogate

Adversarially review a whole codebase or a large subsystem. Split it into areas, review each area on a rotating model, add reviewers that follow cross-cutting concerns across area boundaries, verify the findings, and return one verdict. As in `interrogate`, the adversarial signal comes from model diversity. Do NOT auto-apply changes.

This skill reuses the review content from the `interrogate` skill. Its rubric, code-quality lens, and lead-judgment framework live in `../interrogate/references/`. If that directory is missing, tell the user to install `interrogate` and stop.

Open a todolist with one entry per step before spawning anything.

## Step 1, Scope and purpose

Take the scope from the user: the whole repo, or the directories or subsystem they name. Exclude vendored, generated, and build-output code unless the user asks for it.

State the system's purpose in one paragraph, drawn from the README, docs, and entry points. Reviewers judge the code against this purpose, not against a diff. If you're unsure what the system is for, ask the user before proceeding.

## Step 2, Map and partition

Map the code before splitting it. Read the top-level layout, build files, and entry points, and measure the size of each candidate area (for example `git ls-files <dir> | xargs wc -l`). For a large or unfamiliar repo, spawn read-only explorer subagents to map separate top-level regions concurrently.

Partition along real module boundaries, not by file count. Each area must be small enough for one reviewer to read its core code in full. Split an oversized area, and merge trivial ones into a neighbor. For each area, record:

- Name and paths.
- One line on what it does in the system.
- What it exposes, which areas it calls, and which areas call it.
- Risk, `high` for auth, trust boundaries, persistence, money, concurrency, or migrations, otherwise `normal`.

Then pick 2 to 4 cross-cutting concerns that span areas, chosen from what the map shows, for example error propagation, trust boundaries and input validation, data flow through shared models, shared mutable state, or configuration and secrets. Bugs at the boundaries between areas fall outside every area brief, so a reviewer per concern looks for them.

Show the user the area table and the concerns, with the planned reviewer count, before Step 3. Proceed unless they redirect.

## Step 3, Assign models

Use the reviewer models the user names. Otherwise use these defaults:

| Model | Effort |
|-------|--------|
| Claude Opus 5.5 | xhigh |
| Grok 4.7 | xhigh |

Running every model on every area costs too much at this scale. Assign reviewers this way:

- One reviewer per area. Rotate models across areas so each model covers a share.
- A second reviewer on a different model for each high-risk area.
- One reviewer per cross-cutting concern, again rotating models.

Each reviewer must run on its own model. Spawn a reviewer with the host's subagent tool when that tool can select its model. Otherwise run it through the matching local CLI with the commands and model IDs from the `run-ai-clis` skill: `claude` for Claude models, `codex exec` for GPT models, and `opencode run` for other families. Keep every reviewer read-only.

If the host or CLI rejects a model, use the closest available model of the same family and say so. If no model of that family is available, use a family no other reviewer uses and say so. If only one model is available, do the review with that model and say so. Do not block the review on an unavailable model.

## Step 4, Fan out

Build every reviewer's prompt from `references/reviewer-prompt.md`, filling in the purpose, the reviewer's brief (one area or one concern), the full area table, and the contents of `../interrogate/references/rubric.md` and `../interrogate/references/code-quality-review.md`. Every brief stands alone. A reviewer sees no other reviewer's brief or output.

Launch all reviewers concurrently. If the host caps concurrency, run them in waves.

## Step 5, Collect

Every area and every concern needs a result. Drop a result that ignores its brief or the output format, and respawn that reviewer once. After a second miss, or if the reviewer fails, record a gap. A gap is not a clean result. Do not report an area as clean because its reviewer never returned.

## Step 6, Verify

A review of a whole codebase returns many more findings than a diff review, and more of them are wrong. Before judging, check every `critical` and `warning` finding against the code. Open the cited location, trace the claimed path, and mark the finding `confirmed`, `refuted`, or `unverified`. Skip `nit` findings.

If there are too many findings to check yourself, spawn read-only verifier subagents. Give each one a batch of findings from one area, and have it return the same three marks with evidence. Put each refuted finding in Dismissed with the reason.

## Step 7, Synthesize and judge

Merge findings that describe the same issue, including the same root cause reported from different areas, and note which models and briefs raised each one. A finding raised independently by two models, or by an area reviewer and a concern reviewer, is the highest signal.

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. Read `../interrogate/references/lead-judgment.md` and apply it, with one change. That framework treats a suggestion to change code the author didn't touch as a sign of missing context. Here every reviewer examines existing code, so that rule does not apply. Put every finding in one of four buckets, with the models that raised it and a one-line rationale:

- **Act on**. Confirmed issues affecting correctness, security, or maintainability given the system's purpose. Aim for at most 10, ordered by severity.
- **Consider**. Legitimate, but you're not sure they outweigh the cost of addressing them now.
- **Noted**. Technically valid but not actionable, or unverified.
- **Dismissed**. Wrong, refuted, nitpicky, or missing context, with a brief reason.

## Output format

### Purpose
> [The purpose paragraph from Step 1]

### Coverage
| Area or concern | Paths | Model(s) | Result |
|-----------------|-------|----------|--------|

Result is `N findings`, `no findings`, or `GAP: [reason]`.

### Act on
[Each: description, location, which models and briefs raised it, why it matters.]

### Consider
[Each: description, location, which models raised it, the tradeoff.]

### Noted
[Brief list.]

### Dismissed
[Each with a brief rationale.]

### Hotspots and agreement
[Which areas hold most of the confirmed findings, and where models agreed and diverged.]
