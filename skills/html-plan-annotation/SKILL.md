---
name: html-plan-annotation
description: Create HTML review pages for plans. Use when the user requests a HTML plan, an interactive plan review, or to annotate the plan.
---

# HTML Plan with Annotations

Create the plan normally in chat, then serve the same Markdown as a local HTML review page.

## Workflow

1. Write the plan in Markdown in the chat response.
2. Save the same Markdown to a `.md` file in a temporary or user-requested location.
3. Serve it:

```bash
python3 <skill-dir>/scripts/render_plan.py \
  --input <plan.md> \
  --serve \
  --port 8765
```

4. Return the printed localhost URL:

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
- Use `--title <title>` if you want to provide a custom title for the HTML page -- by default, it's inferred from the first heading in the Markdown.
