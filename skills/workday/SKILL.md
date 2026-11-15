---
name: workday
description: >
  Track the user's tasks as markdown files in ~/work/workday.
  Use when the user starts, updates, or finishes a task; asks what they're
  working on, what's next, or what they did (standup); says "sync workday";
  or wants to pick up an earlier workday task.
---

# Workday

Each task gets one file, `~/work/workday/YYYY-MM-DD-<slug>.md`, dated the day the task started. Aim to finish a task that day. If it runs longer, keep the same file.

The slug is short kebab-case `<repo-or-area>-<topic>`, e.g. `acme-web-ci-parallel-tests`. Match task files with `????-??-??-*.md` so the glob skips `README.md`. To list open tasks, run `grep -L '^status: done' ~/work/workday/????-??-??-*.md`.

## Task file

```markdown
---
title: "acme-web: run CI tests in parallel"
status: waiting
priority: mid
next: waiting on review from X
repo: ~/work/acme-web
branch: chore/ci-parallel-tests
mr: https://gitlab.com/acme/acme-web/-/merge_requests/1234
sessions: [opencode:ses_0a1b2c3d4e5f6g7h8i9j0k1l2m]
links: []
---

## Overview

The web app's unit tests are slow. !1234 splits the CI test job into parallel jobs.

## Todo

- [x] Split the test job into 4 parallel jobs
- [ ] Address review threads on !1234
- [ ] Remove the old `test` job once merged

## Changelog

- 2026-09-29 13:13 Created; !1234 open
- 2026-09-30 10:02 Pipeline passed; 2 unresolved threads
- 2026-09-30 12:34 Approved by X
```

- `status`: `active` (your move), `waiting` (someone else's), or `done`.
- `priority`: `high`, `mid`, or `low`. Ask the user when unsure.
- `next`: one concrete action, or `waiting on <who/what>`. Keep it current, and empty it when the task is done. When the task has a Todo, `next` is the first unchecked item, unless that item is blocked or something else has to happen first.
- `repo`, `branch`, `mr`: fill these from the current repo and from `glab mr list --source-branch <branch>` or `gh pr list --head <branch>`. Use `~` paths. `mr` holds both GitLab merge request and GitHub pull request URLs, and "MR" in the rest of this skill means either. A task can span several MRs, e.g. one per repo or a stack. Then make each field a list, e.g. `mr: [<url>, <url>]`, and append each new MR when it opens.
- `sessions`: `<tool>:<id>` of every agent session that works on the task (see Session ID).
- `links`: issue tracker URLs (read them with a matching skill if there is one), docs, related MRs.
- **Overview.** Write 2 to 4 sentences on the current state. Rewrite it when it goes stale.
- **Todo.** Optional. Use it for tasks with more than one step left. List checkboxes in the order you'd do them, one short line per item (under about 100 characters). Group items under `###` headings for phases that must land in order. Unlike the Changelog, you can edit the Todo at any time: tick, add, reorder, or delete items that no longer apply. Put background detail (SHAs, caveats, how-to) in the Overview or a notes section, not in the item.
- **Changelog.** Append only. Write one factual line per entry, `- YYYY-MM-DD HH:MM <what changed>`, in local time. Convert UTC timestamps from GitLab or GitHub. Refer to GitLab MRs as `!iid`, GitHub PRs as `#number`, and commits as short SHAs. When a task's MRs span repos, prefix the project: `<project>!iid` or `<repo>#number`.

## Flows

- **Add.** First grep the task files for the branch or MR URL, so you don't create a duplicate. Then create the file, record the session, and log `Created`.
- **Update.** Without being asked, update a tracked task whenever the user reports progress or this session does real work on it. Add a changelog line, then adjust `status`, `next`, the Overview, the Todo and `sessions`. Tick Todo items as they're done and add new ones as work turns up. The changelog line covers what moves the task: finished items, blockers, decisions. Leave out side details such as a renamed CSS class.
- **Today.** List active tasks as a numbered list of their `next`, with Todo progress like `3/8` for tasks that have a Todo. Order them by `priority`, high first, then by which is best to do next. Then list waiting tasks, one line each, also ordered by `priority`.
- **Sync.** Fetch the state of every MR on each open task, and look for an MR on the `branch` of open tasks that have no `mr` yet. Log only what changed since the last entry: commits, pipeline or checks, approval, threads, conflicts, merge or close. Date each line with the sync time, and note the head SHA when new commits landed. Set `status` by whose move it is, e.g. unresolved threads or a failed check make it `active`, and a pending approval makes it `waiting`. Tick Todo items that an MR event clearly completes, e.g. a merge. Once all of a task's MRs are merged or closed, offer to mark it done. Then list my recent MRs and review requests that have no task file, and ask which to add.
- **Done.** If Todo items are unchecked, ask whether they're finished, dropped, or moved to a follow-up task. Then set `status: done`, clear `next`, and log it.
- **Standup.** Gather the changelog lines from the previous working day through today, e.g. Friday to Monday. Output **Yesterday** (a summary of those lines), **Today** (from active tasks' `next`) and **Waiting** (waiting tasks, and what active tasks are blocked on), one line per point, ready to paste.

## GitLab and GitHub

Use `gh` for GitHub and `glab` for GitLab, judging by the MR URL or the repo's remote. Sync checks both, and skips a CLI that isn't installed or logged in.

GitLab:

- `glab mr view <iid> -R <group/project> -F json` works from any directory. `detailed_merge_status` says what's blocking the MR.
- `glab mr list` needs a repo or `-g <group>`. For my MRs and review requests across all projects, use `glab api 'merge_requests?state=opened&scope=created_by_me'` or `...&scope=all&reviewer_username=<me>`, adding `updated_after=<14 days ago>`.

GitHub:

- `gh pr view <url> --json state,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,commits` works from any directory. `mergeStateStatus` says what's blocking the PR.
- `gh pr view` doesn't report unresolved review threads. Count them with GraphQL: `gh api graphql -F owner=<owner> -F repo=<repo> -F n=<number> -f query='query($owner:String!,$repo:String!,$n:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$n){reviewThreads(first:100){nodes{isResolved}}}}}' --jq '[.data.repository.pullRequest.reviewThreads.nodes[]|select(.isResolved|not)]|length'`.
- For my PRs and review requests across all repos, use `gh search prs --author=@me --state=open` or `--review-requested=@me`, adding `--updated '>=<14 days ago>' --json url,title,repository,updatedAt`.

## Session ID

- OpenCode: run `opencode session list --format json -n 10` and pick the entry whose `directory` is the current working directory and whose title matches this conversation. Record it as `opencode:<id>`.
- Claude Code: take the newest `*.jsonl` in `~/.claude/projects/<cwd with every non-alphanumeric character replaced by ->/`. Record it as `claude:<filename without .jsonl>`.
- Cursor: run `echo $CURSOR_CONVERSATION_ID` in the shell. Record it as `cursor:<id>`.

## Rules

- Fetch MR facts from GitLab or GitHub. Never invent them.
- Never edit old changelog lines.
- File sync conflict copies (`*.sync-conflict-*.md` from Syncthing, `*conflicted copy*.md` from Dropbox) are not tasks. Merge each copy into its original as soon as you see one. Keep the changelog lines from both in time order, take the frontmatter and Overview from the file with the latest changelog entry, and keep every Todo item from either file. Then delete the copy and say so. The merge itself gets no changelog line.
- Keep replies short. Report each change in one line, e.g. `acme-web-ci-parallel-tests: waiting → active (2 unresolved threads). Next: address review on !1234.`
