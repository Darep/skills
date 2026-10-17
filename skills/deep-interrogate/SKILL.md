---
name: deep-interrogate
description: "Use for \"deep interrogate\", \"interrogate the whole codebase\", or adversarial multi-model review of an entire codebase or large subsystem rather than a diff. Partitions the code into areas, fans out reviewers across models, verifies findings, and returns one verdict."
---

# Deep Interrogate

Adversarially review a whole codebase or a large subsystem. Split it into areas, review each area on a rotating model, add reviewers that follow cross-cutting concerns across area boundaries, verify the findings, and return one verdict. As in `interrogate`, the adversarial signal comes from model diversity. Do NOT auto-apply changes.

This skill uses four things from the `interrogate` skill: its default reviewer models, its rubric, its code-quality lens, and its lead-judgment framework. Look for that skill in `../interrogate/`, relative to the directory that contains this SKILL.md, not the repository under review. If it is not there, look for the installed `interrogate` skill by name. If you cannot find it, tell the user to install `interrogate` and stop.

## Step 1, Scope and purpose

Take the scope from the user: the whole repo, or the directories or subsystem they name. Exclude vendored, generated, and build-output code unless the user asks for it.

State the system's purpose in one paragraph, drawn from the README, docs, and entry points. Reviewers judge the code against this purpose, not against a diff. If you're unsure what the system is for, ask the user before proceeding.

## Step 2, Map and partition

Map the code before splitting it. Read the top-level layout, build files, and entry points, and count the lines in each candidate area, leaving out the Step 1 exclusions. For a large or unfamiliar repo, spawn read-only explorer subagents to map separate top-level regions concurrently. Have each return the directories it found, what each one does, and how they call each other.

Partition along real module boundaries, not by file count. Each area must be small enough for one reviewer to read its core files in full. Split an oversized area, and merge trivial ones into a neighbor. Every in-scope directory belongs to exactly one area or is listed as excluded with a reason. For each area, record:

- Name and paths.
- Core files, the ones the reviewer must read in full.
- One line on what it does in the system.
- What it exposes, which areas it calls, and which areas call it.
- Risk. Mark an area `high` only if it enforces a trust decision, such as authentication, authorization, or input validation at an entry point, or if it moves money or irreversibly changes stored data. Code that only touches a database or a lock is `normal`. When unsure, use `normal`.

Then pick 2 to 4 cross-cutting concerns that span areas, chosen from what the map shows, for example error propagation, trust boundaries and input validation, data flow through shared models, shared mutable state, or configuration and secrets. Bugs at the boundaries between areas fall outside every area brief, so a reviewer per concern looks for them. For each concern, record the areas it crosses and the specific boundaries to trace, such as a call from one area into another or a model two areas share. Take them from the map.

Show the user the area table, the excluded paths, the concerns, and the planned reviewer count. Then stop and wait for the user to confirm or redirect. Do not start Step 3 in the same turn.

## Step 3, Assign models

Use the reviewer models the user names. Otherwise use the default models listed in Step 3 of the `interrogate` skill, at the effort listed there.

Running every model on every area costs too much at this scale. Assign reviewers this way:

- One reviewer per area. Rotate models across areas so each model covers a share.
- A second reviewer on a different model for each high-risk area.
- One reviewer per cross-cutting concern, again rotating models.

Each reviewer runs on the model this rotation assigns it, not on the parent's model. Spawn a reviewer with the host's subagent tool when that tool can select its model. Otherwise run it through the matching local CLI with the commands and model IDs from the `run-ai-clis` skill: `claude` for Claude models, `codex exec` for GPT models, and `opencode run` for other families. Keep every reviewer read-only.

If the host or CLI rejects a model, use the closest available model of the same family and say so. If no model of that family is available, rotate across the models that remain and say so. If only one model is available, run every brief on it, skip the second reviewer on high-risk areas, and say so. Do not block the review on an unavailable model.

## Step 4, Fan out

Build every reviewer's prompt from `references/reviewer-prompt.md`, filling in the purpose, the reviewer's brief, the full area table, and the contents of `rubric.md` and `code-quality-review.md` from interrogate's `references/` directory. An area brief is the area's record from Step 2. A concern brief is the concern, the areas it crosses, and the boundaries to trace. Every brief stands alone. A reviewer sees no other reviewer's brief or output.

Launch all reviewers concurrently. If the host caps concurrency, run them in waves. For reviewers that run through a CLI, write each filled prompt to its own file and pass it on stdin, not as a quoted argument, and write each reviewer's output to its own file. Run at most 4 CLI reviewers at once.

## Step 5, Collect

Every area and every concern needs a result. Drop a result that ignores its brief or the output format, and retry a reviewer whose run fails. Retry once, with the same brief and the same model. After a second miss, record a gap. A gap is not a clean result. Do not report an area as clean because its reviewer never returned.

Compare each area reviewer's `Read` list with the area's core files. If it skipped most of them, retry once. If it still skipped some, report the area as partial and name the unread files.

## Step 6, Verify

A review of a whole codebase returns many more findings than a diff review, and more of them are wrong. First merge findings that describe the same issue, including the same root cause reported from different areas, and note which models and briefs raised each one.

Then check every merged `critical` and `warning` finding against the code. Open the cited location, trace the claimed path, and mark the finding `confirmed`, `refuted`, or `unverified`. A finding whose cited location does not exist is `refuted`. Skip `nit` findings.

If there are too many findings to check yourself, spawn read-only verifier subagents with the same instructions. Batch area findings by area and concern findings by concern, and have each verifier return a mark and evidence for every finding in its batch.

## Step 7, Judge

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. A finding raised independently by two models, or by an area reviewer and a concern reviewer, is the highest signal.

Read `lead-judgment.md` from interrogate's `references/` directory and apply it, with these changes, because it was written for a diff:

- Reviewers here read existing code in full, not a diff. Do not dismiss a finding because the author didn't touch the code or because the reviewer could not see the call chain.
- A pattern repeated across the codebase is a finding, not missing context. When areas share the same flaw, report it once as a systemic issue.
- Ignore any limit it sets on the length of Act on, and use the one below.

Put every finding in one of four buckets, with the models that raised it and a one-line rationale:

- **Act on**. Confirmed issues affecting correctness, security, or maintainability given the system's purpose. Aim for at most 10, ordered by severity.
- **Consider**. Legitimate, but you're not sure they outweigh the cost of addressing them now. Put unverified `critical` findings here, marked unverified.
- **Noted**. Technically valid but not actionable, and unverified `warning` findings.
- **Dismissed**. Wrong, refuted, nitpicky, or missing context, with a brief reason.

## Output format

### Purpose
> [The purpose paragraph from Step 1]

### Coverage
| Area or concern | Paths | Model(s) | Result |
|-----------------|-------|----------|--------|

Paths for a concern are the boundaries it traced. Result is `N findings`, `no findings`, `partial: [unread files]`, or `GAP: [reason]`. Mark high-risk areas that ran on a single model. List excluded paths below the table.

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
