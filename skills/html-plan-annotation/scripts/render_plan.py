#!/usr/bin/env python3
import argparse
import hashlib
import html
import http.server
import json
import re
import sys
import tempfile
from functools import partial
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


def infer_title(markdown):
    for line in markdown.splitlines():
        match = HEADING_RE.match(line)
        if match:
            return match.group(2)
    return "Plan Review"


def build_html(markdown):
    blocks = split_blocks(markdown)
    title = infer_title(markdown)
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
              <button class="note-mark" type="button" data-annotate="{block_id}" aria-label="Edit annotation">✎</button>
              <div class="block-body">{render_block(block)}</div>
              <button class="add-note" type="button" data-annotate="{block_id}" aria-label="Annotate this block">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
              </button>
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
  color-scheme: light dark;
  --bg: #eef0f4;
  --bg-grad: radial-gradient(1200px 600px at 100% -10%, #e7ecf6 0%, transparent 60%), radial-gradient(900px 500px at -10% 0%, #eaf3f0 0%, transparent 55%);
  --panel: #ffffff;
  --panel-2: #f7f8fb;
  --ink: #1a2230;
  --ink-soft: #3a4760;
  --muted: #6b7689;
  --line: #e2e5ec;
  --line-strong: #d2d7e0;
  --accent: #4f46e5;
  --accent-soft: #eef0fe;
  --accent-ink: #ffffff;
  --note: #f59e0b;
  --note-soft: #fff7e8;
  --shadow: 0 1px 2px rgba(16,24,40,.04), 0 12px 32px rgba(16,24,40,.06);
  --radius: 14px;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0d1017;
    --bg-grad: radial-gradient(1200px 600px at 100% -10%, #161b2b 0%, transparent 60%), radial-gradient(900px 500px at -10% 0%, #10211d 0%, transparent 55%);
    --panel: #14181f;
    --panel-2: #1a1f29;
    --ink: #e7eaf0;
    --ink-soft: #c2c9d6;
    --muted: #8893a7;
    --line: #262c38;
    --line-strong: #333a48;
    --accent: #7c79ff;
    --accent-soft: #1d1f3a;
    --note: #f6b73c;
    --note-soft: #2a2113;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 16px 40px rgba(0,0,0,.45);
  }}
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--bg-grad), var(--bg);
  background-attachment: fixed;
  color: var(--ink);
  font: 15px/1.65 -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
