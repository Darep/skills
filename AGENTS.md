# AGENTS.md

Agent skills under `skills/<name>/`. Most are copied from upstream projects, credited in `README.md`. Stay as close to upstream as possible. Only deliberate local adaptations differ.

## Updating a skill from upstream

1. Find the source in `README.md`. Before syncing, check that the source is still the freshest copy. A skill can live in more than one repo (`how` is in both `poteto/how` and pstack, and pstack is newer).
2. Find the last synced upstream commit from the README pin or the skill's history (`git log -- skills/<name>`).
3. Diff our copy against upstream at that commit. The differences are the local adaptations.
4. Copy the latest upstream files verbatim, then reapply only those adaptations. Do not reword, reformat, or "improve" upstream text.
5. Diff against latest upstream again to confirm only the adaptations remain.

## Local adaptations

- Host-neutral wording so skills work in Claude Code, Codex, OpenCode, and Cursor. No Cursor-only tool fields, paths, or rule files.
- Claude models as defaults where upstream names models a host can't select.
- No references to skills this repo doesn't ship.
- Deviations listed in `README.md` stay.

## Conventions

- One commit per skill or skill group: `fix(<skill>): update skill to upstream <short-sha>`.
- Move a README source pin only when every skill in that group is synced to it.
- Keep each copied skill's upstream `LICENSE`.
