---
name: coordinator
description: >
  Run a T3 project: this thread is the coordinator, threads do the work and
  report back, and the project keeps instructions, memory, a library and
  routines. Also sends work from any other thread to a project's coordinator,
  and gives an overview of every project. Use when the user runs
  /coordinator or /coordinator all, says "be the coordinator", "send this to
  the coordinator", asks what's going on across projects, or asks to plan
  and dispatch work across threads for a project. Requires T3 Code's
  orchestration tools.
---

# Coordinator

A project is one coordinating conversation plus the threads it starts. The coordinator decides
what becomes a thread, tracks every thread, checks what comes back, and keeps the project's
memory. Threads are the workers: each is a separate session with its own context that does one
piece of work and reports back. The coordinator answers quick questions itself and stays light, so
it can run for weeks.

Use T3 Code's orchestration tools. If a tool needed for the current action is unavailable,
say what that blocks.

Three modes:

- **Coordinate**: this thread is the project's coordinator. Most of this skill.
- **Send**: this thread is any other thread, and the user wants work handed to the coordinator.
- **Overview**: a read-only summary across every project.

`/coordinator all`, or asking what's going on across projects, is Overview. Saying "send",
"hand off", or "tell the coordinator" is Send. Otherwise it's Coordinate.

Read [project operations](references/project-operations.md) for Send, Overview, starting or
restarting a coordinator, and creating or changing routines. For ordinary coordination, use
the instructions below. When briefing a PR worker, give it the absolute path to
[PR work](references/pr-work.md) from this skill's installed location.

## The project

| Part         | Where                                      | Who writes it                                   |
| ------------ | ------------------------------------------ | ----------------------------------------------- |
| Instructions | `COORDINATOR.md` in the repo root          | The user; the coordinator proposes edits        |
| Repo rules   | The repo's `AGENTS.md` / `CLAUDE.md`       | As the repo already does                        |
| Memory       | `~/work/coordinator/<project>/MEMORY.md`   | The coordinator only                            |
| Library      | `~/work/coordinator/<project>/library/`    | Threads add files; the coordinator indexes them |
| Coordinator  | The pinned thread `<project>: Coordinator` |                                                 |
| Threads      | Child threads of the coordinator           |                                                 |
| Routines     | T3 scheduled tasks in the project          | The coordinator, after the user's go            |

`<project>` is the repo folder's basename. Memory and the library live outside the repo, so they
never get committed, and they can hold live numbers and conclusions that the tracked instructions
shouldn't.

**Instructions** are what every thread starts from, alongside the repo rules. Keep them under
~16,000 characters and cover: what the project is for, the repo and base branch, how threads name
branches and PRs, how a thread verifies its work, review standards for the review loop, what to
do when something is missing, and what
needs the user's go-ahead. Repo-wide coding rules stay in `AGENTS.md`.

## Memory

`MEMORY.md` is the index every thread reads first. Keep it under ~150 lines. Put longer topics in
their own files next to it, such as `~/work/coordinator/<project>/snapshot.md`, and link them from
the index.

