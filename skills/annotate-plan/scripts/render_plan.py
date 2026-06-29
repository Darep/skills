#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")


def split_blocks(markdown):
    blocks = []
    current = []
    current_type = None
    lines = markdown.splitlines()
    index = 0

    def flush():
        nonlocal current, current_type
        if current:
            blocks.append({"type": current_type or "paragraph", "text": "\n".join(current)})
        current = []
        current_type = None

    while index < len(lines):
        line = lines[index]

        if line.strip().startswith("```"):
            flush()
            code = [line]
            index += 1
            while index < len(lines):
                code.append(lines[index])
                if lines[index].strip().startswith("```"):
                    index += 1
                    break
                index += 1
            blocks.append({"type": "code", "text": "\n".join(code)})
            continue

        if not line.strip():
            flush()
            index += 1
            continue

        if HEADING_RE.match(line):
            flush()
            blocks.append({"type": "heading", "text": line})
            index += 1
            continue

        line_type = "list" if LIST_RE.match(line) else "paragraph"
        if current_type and current_type != line_type:
            flush()
        current_type = line_type
        current.append(line)
        index += 1

    flush()
    return blocks


def strip_list_marker(line):
    return re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line)


def render_block(block):
    text = block["text"]
    block_type = block["type"]

    if block_type == "heading":
        match = HEADING_RE.match(text)
        level = min(len(match.group(1)) + 1, 6) if match else 2
        body = html.escape(match.group(2) if match else text)
        return f"<h{level}>{body}</h{level}>"

    if block_type == "code":
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return f"<pre><code>{html.escape(chr(10).join(lines))}</code></pre>"

    if block_type == "list":
        ordered = bool(re.match(r"^\s*\d+[.)]\s+", text.splitlines()[0]))
        tag = "ol" if ordered else "ul"
        items = "\n".join(
            f"<li>{html.escape(strip_list_marker(line))}</li>" for line in text.splitlines() if line.strip()
        )
        return f"<{tag}>{items}</{tag}>"

    paragraphs = "<br>".join(html.escape(line) for line in text.splitlines())
    return f"<p>{paragraphs}</p>"


def preview_for(block):
    text = block["text"]
    if block["type"] == "code":
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = lines[0].strip() if lines else "code block"
    elif block["type"] == "heading":
        match = HEADING_RE.match(text)
        text = match.group(2) if match else text
    else:
        text = " ".join(strip_list_marker(line).strip() for line in text.splitlines() if line.strip())
    return text[:120] or "Untitled block"


def build_html(markdown, title):
    blocks = split_blocks(markdown)
    plan_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()[:16]
    block_payload = []
    rendered_blocks = []

    for number, block in enumerate(blocks, start=1):
        block_id = f"block-{number}"
        preview = preview_for(block)
        block_payload.append({"id": block_id, "preview": preview})
        rendered_blocks.append(
            f"""
            <section class="plan-block" id="{block_id}" data-block-id="{block_id}">
              <div class="block-tools">
                <span class="block-id">{block_id}</span>
                <button type="button" data-annotate="{block_id}">Annotate</button>
                <span class="mark" aria-label="Annotated">annotated</span>
              </div>
              <div class="block-content">{render_block(block)}</div>
              <textarea class="annotation" data-note="{block_id}" placeholder="Annotation for this block"></textarea>
            </section>
            """
        )

    title_text = html.escape(title)
    blocks_json = (
        json.dumps(block_payload)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_text}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #f7f7f4;
  --panel: #ffffff;
  --ink: #1f2933;
  --muted: #667085;
  --line: #d6d8dc;
  --accent: #0f766e;
  --accent-ink: #ffffff;
  --note: #fff7d6;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
header {{
  padding: 18px 24px;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}}
h1 {{ margin: 0; font-size: 24px; }}
main {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 18px;
  padding: 18px;
  max-width: 1320px;
  margin: 0 auto;
}}
.plan, .side {{
  min-width: 0;
}}
.plan-block {{
  position: relative;
  margin-bottom: 12px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}}
.plan-block.has-note {{
  border-color: #d7a900;
  background: var(--note);
}}
.block-tools {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--muted);
  font-size: 12px;
}}
.block-id {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
.mark {{ display: none; color: #8a5a00; }}
.has-note .mark {{ display: inline; }}
button {{
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
  font: inherit;
  padding: 6px 10px;
}}
button.primary {{
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
}}
button:hover {{ filter: brightness(0.97); }}
.block-content > :first-child {{ margin-top: 0; }}
.block-content > :last-child {{ margin-bottom: 0; }}
pre {{
  margin: 0;
  padding: 12px;
  overflow: auto;
  border-radius: 6px;
  background: #15191f;
  color: #f4f7fb;
}}
code {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
}}
.annotation, #global-notes, #prompt-output {{
  width: 100%;
  min-height: 74px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px;
  font: inherit;
}}
.annotation {{
  margin-top: 10px;
}}
.side {{
  position: sticky;
  top: 12px;
  align-self: start;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}}
