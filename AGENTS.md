# AGENTS.md

pstack skills are not verbatim copies. To update one:

1. Find our adaptations: diff the skill against upstream at the commit it was last synced from (named in `git log -- skills/<name>`, else the README pstack pin).
2. Copy the latest upstream skill verbatim.
3. Reapply the adaptations, and adapt new upstream text the same way.

Adaptations, and why:

- **Host-neutral wording** instead of Cursor's Task fields, tool names, and `pstack-models.mdc`, so the skills run in Claude Code, Codex, and OpenCode.
- **Claude model defaults** for roles the host spawns itself (`how`), because hosts can't spawn other families. `interrogate` keeps its model families and runs them through `run-ai-clis`, because its value is model diversity.
- **`gh` and `glab`** for PR work, no Graphite, so it works on GitHub and GitLab.
- **`opening-a-pr` is a skill** made from pstack's playbook of the same name, because we don't ship the playbook.
- **No references to skills we don't ship** (such as `why`). Inline what a skill needs, so nothing points at a missing skill.
- **The deviations listed in `README.md`**, for the reasons given there.

## Installing

Symlink each skill into `~/.agents/skills`. The links point at this repo, so pulling updates the installed skills. Codex, OpenCode, and Gemini CLI read that directory.

Claude Code and Antigravity don't. If the user runs either, also link into its directory:

- **Claude Code:** `~/.claude/skills`
- **Antigravity:** `~/.gemini/config/skills`

Don't link into an agent's own directory, such as `~/.codex/skills`, if the agent reads `~/.agents/skills`. It would load each skill twice.

Run this from the repo root after each pull. It links new skills and removes links to deleted ones. Set `dir` to each install directory in turn:

```sh
dir=~/.agents/skills
mkdir -p "$dir"
for skill in "$PWD"/skills/*; do ln -sfn "$skill" "$dir"/; done
for link in "$dir"/*; do [ -e "$link" ] || rm "$link"; done
```