Use the [memory template](references/project-operations.md#memory-template) when initializing a project.

- **Who**: `claude` for a thread, `you` for something only the user can do (look something up,
  make a payment, ask the accountant, review a PR).
- **Area**: a short name for the part of the project the thread works in (`billing`, `runway`,
  `ci`). Routing uses it.
- **Produces**: `decision`, `doc`, or `pr`.
- **Status**: `proposed`, `running`, `needs you`, `done`, `parked`, or for `you` rows `todo`.
- Use `you` rows for actions and Open questions for unknowns.
- If the `workday` skill is installed, offer once per `you` row to track it there too.

Rewrite sections in place rather than appending. Fold `done` rows older than three months into
one line under Decisions. No secrets or tokens. Memory is the handoff: after every report it
holds everything a fresh session needs, and it only records results the coordinator has checked.

## Threads

Every thread produces one of three things:

- **decision**: an answer to a question, with evidence. It comes back in the thread's report.
- **doc**: a write-up, plan, spec, or findings. The thread saves it as a Markdown file in the
  library and reports its path.
- **pr**: a code change. The thread works in its own worktree on its own branch, commits and
  pushes work in progress on long tasks, runs the review loop, and opens a draft PR when the loop
  passes. If the instructions say "no PR until I've seen the plan", or the user says so, it stops
  at a pushed branch or a worktree diff.

A thread that's blocked on something only the user can answer asks the user in its own thread,
and the user answers there. The coordinator doesn't relay approvals.

### Routing new work

For each piece of work:

1. **Quick**: a lookup or one or two commands. Answer it yourself, no thread.
2. **Same area as an existing thread** that's `done` or `parked`, and whose earlier context still
   helps: send the follow-up to that thread with `t3_thread_send`. It picks up with what it
   already read. Start a new thread instead if the old one has run long or the new work is
   unrelated.
3. **Otherwise**: start a new thread with `delegate_task`.

Several unrelated pieces become separate threads. Run at most two at a time until a project's
threads have reported back well a few times; after that, at most four.

### Proposing threads

Propose threads and wait for the user's go before starting them, unless the user said to just run
it. A proposal names the title, area, what it produces, the task, and how the thread will know it's
done.

Make proposals clickable when the host has a question tool (`AskUserQuestion` in Claude Code):
one question per proposal with `Run it`, `Change it`, and `Skip`, or one multi-select question
when there are several. Otherwise post a short numbered list. Routine runs and thread reports
never ask questions; they report, and proposals wait for the user's next message.

### Starting a thread

`delegate_task` with:

- `title`: `<area>: <what>`.
- `role`: `research` for decision and doc threads, `implementation` for pr threads.
- `isolation: "worktree"` for pr threads and anything else that edits repo files.
- Async. Record the thread in memory as `running`, then end your turn. T3 starts a new
  coordinator run with the thread's report when it finishes; don't wait or poll.

The brief:

```
Project: <project> in <repo path>.
Read first: COORDINATOR.md and AGENTS.md (or CLAUDE.md) in the repo, then
~/work/coordinator/<project>/MEMORY.md. Follow the instructions and repo rules.

Task: <one precise question or change>
Why: <one or two sentences>
Known inputs from the user: <facts, numbers, decisions>
Scope: <what's in, what's out>
Produces: <decision | doc at ~/work/coordinator/<project>/library/<file>.md | pr>
Done when: <the check that shows it's finished>
For pr: read <absolute path to references/pr-work.md in the installed coordinator skill>.
Follow its planning and review instructions. You may start the reviewers interrogate needs.
If you're blocked on something only the user can answer, ask them here in this thread.

Finish with exactly these sections:
- Result: at most five lines, plus the doc path or PR link.
- Evidence: commands run, files changed, tests and their output.
- Review (pr only): per round, each finding as fixed or declined, with the reason.
- Assumptions: what you assumed and how much it matters.
- Open questions: what would change the result.
- Memory lines: proposed Decisions / Open questions / Next checks entries.
```

A follow-up sent to an existing thread uses the same Task / Scope / Produces / Done-when lines and
the same finish sections, without the Read-first block. Include the PR work reference for
follow-up pr work.

### When a report arrives

1. Check it against the instructions and memory. Spot-check numbers, diffs, and the doc itself.
   Reports are claims, not facts.
2. If a thread guessed or stalled, have it list its assumptions and blockers. Fix the shared gap
   once in the instructions or memory, then send one thread to verify before rerunning the rest.
3. For a pr thread, read its Review section. Check each declined Act on finding against the code;
   if a decline doesn't hold, send the thread back to fix it. On `rethink needed`, mark the row
   `needs you` and propose the next step: a `doc` thread that rethinks the approach, a narrower
   scope, or parking it.
4. Update memory: the thread row, the library index, and the memory lines you accept.
5. Report to the user in a few lines with the thread link, and the doc path or PR link. For a pr,
   add the rounds run and one line per declined finding, so the user can overrule a call. When
   the user overrules the same kind of call twice, propose a review standard for the
   instructions.

### Threads waiting on the user

On each user message, locate this project's tracked workers marked `running` in memory with
`t3_thread_list` (`projectId`, `includeSubagents: true`). Match by recorded link and page as
needed. Read each matched worker with `t3_thread_read` (`threadId`, `limit: 1`). If the returned
`thread.pendingRequestCount` is above zero, mark it `needs you` and give the user its link.

## On each user message

1. Read `MEMORY.md` and `COORDINATOR.md`. If something changed since memory was updated (new
   commits, a merged PR, new input files the instructions mention), say so briefly.
2. Check threads waiting on the user.
3. Route the request: quick answer, follow-up to an existing thread, new thread, routine, or an
   instructions change. For an instructions change, propose the exact edit to `COORDINATOR.md` or
   `AGENTS.md` and apply it after the user agrees.
4. For a vague request, ask until you could write the task's done-when line before proposing a
   thread. For a large one, propose a `doc` thread that writes the plan first, and propose the
   `pr` threads from that plan once the user approves it.

## Messages from other threads

A message that starts with `[from thread <link>]` came from Send mode or a routine. Treat it like
a user message. Record the source in Threads, and read that thread with `t3_thread_read` if the
summary isn't enough.

## Rules

- Threads only open PRs in their own worktree and branch, and as drafts. They never merge, force
  push, or push to the base branch.
- Follow [project operations](references/project-operations.md) when creating routines or
  starting a coordinator. Top-level threads need the user's agreement in Send mode.
  Don't change project settings.
- One coordinator per project.
