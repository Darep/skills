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

This needs T3 Code's tools (`delegate_task`, `t3_thread_list`, `t3_thread_send`,
`schedule_task`). If they aren't available, say so and stop.

Three modes:

- **Coordinate**: this thread is the project's coordinator. Most of this skill.
- **Send**: this thread is any other thread, and the user wants work handed to the coordinator.
- **Overview**: a read-only summary across every project.

`/coordinator all`, or asking what's going on across projects, is Overview. Saying "send",
"hand off", or "tell the coordinator" is Send. Otherwise it's Coordinate.

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
branches and PRs, how a thread verifies its work, what to do when something is missing, and what
needs the user's go-ahead. Repo-wide coding rules stay in `AGENTS.md`.

## Memory

`MEMORY.md` is the index every thread reads first. Keep it under ~150 lines. Put longer topics in
their own files next to it, such as `~/work/coordinator/<project>/snapshot.md`, and link them from
the index.

```markdown
# <project>

Coordinator memory for <repo path>. Updated <YYYY-MM-DD>.
Coordinator thread: <thread id> <thread link>

## Summary
2 to 5 sentences: what the project is, where it stands, what's next.

## Decisions
- YYYY-MM-DD <what the user decided, and why if it isn't obvious>

## Open questions
- <question>: <what would resolve it>

## Threads
| Who | Area | Title | Produces | Status | Result | Link |

## Library
- library/<file>: <one line on what it is>, from <thread link>

## Routines
| Name | Schedule | What it does | Scheduled task id |

## Next checks
- YYYY-MM-DD <what to look at, and why then>
```

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
  pushes work in progress on long tasks, and opens a draft PR when done. If the instructions say
  "no PR until I've seen the plan", or the user says so, it stops at a pushed branch or a
  worktree diff.

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
If you're blocked on something only the user can answer, ask them here in this thread.

