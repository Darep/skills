---
name: annotate-plan
description: Create annotatable HTML review pages for Codex plans. Use when the user wants a plan that can be opened in a browser, reviewed interactively, annotated section by section, and converted into a concise prompt to paste back into Codex.
---

# Annotate Plan

Create the plan normally in chat, then serve the same Markdown as a local HTML
review page.

## Workflow

1. Write the plan in Markdown in the chat response.
2. Save the same Markdown to a `.md` file in a temporary or user-requested
   location.
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
- Keep the HTML static; do not add a custom POST server.
- Do not add Markdown dependencies. The renderer intentionally supports only
  simple headings, paragraphs, lists, and fenced code blocks.
- Use `--output <plan.html>` instead of `--serve` only when the user asks for a
  standalone HTML file. `--output` and `--serve` are mutually exclusive.
