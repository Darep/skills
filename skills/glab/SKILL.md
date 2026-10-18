---
name: glab
description: Guidance for using the GitLab CLI (glab) to manage GitLab issues, merge requests, CI/CD pipelines, repositories, and other GitLab operations from the command line. Use this skill when the user needs to interact with GitLab resources or perform GitLab workflows.
allowed-tools: Bash, Read, Grep, Glob
---

Use `glab` for all GitLab operations from the shell. GitLab calls pull requests **merge requests (MRs)**.

Target a different project with `-R OWNER/REPO`, `GROUP/NAMESPACE/REPO`, project URL, or Git remote URL.

Most `glab mr` subcommands default to the **current branch's open MR** when no ID or branch is given.

---

## Workflow 1: Create a merge request

Create the MR. Pass title and body via HEREDOC:

```bash
glab mr create --title "the mr title" --description "$(cat <<'EOF'
This MR:

<1-3 bullet points>

EOF
)" --target-branch <base-branch> --yes
```

Common flags:

| Flag                     | Use                                                     |
| ------------------------ | ------------------------------------------------------- |
| `-f` / `--fill`          | Auto title/description from commits; also pushes branch |
| `--fill-commit-body`     | With `--fill`, include each commit body in description  |
| `--draft` / `--wip`      | Draft MR                                                |
| `--reviewer user1,user2` | Request reviewers                                       |
| `-a` / `--assignee`      | Assignees                                               |
| `-l` / `--label`         | Labels (repeatable)                                     |
| `-i` / `--related-issue` | Link/branch from issue                                  |
| `--remove-source-branch` | Delete source branch on merge                           |
| `--squash-before-merge`  | Squash on merge                                         |
| `--auto-merge`           | Merge when checks pass                                  |
| `-w` / `--web`           | Finish in browser                                       |
| `-y` / `--yes`           | Skip confirmation prompts                               |

**Preferred one-shot** when commit messages are good:

```bash
glab mr create --fill --fill-commit-body --yes --target-branch <base-branch>
```

Note: `glab mr new` is an alias for `glab mr create`.

### Return the MR URL

Report the URL from command output. If missing, run:

```bash
glab mr view --web   # or: glab mr view -F json
```

---

## Workflow 2: Review merge requests

When the user asks to review MRs, triage review queue, or review a specific MR.

### 1. Find MRs to review

```bash
# MRs requesting your review
glab mr list --reviewer=@me

# Open MRs assigned to you
glab mr list --assignee=@me

# Filter further
glab mr list --search "feature X"
glab mr list --source-branch=<branch>
```

Use `--all`, `-M` (merged), or `-c` (closed) when history is needed.

### 2. Inspect an MR

By ID, branch name, or current branch:

```bash
glab mr view <id-or-branch>
glab mr view <id> --comments          # discussion threads
glab mr view <id> --unresolved        # open threads only
glab mr view <id> -F json             # machine-readable
```

```bash
glab mr diff <id-or-branch>           # code changes
glab mr diff <id> --raw               # pipe-friendly
```

```bash
glab ci status --branch=<source-branch>
glab ci status --live                 # watch until pipeline ends
glab ci trace <job-name>              # job logs
```

```bash
glab mr approvers <id>                # who can approve
```

### 3. Leave feedback

**General comment** (new discussion thread):

```bash
glab mr note create <id> -m "$(cat <<'EOF'
Comment/Feedback here.
EOF
)"
```

**Inline diff comment**:

```bash
glab mr note create <id> --file path/to/file.go --line 42 -m "Comment on this line"
glab mr note create <id> --file path/to/file.go --old-line 7 -m "Why remove this?"
```

**Reply to a thread** (8+ char discussion ID prefix):

```bash
glab mr note create <id> --reply abc12345 -m "Agreed, fixed."
```

**Bot/status note** (non-blocking):

```bash
glab mr note create <id> -m "CI green" --resolvable=false
```

**Resolve a thread**:

```bash
glab mr note resolve <discussion-id-prefix> <id>
```

### 4. Approve, request changes, or merge

```bash
glab mr approve <id-or-branch>
glab mr revoke <id-or-branch>         # undo approval
```

Update MR metadata after review:

```bash
glab mr update <id> --ready           # mark draft as ready
glab mr update <id> --reviewer +user  # add reviewer
glab mr update <id> -l bugfix         # add label
```

---

## Quick reference

| Task                 | Command                             |
| -------------------- | ----------------------------------- |
| List open MRs        | `glab mr list`                      |
| MRs for me to review | `glab mr list --reviewer=@me`       |
| View MR              | `glab mr view <id>`                 |
| View diff            | `glab mr diff <id>`                 |
| Pipeline status      | `glab ci status --branch=<branch>`  |
| Create MR            | `glab mr create --fill --yes`       |
| Approve              | `glab mr approve <id>`              |
| Comment              | `glab mr note create <id> -m "..."` |
| Merge                | `glab mr merge <id> -y`             |
| Other repo           | add `-R OWNER/REPO` to any command  |

## Other useful commands

- `glab issue …` — issues (link with `glab mr create -i <issue-id>`)
- `glab api <endpoint>` — raw GitLab API when no subcommand exists
- `glab repo view` — project info
- `glab config get host` — configured GitLab host