Finish with exactly these sections:
- Result: at most five lines, plus the doc path or PR link.
- Evidence: commands run, files changed, tests and their output.
- Assumptions: what you assumed and how much it matters.
- Open questions: what would change the result.
- Memory lines: proposed Decisions / Open questions / Next checks entries.
```

A follow-up sent to an existing thread uses the same Task / Produces / Done-when lines and the
same finish sections, without the Read-first block.

### When a report arrives

1. Check it against the instructions and memory. Spot-check numbers, diffs, and the doc itself.
   Reports are claims, not facts.
2. If a thread guessed or stalled, have it list its assumptions and blockers. Fix the shared gap
   once in the instructions or memory, then send one thread to verify before rerunning the rest.
3. Update memory: the thread row, the library index, and the memory lines you accept.
4. Report to the user in a few lines with the thread link, and the doc path or PR link.

### Threads waiting on the user

On each user message, check running threads with `t3_thread_list` (`includeSubagents: true`). A
thread with `pendingRequestCount` above zero is waiting on the user: mark it `needs you` and give
the user its link.

## Becoming the coordinator

When this thread starts coordinating, on a project's first run or when taking over:

1. Find an existing coordinator (see "Finding the coordinator"). If one exists and it isn't this
   thread, ask the user which one to keep. Don't run two.
2. Rename this thread to `<project>: Coordinator` (`t3_thread_update`, `action: "rename"`) and pin
   it (`t3_thread_organize`, `action: "pin"`). Look up its id with `t3_thread_list`
   (`titleContains: "<project>: Coordinator"`) and write the id and link to memory.
3. If `~/work/coordinator/<project>/` doesn't exist, create it with `library/` and seed
   `MEMORY.md` from the README, `AGENTS.md`/`CLAUDE.md`, `COORDINATOR.md`, the last ~20 commits,
   open PRs, and open workday tasks for this repo if the `workday` skill is installed.
4. Check routines with `list_scheduled_tasks` for the project, and reconcile them with memory.
5. On a project's first run only, start one thread right away: area `explore`, produces `doc`,
   task "Explore the repository without changing anything. Write what it is, how it's built and
   checked, what looks wrong or unfinished, and three to five proposed next threads, each with
   area, produces, task, and done-when." Its proposed threads become proposals when it reports.
6. If `COORDINATOR.md` is missing, propose one from what you learned, covering the topics under
   "The project". Write it only after the user agrees.
7. Reply with the Summary, the open questions, and any setup recommendations (instructions,
   routines), and say you're ready.

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

## Routines

Routines run as their own threads in the project, then report to the coordinator.

1. Propose it like a thread: name, schedule, what each run does, and that every run spends
   tokens whether or not anything changed. Wait for the user's go.
2. Create it with `schedule_task`: the project's `projectId`, `bindToCurrentThread: false`,
   `freshSession: true`, a `title` of `<project>: <name>`, and `fixed_time` with `timeOfDay` and
   `weekdays` for calendar schedules. Write the prompt so it stands alone: `Routine "<name>" for
   <project>. Read COORDINATOR.md and ~/work/coordinator/<project>/MEMORY.md. <What to check>.
   Then use the coordinator skill's Send mode, without asking first, to send the coordinator
   your result in at most three sentences, or "nothing new".`
3. Record it in memory's Routines with the scheduled task id.
4. To change or pause a routine, call `schedule_task` with its `scheduledTaskId` (`enabled: false`
   pauses it). Delete one only when the user asks.

## Fresh start

Because memory is the handoff, the coordinator can start over at any time. When its conversation
has been compacted more than once, or the user says it's gotten slow or confused, bring memory up
to date and tell the user to restart it: from any thread, `t3_thread_send` to the coordinator
with `freshContext: true` and the message `/coordinator`.

## Finding the coordinator

1. Read `Coordinator thread` from `~/work/coordinator/<project>/MEMORY.md`, and check with
   `t3_thread_read` that the thread exists and isn't archived.
2. If memory has no id, or that thread is gone, run `t3_thread_list` with the project's id and
   `titleContains: "<project>: Coordinator"`. Only count threads titled exactly
   `<project>: Coordinator` with no `parentThreadId`.
3. More than one match: ask the user which is the coordinator.

## Sending work to the coordinator

In Send mode, from any thread in the project:

1. Find the coordinator.
2. Write the message: `[from thread <this thread's link>]`, then at most three plain sentences on
   what the work is, where it stands, and what's left or what to decide. No secrets or tokens.
3. Show the user the message and ask for the go, unless this thread is a routine run. Send it with
   `t3_thread_send` and `mode: "queue"`, and give the user the coordinator's link.
4. If the project has no coordinator, offer to start one. On a yes, use `t3_thread_launch` in the
   project with the title `<project>: Coordinator` and the message `/coordinator`, followed by
   the summary from step 2.

## Overview

A read-only summary across projects, from any thread. It writes nothing.

1. Read every `~/work/coordinator/*/MEMORY.md`.
2. For each project, at most four lines: the first sentence of the Summary and the coordinator's
   link; threads `running` or `needs you`; `you` rows that are `todo`; Next checks due within 7
   days or overdue.
3. Put projects that need the user first (`needs you`, an overdue check, or a `you` row older
   than a week), then projects with running threads, then the rest, one line each.
4. Flag memory updated over 30 days ago as stale, and a missing or archived coordinator thread as
   orphaned, and suggest `/coordinator` in that project.
5. End with one line listing T3 projects that have no memory folder, from `t3_project_list`,
   skipping archived projects and scratch folders.

Don't start threads, send messages, or change memory from Overview. Point the user to the
project's coordinator, or offer Send.

## Rules

- Threads only open PRs in their own worktree and branch, and as drafts. They never merge, force
  push, or push to the base branch.
- Create routines only through the Routines flow, and top-level threads only in Send mode when
  the user agrees to start a coordinator. Don't change project settings.
- One coordinator per project.
