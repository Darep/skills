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
            <div class="annotatable" id="{block_id}" data-block-id="{block_id}">
              <button class="add-note" type="button" data-annotate="{block_id}" aria-label="Annotate this block">+</button>
              <span class="note-mark" aria-label="Annotated">note</span>
              {render_block(block)}
            </div>
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
  --bg: #f3f4f0;
  --panel: #ffffff;
  --ink: #1f2933;
  --muted: #667085;
  --line: #d6d8dc;
  --accent: #0f766e;
  --accent-ink: #ffffff;
  --note: #fff8d8;
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
  gap: 22px;
  padding: 22px;
  max-width: 1260px;
  margin: 0 auto;
}}
.plan, .side {{
  min-width: 0;
}}
.document {{
  padding: 34px clamp(22px, 4vw, 54px);
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
  box-shadow: 0 18px 50px rgba(31, 41, 51, 0.08);
}}
.annotatable {{
  position: relative;
  margin: 0 0 18px;
  padding: 2px 34px 2px 0;
  border-radius: 6px;
}}
.annotatable:hover,
.annotatable.selected {{
  background: #f7fbfa;
}}
.annotatable.has-note {{
  background: var(--note);
}}
.add-note {{
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 1px solid var(--accent);
  border-radius: 999px;
  background: var(--accent);
  color: var(--accent-ink);
  cursor: pointer;
  font: 700 17px/1 system-ui, sans-serif;
  opacity: 0;
  transform: scale(0.9);
  transition: opacity 120ms ease, transform 120ms ease;
}}
.annotatable:hover .add-note,
.annotatable.selected .add-note,
.add-note:focus {{
  opacity: 1;
  transform: scale(1);
}}
.note-mark {{
  position: absolute;
  top: 7px;
  right: 34px;
  display: none;
  color: #8a5a00;
  font-size: 12px;
  font-weight: 700;
}}
.has-note .note-mark {{ display: inline; }}
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
.annotatable > :first-child:not(button):not(.note-mark) {{ margin-top: 0; }}
.annotatable > :last-child {{ margin-bottom: 0; }}
.document h2,
.document h3,
.document h4,
.document h5,
.document h6 {{
  color: #15202b;
  line-height: 1.2;
}}
.document h2 {{ font-size: 28px; }}
.document h3 {{ font-size: 21px; margin-top: 24px; }}
.document p, .document li {{ color: #2f3a45; }}
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
#annotation-editor, #global-notes, #prompt-output {{
  width: 100%;
  min-height: 74px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px;
  font: inherit;
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
.selected-preview {{
  min-height: 42px;
  padding: 9px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #f8faf9;
  color: var(--muted);
  font-size: 13px;
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
@media (hover: none) {{
  .add-note {{ opacity: 1; transform: scale(1); }}
}}
</style>
</head>
<body>
<header>
  <h1>{title_text}</h1>
</header>
<main>
  <div class="plan">
    <article class="document">
    {''.join(rendered_blocks)}
    </article>
  </div>
  <aside class="side">
    <h2>Annotations</h2>
    <label for="annotation-editor">Selected block</label>
    <div class="selected-preview" id="selected-preview">Hover a plan element and press + to annotate it.</div>
    <textarea id="annotation-editor" placeholder="Annotation for the selected block" disabled></textarea>
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
const annotationEditor = document.getElementById("annotation-editor");
const selectedPreview = document.getElementById("selected-preview");
const promptOutput = document.getElementById("prompt-output");
const statusEl = document.getElementById("status");
let selectedBlockId = null;

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

function updateMarkers() {{
  for (const block of blocks) {{
    const value = (state.notes[block.id] || "").trim();
    const element = document.getElementById(block.id);
    element.classList.toggle("has-note", Boolean(value));
    element.classList.toggle("selected", block.id === selectedBlockId);
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

function selectBlock(blockId) {{
  const block = blocks.find((item) => item.id === blockId);
  selectedBlockId = blockId;
  selectedPreview.textContent = block ? block.preview : blockId;
  annotationEditor.disabled = false;
  annotationEditor.value = state.notes[blockId] || "";
  annotationEditor.focus();
  updateMarkers();
}}

globalNotes.value = state.global || "";
globalNotes.addEventListener("input", () => {{
  state.global = globalNotes.value;
  saveState();
}});

annotationEditor.addEventListener("input", () => {{
  if (!selectedBlockId) return;
  state.notes[selectedBlockId] = annotationEditor.value;
  saveState();
}});

document.addEventListener("click", (event) => {{
  const button = event.target.closest("[data-annotate]");
  if (!button) return;
  selectBlock(button.dataset.annotate);
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
  annotationEditor.value = "";
  selectedBlockId = null;
  annotationEditor.disabled = true;
  selectedPreview.textContent = "Hover a plan element and press + to annotate it.";
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
