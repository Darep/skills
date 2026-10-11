# AGENTS.md

Skills live in `skills/<name>/`. `README.md` credits each community skill's source. Skills under "My Skills" are ours.

## Updating community skills

Community skills are verbatim copies of upstream, except pstack (below). To update one:

1. Check that the README source is still the freshest copy. A skill can live in more than one repo (`poteto/how` is older than pstack's `how`). Ask before switching sources.
2. Resolve upstream's latest commit once and use that SHA throughout.
3. Replace our skill folder with upstream's, including deletions and renames. Do not reword or reformat. Keep a `LICENSE` file we added.
4. Commit as `fix(<skill>): update skill to upstream <short-sha>`.

## pstack

pstack skills are adapted to run in Claude Code, Codex, and OpenCode, not only Cursor. Sync them by reapplying our adaptations to the new upstream:

1. Find the base: the upstream SHA named in the newest commit for this skill (`git log -- skills/<name>`), or the README pstack pin if none names one.
2. Diff our copy against upstream at the base. The differences are our adaptations.
3. Copy upstream at the latest SHA, then reapply those adaptations. Adapt new upstream text the same way.
4. Diff against the latest SHA. Every remaining difference must fit an adaptation below.

Adaptations:

- The host's subagent tool and plain-language settings, not Cursor's Task fields or `pstack-models.mdc`.
- Claude defaults for roles the host spawns itself (`how`). `interrogate` keeps its model families and runs them through `run-ai-clis`.
- GitHub (`gh`) and GitLab (`glab`) for PR work, no Graphite.
- `opening-a-pr` is a skill made from pstack's `opening-a-pr` playbook.
- No references to skills this repo doesn't ship (such as `why`). Inline what a skill needs from them.
- The deviations listed in `README.md`.

Move the README pstack pin only when every pstack skill is synced to it.