.side h2 {{
  margin: 0 0 10px;
  font-size: 18px;
}}
.side label {{
  display: block;
  margin: 12px 0 6px;
  font-weight: 600;
}}
.actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}}
#prompt-output {{
  min-height: 220px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
}}
.status {{
  min-height: 20px;
  color: var(--muted);
  font-size: 13px;
}}
@media (max-width: 900px) {{
  main {{ grid-template-columns: 1fr; }}
  .side {{ position: static; }}
}}
</style>
</head>
<body>
<header>
  <h1>{title_text}</h1>
</header>
<main>
  <div class="plan">
    {''.join(rendered_blocks)}
  </div>
  <aside class="side">
    <h2>Annotations</h2>
    <label for="global-notes">Overall notes</label>
    <textarea id="global-notes" placeholder="Notes about the whole plan"></textarea>
    <div class="actions">
      <button type="button" class="primary" id="copy-prompt">Copy Prompt</button>
      <button type="button" id="download-prompt">Download Prompt</button>
      <button type="button" id="clear-notes">Clear</button>
    </div>
    <label for="prompt-output">Generated prompt</label>
    <textarea id="prompt-output" readonly></textarea>
    <div class="status" id="status"></div>
  </aside>
</main>
<script type="application/json" id="block-data">{blocks_json}</script>
<script>
const storageKey = "annotate-plan:{plan_hash}";
const blocks = JSON.parse(document.getElementById("block-data").textContent);
const globalNotes = document.getElementById("global-notes");
const promptOutput = document.getElementById("prompt-output");
const statusEl = document.getElementById("status");

function loadState() {{
  try {{
    return JSON.parse(localStorage.getItem(storageKey)) || {{ global: "", notes: {{}} }};
  }} catch {{
    return {{ global: "", notes: {{}} }};
  }}
}}

let state = loadState();

function saveState() {{
  localStorage.setItem(storageKey, JSON.stringify(state));
  refreshPrompt();
}}

function setStatus(message) {{
  statusEl.textContent = message;
  if (message) {{
    setTimeout(() => {{
      if (statusEl.textContent === message) statusEl.textContent = "";
    }}, 1800);
  }}
}}

function noteFor(blockId) {{
  return document.querySelector(`[data-note="${{blockId}}"]`);
}}

function updateMarkers() {{
  for (const block of blocks) {{
    const value = (state.notes[block.id] || "").trim();
    document.getElementById(block.id).classList.toggle("has-note", Boolean(value));
  }}
}}

function buildPrompt() {{
  const lines = ["Please revise the plan using these annotations.", ""];
  const overall = (state.global || "").trim();
  lines.push("Overall notes:");
  lines.push(overall || "(none)");
  lines.push("", "Section annotations:");

  let count = 0;
  for (const block of blocks) {{
    const annotation = (state.notes[block.id] || "").trim();
    if (!annotation) continue;
    count += 1;
    lines.push(`${{count}}. "${{block.preview}}"`);
    lines.push(`   Annotation: ${{annotation}}`);
    lines.push("");
  }}

  if (!count) lines.push("(none)", "");
  lines.push("Keep unchanged parts of the plan unless an annotation asks for a change.");
  return lines.join("\\n");
}}

function refreshPrompt() {{
  updateMarkers();
  promptOutput.value = buildPrompt();
}}

globalNotes.value = state.global || "";
globalNotes.addEventListener("input", () => {{
  state.global = globalNotes.value;
  saveState();
}});

for (const block of blocks) {{
  const textarea = noteFor(block.id);
  textarea.value = state.notes[block.id] || "";
  textarea.addEventListener("input", () => {{
    state.notes[block.id] = textarea.value;
    saveState();
  }});
}}

document.addEventListener("click", (event) => {{
  const button = event.target.closest("[data-annotate]");
  if (!button) return;
  const textarea = noteFor(button.dataset.annotate);
  textarea.focus();
  textarea.scrollIntoView({{ block: "center", behavior: "smooth" }});
}});

document.getElementById("copy-prompt").addEventListener("click", async () => {{
  refreshPrompt();
  try {{
    await navigator.clipboard.writeText(promptOutput.value);
    setStatus("Prompt copied.");
  }} catch {{
    promptOutput.focus();
    promptOutput.select();
    document.execCommand("copy");
    setStatus("Prompt selected.");
  }}
}});

document.getElementById("download-prompt").addEventListener("click", () => {{
  refreshPrompt();
  const blob = new Blob([promptOutput.value], {{ type: "text/plain" }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "plan-annotations-prompt.txt";
  link.click();
  URL.revokeObjectURL(url);
  setStatus("Prompt downloaded.");
}});

document.getElementById("clear-notes").addEventListener("click", () => {{
  state = {{ global: "", notes: {{}} }};
  localStorage.removeItem(storageKey);
  globalNotes.value = "";
  for (const block of blocks) noteFor(block.id).value = "";
  refreshPrompt();
  setStatus("Annotations cleared.");
}});

refreshPrompt();
</script>
</body>
</html>
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Render a plan as annotatable static HTML.")
    parser.add_argument("--input", required=True, help="Markdown plan file to render")
    parser.add_argument("--output", required=True, help="HTML output path")
    parser.add_argument("--title", default="Plan Review", help="HTML page title")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        markdown = input_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: could not read {input_path}: {exc}", file=sys.stderr)
        return 1

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(build_html(markdown, args.title), encoding="utf-8")
    except OSError as exc:
        print(f"error: could not write {output_path}: {exc}", file=sys.stderr)
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