header {{
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px clamp(18px, 4vw, 40px);
  border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel) 80%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
}}
.brand-dot {{
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
  flex: none;
}}
.titles {{ min-width: 0; flex: 1; }}
h1 {{
  margin: 0;
  font-size: clamp(17px, 2.4vw, 21px);
  font-weight: 650;
  letter-spacing: -.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.subtitle {{ margin: 1px 0 0; font-size: 12.5px; color: var(--muted); }}
.count-chip {{
  flex: none;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 11px;
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  background: var(--panel-2);
  color: var(--ink-soft);
  font-size: 12.5px; font-weight: 600;
  font-variant-numeric: tabular-nums;
}}
.count-chip b {{ color: var(--accent); }}
main {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 26px;
  padding: clamp(18px, 3vw, 32px) clamp(16px, 4vw, 40px) 64px;
  max-width: 1320px;
  margin: 0 auto;
}}
.plan, .side {{ min-width: 0; }}
.document {{
  padding: clamp(26px, 4vw, 56px) clamp(22px, 4.5vw, 64px);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--panel);
  box-shadow: var(--shadow);
}}
.annotatable {{
  position: relative;
  margin: 2px 0;
  padding: 8px 44px 8px 16px;
  border-radius: 10px;
  border: 1px solid transparent;
  transition: background 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
}}
.annotatable::before {{
  content: "";
  position: absolute;
  left: 4px; top: 10px; bottom: 10px;
  width: 3px;
  border-radius: 3px;
  background: transparent;
  transition: background 140ms ease;
}}
.annotatable:hover {{
  background: var(--panel-2);
  border-color: var(--line);
}}
.annotatable.open {{
  background: var(--accent-soft);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 12%, transparent);
}}
.annotatable.open::before {{ background: var(--accent); }}
.annotatable.has-note {{ background: var(--note-soft); }}
.annotatable.has-note::before {{ background: var(--note); }}
.annotatable.has-note.open {{
  background: color-mix(in srgb, var(--accent-soft) 70%, var(--note-soft));
}}
.add-note {{
  position: absolute;
  top: 8px;
  right: 8px;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
  border-radius: 9px;
  background: var(--panel);
  color: var(--accent);
  cursor: pointer;
  opacity: 0;
  transform: translateY(-2px) scale(.92);
  transition: opacity 130ms ease, transform 130ms ease, background 130ms ease, color 130ms ease;
}}
.annotatable:hover .add-note,
.add-note:focus-visible {{
  opacity: 1;
  transform: translateY(0) scale(1);
}}
.add-note:hover {{ background: var(--accent); color: var(--accent-ink); }}
.note-mark {{
  position: absolute;
  top: 8px;
  right: 8px;
  display: none;
  place-items: center;
  width: 28px; height: 28px;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--note) 50%, transparent);
  border-radius: 9px;
  background: var(--note);
  color: #3a2400;
  font-size: 14px;
  cursor: pointer;
}}
.note-mark:hover {{ filter: brightness(.96); }}
.has-note .note-mark {{ display: grid; }}
.has-note .add-note {{ display: none; }}
.annotatable.open {{ z-index: 30; }}
.annotatable.open .add-note,
.annotatable.open .note-mark {{ opacity: 1; transform: none; background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }}
.popover {{
  position: absolute;
  top: 6px;
  right: 44px;
  width: min(320px, calc(100% - 56px));
  z-index: 40;
  padding: 12px;
  border: 1px solid var(--line-strong);
  border-radius: 12px;
  background: var(--panel);
  box-shadow: 0 12px 28px rgba(16,24,40,.18), 0 2px 6px rgba(16,24,40,.10);
  animation: pop 120ms ease;
}}
@media (prefers-color-scheme: dark) {{
  .popover {{ box-shadow: 0 16px 40px rgba(0,0,0,.6); }}
}}
@keyframes pop {{ from {{ opacity: 0; transform: translateY(-4px) scale(.98); }} to {{ opacity: 1; transform: none; }} }}
.popover-head {{
  display: flex; align-items: baseline; gap: 8px;
  margin-bottom: 8px;
  font-size: 11.5px; font-weight: 600; letter-spacing: .03em; text-transform: uppercase;
  color: var(--muted);
}}
.popover-head .ann-label {{
  flex: 1; min-width: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  text-transform: none; letter-spacing: 0; font-weight: 600; font-size: 12.5px;
  color: var(--ink-soft);
}}
.popover textarea {{ min-height: 72px; margin: 0; }}
.popover-actions {{ display: flex; gap: 8px; margin-top: 9px; }}
.popover-actions .done {{ flex: 1; justify-content: center; }}
.popover-actions button {{ padding: 7px 11px; font-size: 13px; }}
.btn-danger {{ color: #b42318; border-color: color-mix(in srgb, #b42318 30%, var(--line-strong)); }}
.btn-danger:hover {{ background: #fef3f2; }}
@media (prefers-color-scheme: dark) {{ .btn-danger {{ color: #ff8a7a; }} .btn-danger:hover {{ background: #2a1614; }} }}
@media (max-width: 920px) {{
  .popover {{ right: 8px; left: 8px; width: auto; }}
}}
.summary {{ display: flex; flex-direction: column; gap: 8px; margin-top: 4px; }}
.summary:empty::after {{
  content: "No annotations yet \2014 click + on any block.";
  color: var(--muted); font-size: 12.5px; font-style: italic;
}}
.summary-item {{
  text-align: left; width: 100%;
  display: block;
  padding: 9px 11px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel-2);
  cursor: pointer;
  font-weight: 500;
}}
.summary-item:hover {{ border-color: var(--line-strong); background: var(--panel); }}
.summary-item .si-block {{
  display: block;
  font-size: 11.5px; color: var(--accent); font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-bottom: 2px;
}}
.summary-item .si-note {{
  display: block;
  font-size: 13px; color: var(--ink-soft);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}}
.block-body > :first-child {{ margin-top: 0; }}
.block-body > :last-child {{ margin-bottom: 0; }}
.document h2, .document h3, .document h4, .document h5, .document h6 {{
  color: var(--ink);
  line-height: 1.25;
  letter-spacing: -.012em;
  font-weight: 650;
}}
.document h2 {{ font-size: clamp(22px, 3vw, 27px); margin: 6px 0 4px; }}
.document h3 {{ font-size: 19px; margin-top: 12px; }}
.document h4 {{ font-size: 16px; }}
.document p {{ color: var(--ink-soft); }}
.document li {{ color: var(--ink-soft); margin: 3px 0; }}
.document ul, .document ol {{ padding-left: 22px; }}
.document a {{ color: var(--accent); }}
.document hr {{ border: none; border-top: 1px solid var(--line); margin: 22px 0; }}
.document code {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
}}
.document p code, .document li code {{
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 5px;
  padding: 1px 5px;
  font-size: 12.5px;
}}
pre {{
  margin: 6px 0;
  padding: 16px 18px;
  overflow: auto;
  border-radius: 11px;
  background: #0f1320;
  border: 1px solid #1e2742;
  color: #e7ecfb;
  line-height: 1.55;
}}
pre code {{ font-size: 12.5px; color: inherit; }}
.side {{
  position: sticky;
  top: 80px;
  align-self: start;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--panel);
  box-shadow: var(--shadow);
  max-height: calc(100vh - 100px);
  overflow: auto;
}}
.side h2 {{
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 650;
  letter-spacing: -.01em;
}}
.side .hint {{ margin: 0 0 6px; font-size: 12.5px; color: var(--muted); }}
.side label {{
  display: block;
  margin: 16px 0 7px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .02em;
  text-transform: uppercase;
  color: var(--muted);
}}
textarea {{
  width: 100%;
  resize: vertical;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 11px 12px;
  font: inherit;
  color: var(--ink);
  background: var(--panel);
  transition: border-color 120ms ease, box-shadow 120ms ease;
}}
textarea::placeholder {{ color: var(--muted); }}
textarea:focus-visible {{
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
}}
textarea:disabled {{ background: var(--panel-2); color: var(--muted); cursor: not-allowed; }}
#global-notes {{ min-height: 84px; }}
#prompt-output {{
  min-height: 200px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12.5px;
  background: var(--panel-2);
}}
button {{
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: var(--panel);
  color: var(--ink);
  cursor: pointer;
  font: inherit; font-weight: 550;
  padding: 9px 13px;
  transition: background 120ms ease, border-color 120ms ease, transform 60ms ease, box-shadow 120ms ease;
}}
button:hover {{ background: var(--panel-2); }}
button:active {{ transform: translateY(1px); }}
button:focus-visible {{ outline: none; box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 22%, transparent); }}
button.primary {{
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
  box-shadow: 0 1px 2px color-mix(in srgb, var(--accent) 40%, transparent);
}}
button.primary:hover {{ background: color-mix(in srgb, var(--accent) 88%, #000); }}
.actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0 4px;
}}
.actions .primary {{ flex: 1; justify-content: center; }}
.status {{
  min-height: 18px;
  margin-top: 8px;
  color: var(--accent);
  font-size: 12.5px;
  font-weight: 550;
}}
.divider {{ height: 1px; background: var(--line); margin: 18px -2px 2px; }}
@media (max-width: 920px) {{
  main {{ grid-template-columns: 1fr; }}
  .side {{ position: static; max-height: none; }}
}}
@media (hover: none) {{
  .add-note {{ opacity: 1; transform: none; }}
}}
::selection {{ background: color-mix(in srgb, var(--accent) 28%, transparent); }}
</style>
</head>
<body>
<header>
  <span class="brand-dot"></span>
  <div class="titles">
    <h1>{title_text}</h1>
    <p class="subtitle">Plan review &middot; hover a section and click + to annotate</p>
  </div>
  <span class="count-chip"><b id="note-count">0</b>&nbsp;annotations</span>
</header>
<main>
  <div class="plan">
    <article class="document">
    {''.join(rendered_blocks)}
    </article>
  </div>
  <aside class="side">
    <h2>Annotations</h2>
    <p class="hint">Stored in your browser only.</p>
    <label>Per-block comments</label>
    <div class="summary" id="summary"></div>
    <label for="global-notes">Overall notes</label>
    <textarea id="global-notes" placeholder="Notes about the whole plan"></textarea>
    <div class="actions">
      <button type="button" class="primary" id="copy-prompt">Copy prompt</button>
      <button type="button" id="download-prompt">Download</button>
      <button type="button" id="clear-notes">Clear</button>
    </div>
    <div class="divider"></div>
    <label for="prompt-output">Generated prompt</label>
    <textarea id="prompt-output" readonly></textarea>
    <div class="status" id="status"></div>
  </aside>
</main>
<div class="popover" id="popover" hidden>
  <div class="popover-head"><span class="ann-label" id="popover-label"></span></div>
  <textarea id="popover-text" placeholder="What should change about this block?"></textarea>
  <div class="popover-actions">
    <button type="button" class="primary done" id="popover-done">Done</button>
    <button type="button" class="btn-danger" id="popover-remove">Remove</button>
  </div>
</div>
<script type="application/json" id="block-data">{blocks_json}</script>
<script>
const storageKey = "annotate-plan:{plan_hash}";
const blocks = JSON.parse(document.getElementById("block-data").textContent);
const globalNotes = document.getElementById("global-notes");
const promptOutput = document.getElementById("prompt-output");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const popover = document.getElementById("popover");
const popoverLabel = document.getElementById("popover-label");
const popoverText = document.getElementById("popover-text");
let openBlockId = null;

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

const noteCountEl = document.getElementById("note-count");

function updateMarkers() {{
  let count = 0;
  for (const block of blocks) {{
    const value = (state.notes[block.id] || "").trim();
    const element = document.getElementById(block.id);
    if (value) count += 1;
    element.classList.toggle("has-note", Boolean(value));
  }}
  noteCountEl.textContent = String(count);
  renderSummary();
}}

function renderSummary() {{
  summaryEl.textContent = "";
  for (const block of blocks) {{
    const note = (state.notes[block.id] || "").trim();
    if (!note) continue;
    const item = document.createElement("button");
    item.type = "button";
    item.className = "summary-item";
    item.dataset.annotate = block.id;
    const blk = document.createElement("span");
    blk.className = "si-block";
    blk.textContent = block.preview;
    const txt = document.createElement("span");
    txt.className = "si-note";
    txt.textContent = note;
    item.append(blk, txt);
    summaryEl.appendChild(item);
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

function openPopover(blockId) {{
  const block = blocks.find((item) => item.id === blockId);
  const element = document.getElementById(blockId);
  if (!element) return;
  closePopover();
  openBlockId = blockId;
  element.classList.add("open");
  element.appendChild(popover);
  popoverLabel.textContent = block ? block.preview : blockId;
  popoverText.value = state.notes[blockId] || "";
  popover.hidden = false;
  popoverText.focus();
  popoverText.setSelectionRange(popoverText.value.length, popoverText.value.length);
  // Keep the popover on screen if the block sits at the top edge.
  element.scrollIntoView({{ block: "nearest" }});
}}

function closePopover() {{
  if (!openBlockId) return;
  const element = document.getElementById(openBlockId);
  if (element) element.classList.remove("open");
  popover.hidden = true;
  document.body.appendChild(popover);
  openBlockId = null;
}}

globalNotes.value = state.global || "";
globalNotes.addEventListener("input", () => {{
  state.global = globalNotes.value;
  saveState();
}});

popoverText.addEventListener("input", () => {{
  if (!openBlockId) return;
  state.notes[openBlockId] = popoverText.value;
  saveState();
}});

document.getElementById("popover-done").addEventListener("click", closePopover);
document.getElementById("popover-remove").addEventListener("click", () => {{
  if (openBlockId) delete state.notes[openBlockId];
  closePopover();
  saveState();
  setStatus("Annotation removed.");
}});

document.addEventListener("click", (event) => {{
  const trigger = event.target.closest("[data-annotate]");
  if (trigger) {{
    const id = trigger.dataset.annotate;
    if (id === openBlockId) closePopover();
    else openPopover(id);
    return;
  }}
  if (openBlockId && !event.target.closest("#popover")) closePopover();
}});

document.addEventListener("keydown", (event) => {{
  if (event.key === "Escape") closePopover();
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
  closePopover();
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
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--output", help="HTML output path")
    target.add_argument("--serve", action="store_true", help="Render and serve a temporary HTML page")
    parser.add_argument("--port", type=int, help="Port for --serve")
    args = parser.parse_args()
    if args.port is not None and not args.serve:
        parser.error("--port requires --serve")
    if args.port is None:
        args.port = 8765
    return args


def write_html(markdown, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(markdown), encoding="utf-8")


def serve(markdown, port):
    with tempfile.TemporaryDirectory(prefix="annotate-plan-") as directory:
        output_path = Path(directory) / "plan.html"
        write_html(markdown, output_path)
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=directory)
        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        except OSError as exc:
            print(f"error: could not serve on port {port}: {exc}", file=sys.stderr)
            return 1

        url = f"http://127.0.0.1:{port}/plan.html"
        print(url, flush=True)
        print("Press Ctrl-C to stop.", file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
        finally:
            server.server_close()
    return 0


def main():
    args = parse_args()
    input_path = Path(args.input)

    try:
        markdown = input_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: could not read {input_path}: {exc}", file=sys.stderr)
        return 1

    if args.serve:
        return serve(markdown, args.port)

    output_path = Path(args.output)
    try:
        write_html(markdown, output_path)
    except OSError as exc:
        print(f"error: could not write {output_path}: {exc}", file=sys.stderr)
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
