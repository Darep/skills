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
