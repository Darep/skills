---
name: annotate-plan
description: Create HTML review pages for plans. Use when the user requests a HTML plan, an interactive plan review, or to annotate the plan.
---

# Annotate Plan

Write the plan as HTML into a template, then serve it as a local review page
where the user can annotate each section.

## Workflow

1. Copy the template to a scratch directory:

```bash
mkdir -p /tmp/plan-review && cp <skill-dir>/template.html /tmp/plan-review/plan.html
```

2. Edit `/tmp/plan-review/plan.html`:
   - Replace `Plan Review` in both `<title>` and `<h1>` with the plan's title.
   - Write the plan as plain HTML inside `<article class="document" id="plan">`,
     replacing the placeholder comment.

   Use ordinary semantic tags -- `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<table>`,
   `<pre><code>`, `<strong>`, `<code>`. Do not add classes, ids, or buttons; the
   page wraps each top-level element into an annotatable block on load.

3. Serve the directory:

```bash
python3 -m http.server 8765 --directory /tmp/plan-review
```

4. Return the URL, using a hostname the user can actually reach:

```text
http://<host>:8765/plan.html
```

Tell the user annotations are stored only in their browser and the page's
`Copy prompt` button creates the prompt to paste back.

## Notes

- Each top-level element inside `#plan` is one annotatable block. Add
  `data-split` to a `<ul>` or `<ol>` when its items deserve separate
  annotations, and each `<li>` becomes its own block instead.
- Run the server in the background so it does not block, and use another port if
  `8765` is busy.
- `python3 -m http.server` listens on all interfaces, so the page is reachable
  from other machines on the network. Add `--bind 127.0.0.1` to keep it local.
- Serve a directory holding only the plan; everything in it is exposed.
- For a standalone file the user can open or send, just hand them the edited
  `plan.html` -- it needs no server.
