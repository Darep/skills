---
name: annotate-plan
description: Create HTML review pages for plans. Use when the user requests a HTML plan, an interactive plan review, or to annotate the plan.
---

# Annotate Plan

Write the plan as Markdown, then serve it as a local HTML review page.

## Workflow

1. Write the plan in Markdown to a `.md` file in a temporary or user-requested
   location. Showing the plan in the chat response too is optional.
2. Serve it:

```bash
python3 <skill-dir>/scripts/render_plan.py \
  --input <plan.md> \
  --serve \
  --port 8765
```

3. Return the printed localhost URL:

```text
http://127.0.0.1:8765/plan.html
```

Tell the user annotations are stored only in their browser and the page's
`Copy Prompt` button creates the prompt to paste back into Codex.
The plan is shown as one document; hover a plan element and click `+` to
annotate it in the side panel.

## Notes

- Use another port if `8765` is busy.
- Use `--output <plan.html>` instead of `--serve` only when the user asks for a standalone HTML file. `--output` and `--serve` are mutually exclusive.
- The page title comes from the first heading in the Markdown.
