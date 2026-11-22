# PR work

Follow these steps in the implementation worktree.

## Plan before editing

Start implementing when both the fix and its scope are clear. When the approach is uncertain
or the change may alter behavior beyond the request, start with a read-only pass in the same
pr thread. Trace the current behavior through its callers, and record the smallest viable
fix, what it would change, what's out of scope, and how to verify it through the normal entry
point.

If a choice about existing behavior or scope is still unresolved, ask the user in the pr
thread before editing. State the options and recommend one. Record the answer in the
thread's Scope and update Done when to match. Proceed directly when planning leaves no
scope decision for the user, or once the user answers. Ask again only if new evidence
requires a decision that would change the agreed scope.

## Review loop

A pr thread reviews its own change before it opens the PR, in up to three rounds, unless the
instructions set another limit or exempt a kind of change. If required review is unavailable,
report the blocker. Commit the intended changes before the first round so the branch diff
includes them. Open the PR from the commit that passed review and verification. Each round:

1. Run the `interrogate` skill on the branch's diff against the base branch. Use the brief's Task,
   Why, and Scope, including any decisions from planning, as the intent. From round 2 on, add the
   earlier rounds' findings and what was done with each, and ask reviewers not to raise a
   declined finding again unless they bring new evidence.
2. Triage every Act on and Consider finding as `fix` or `decline`, with a one-line reason. Fix
   real problems in this change's scope: correctness, security, data loss, broken contracts, and
   maintainability that would block a real PR. Decline findings that are speculative, outside
   the scope, a matter of taste, already handled, or in conflict with the instructions or repo
   rules. Report real pre-existing problems outside the agreed scope as follow-ups. Apply any
   review standards the instructions give. Decline an Act on finding only with a concrete reason.
3. No `fix` findings: verify the reviewed commit against Done when. Open the draft PR (see "Opening
   the PR") if verification passes. If it exposes an in-scope defect, handle it like a `fix`
   finding. Report any check you cannot complete as a blocker.
4. `fix` findings before the last round: fix them, commit, rerun the checks, and start the next
   round.
5. `fix` findings in the last round: stop the review loop and leave the draft unopened. Push the
   branch and report `Result: rethink needed` with the open findings and what you'd reconsider.

## Opening the PR

Follow the `opening-a-pr` skill for the forge (`gh` or `glab`), commits, title, and body, with
one exception: coordinator PRs open as drafts. The user marks them ready. The review loop already
covers its `interrogate` step.
