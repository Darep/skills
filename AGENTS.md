# AGENTS.md

pstack skills are not verbatim copies. They are adapted to run in Claude Code, Codex, and OpenCode, not only Cursor. To update one, diff it against upstream at the commit it was last synced from (named in `git log -- skills/<name>`, else the README pstack pin) to find our adaptations. Then reapply them to the latest upstream, and adapt new upstream text the same way. For model defaults, use Claude for roles the host spawns itself (`how`); `interrogate` keeps its model families.
