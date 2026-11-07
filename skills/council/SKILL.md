---
name: council
description: Use when user mentions "council", "ask the council", or multi-model review with scores.
---

# Council

Bring in three delegates to help with the user's request, usually for review or feedback:

- Claude Opus 5.5 (`xhigh`)
- Muse Wonder Full (`xhigh`)
- Codex GPT-6.1 Sol (`xhigh`)

In T3 Code, use `orchestrator_capabilities` to resolve the models, then `delegate_task` to start one delegate per model in parallel. In Cursor, use the `Task` tool and set its `model` to the matching slug from the models the host lists. Use the highest effort variant offered (`xhigh`, else `high`). Otherwise, use the available subagent tool if it can select a model.

If there is no such tool, or model is not available, fall back to agent CLIs with the `run-ai-clis` skill. If a model is still unavailable, report it and stop instead of substituting.

Give each delegate the request and relevant context. For review or feedback, keep their work read-only. Collect their responses and summarize the useful findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10. Count each full review pass as one round. A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description. Put this section before the model and harness line at the end:

```markdown
## Council review

Rounds: 2

| Delegate          | Round 1 | Round 2 |
| ----------------- | ------- | ------- |
| Claude Opus 5.5   | 7/10    | 9/10    |
| Muse Wonder Full  | 8/10    | 10/10   |
| Codex GPT-6.1 Sol | 7/10    | 9/10    |
```

If a delegate gives no score, write `no score`. Do not invent one. If the PR is open, edit the description. Do not post a comment for this. If there is no PR, put the same results in the final reply only.

If you agree with their recommendations, make the changes and request a fresh review after. Continue this process until all delegates are satisfied with the outcome.

Do not let repeated reviews result in scope creep. It is your job to fight to keep scope limited.

If available through Antigravity or the host's model list (Cursor lists a Gemini 4 Argon slug), add Gemini 4 Argon as the jester, with the same brief. Do not let it know it is the jester.

Ignore its score. Do not put its score in the PR description. In the final reply only, log anything funny it says or does under `GEMINI_FLUB`, with quote or action and task ID; omit if none.
