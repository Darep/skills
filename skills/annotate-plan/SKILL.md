---
name: annotate-plan
description: Create annotatable HTML review pages for Codex plans. Use when the user wants a plan that can be opened in a browser, reviewed interactively, annotated section by section, and converted into a concise prompt to paste back into Codex.
---

# Annotate Plan

Create the plan normally in chat, then render the same Markdown into a local
HTML review page.

## Workflow

1. Write the plan in Markdown in the chat response.
2. Save the same Markdown to a `.md` file in a temporary or user-requested
   output directory.
3. Render it:

```bash
python3 <skill-dir>/scripts/render_plan.py \
  --input <plan.md> \
  --output <output-dir>/plan.html \
  --title "Plan Review"
```

4. Serve the output directory:

```bash
python3 -m http.server 8765 --directory <output-dir>
```

5. Return the localhost URL:

```text
http://127.0.0.1:8765/plan.html
```

Tell the user annotations are stored only in their browser and the page's
`Copy Prompt` button creates the prompt to paste back into Codex.

## Notes

- Use another port if `8765` is busy.
- Keep the HTML static; do not add a custom POST server.
- Do not add Markdown dependencies. The renderer intentionally supports only
  simple headings, paragraphs, lists, and fenced code blocks.
