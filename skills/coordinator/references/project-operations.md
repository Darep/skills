# Project operations

## Becoming the coordinator

When this thread starts coordinating, on a project's first run or when taking over:

1. Find an existing coordinator (see "Finding the coordinator"). If one exists and it isn't this
   thread, ask the user which one to keep. Don't run two.
2. Rename this thread to `<project>: Coordinator` (`t3_thread_update`, `action: "rename"`) and pin
   it (`t3_thread_organize`, `action: "pin"`). Look up its id with `t3_thread_list`
   (`titleContains: "<project>: Coordinator"`) and write the id and link to memory.
3. If `~/work/coordinator/<project>/` doesn't exist, create it with `library/`. Use the memory
   template below and seed `MEMORY.md` from the README, `AGENTS.md`/`CLAUDE.md`, `COORDINATOR.md`, the last ~20 commits,
   open PRs, and open workday tasks for this repo if the `workday` skill is installed.
4. Check routines with `list_scheduled_tasks` for the project, and reconcile them with memory.
5. On a project's first run only, start one thread right away: area `explore`, produces `doc`,
   task "Explore the repository without changing anything. Write what it is, how it's built and
   checked, what looks wrong or unfinished, and three to five proposed next threads, each with
   area, produces, task, and done-when." Its proposed threads become proposals when it reports.
6. If `COORDINATOR.md` is missing, propose one from what you learned, covering the topics under
   "The project" in [SKILL.md](../SKILL.md). Write it only after the user agrees.
7. Reply with the Summary, the open questions, and any setup recommendations (instructions,
   routines), and say you're ready.

## Memory template

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
| Who | Area | Title | Produces | Priority | Status | Next | Result | Link |

## Library
- library/<file>: <one line on what it is>, from <thread link>

## Routines
| Name | Schedule | What it does | Scheduled task id |

## Next checks
- YYYY-MM-DD <what to look at, and why then>
```

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

1. Check memory ownership as described in [SKILL.md](../SKILL.md). Read `Coordinator thread`
   from the matching memory. Use `t3_thread_read` to verify its `projectId` and archive state.
2. If the stored thread is missing, archived, or in another project, use `t3_thread_list` with
   the project's id and
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
   the summary from step 2. On a routine run, report the missing coordinator and stop.

## Overview

A read-only summary across projects, from any thread. It writes nothing.

1. Read every `~/work/coordinator/*/MEMORY.md`.
2. For each project, at most four lines: the first sentence of the Summary and the coordinator's
   link; threads `running` or `needs you`, with the Next of each `needs you` row; `you` rows that
   are `todo`, high priority first; Next checks due within 7 days or overdue.
3. Put projects that need the user first (`needs you`, an overdue check, or a `you` row older
   than a week), then projects with running threads, then the rest, one line each.
4. Flag memory updated over 30 days ago as stale, and a missing or archived coordinator thread as
   orphaned, and suggest `/coordinator` in that project.
5. End with one line listing T3 projects that have no memory folder, from `t3_project_list`,
   skipping archived projects and scratch folders.

Don't start threads, send messages, or change memory from Overview. Point the user to the
project's coordinator, or offer Send.
