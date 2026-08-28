#!/usr/bin/env python3
"""Pre-push validator for the academic website.

Catches the breakages that actually happen when editing this site by hand,
without needing Ruby or any third-party package:

  1. Front matter present and closed in index.md
  2. Every nav anchor in _data/navigation.yml resolves to a heading in index.md
  3. Every local file referenced from index.md / _config.yml exists on disk
  4. Every PDF in the repo root is referenced from index.md (no orphans)
  5. <details>, <div> and <span> tags in index.md are balanced
  6. Paper entries keep kramdown's "tight list" rule -- no blank line before
     the <div class="paper-actions"> or bare <details>, which would otherwise
     wrap the item in <p> and invalidly nest a block element inside it
  7. Abstract entries carry the markup the conventions in CLAUDE.md require:
     the toggle first, the PDF link second, and the abstract text in a
     sibling <span class="abstract-text">

Usage:  python .claude/scripts/site_check.py
Exit code 0 = safe to push, 1 = problems found.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

problems = []
notes = []


def fail(msg):
    problems.append(msg)


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        fail("missing file: %s" % rel)
        return ""
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n")


index = read("index.md")
config = read("_config.yml")
nav = read("_data/navigation.yml")

# --- 1. front matter -------------------------------------------------------
if not index.startswith("---\n"):
    fail("index.md does not start with YAML front matter")
elif index.count("\n---\n") < 1:
    fail("index.md front matter is not closed")

# --- 2. nav anchors resolve ------------------------------------------------
anchors = set(re.findall(r"\{#([a-z0-9-]+)\}", index))
nav_urls = re.findall(r'url:\s*"?/#([a-z0-9-]+)', nav)
for a in sorted(set(nav_urls)):
    if a not in anchors:
        fail("nav anchor /#%s has no matching heading in index.md" % a)
notes.append("%d nav anchors checked against %d headings" % (len(set(nav_urls)), len(anchors)))

# --- 3. referenced local files exist ---------------------------------------
refs = set()
for text in (index, config):
    refs |= set(re.findall(r'["\(](/[A-Za-z0-9_.\-]+\.(?:pdf|jpg|jpeg|png|gif|svg))', text))
for ref in sorted(refs):
    if not os.path.exists(os.path.join(ROOT, ref.lstrip("/"))):
        fail("referenced file does not exist: %s" % ref)
notes.append("%d referenced local files checked" % len(refs))

# --- 4. no orphan PDFs in the repo root ------------------------------------
root_pdfs = sorted(f for f in os.listdir(ROOT) if f.lower().endswith(".pdf"))
for pdf in root_pdfs:
    if ("/" + pdf) not in refs:
        fail("PDF in repo root is not linked from index.md (orphan?): %s" % pdf)
notes.append("%d root PDFs, all linked" % len(root_pdfs))

# --- 5. balanced tags ------------------------------------------------------
body = index.split("\n---\n", 1)[-1]
for tag in ("details", "div", "span"):
    opens = len(re.findall(r"<%s[\s>]" % tag, body))
    closes = len(re.findall(r"</%s>" % tag, body))
    if opens != closes:
        fail("unbalanced <%s>: %d opened, %d closed" % (tag, opens, closes))
notes.append("details/div/span tags balanced")

# --- 6. tight-list rule ----------------------------------------------------
lines = body.split("\n")
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("<div class=\"paper-actions\"") or stripped.startswith("<details"):
        if i > 0 and lines[i - 1].strip() == "":
            fail("line %d: blank line before %s breaks kramdown's tight-list rule "
                 "(the item gets wrapped in <p>)" % (i + 1, stripped[:34]))

# --- 7. abstract markup conventions ----------------------------------------
rows = list(re.finditer(r'<div class="paper-actions">(.*?)</div>', body, re.S))
for m in rows:
    row = m.group(1)
    if "\n" in row:
        fail("a paper-actions row spans several lines; it must stay on one line")
    if not row.startswith('<details class="abstract"'):
        fail("a paper-actions row does not start with the abstract toggle; the "
             "toggle must come first so every abstract on the page lines up, "
             "including entries that have no PDF")
    if '<span class="abstract-text">' not in row:
        fail("a paper-actions row has no <span class=\"abstract-text\"> body")
    if row.count("<details") != 1:
        fail("a paper-actions row does not hold exactly one <details> abstract")

n_open = len(re.findall(r'<details class="abstract" open>', body))
notes.append("%d paper-action rows, %d expanded by default" % (len(rows), n_open))

# the <details> carries the summary only -- the body is its sibling, which is
# what keeps the toggle button-width while the text spans the full row
for m in re.finditer(r'<details class="abstract"(?: open)?>(.*?)</details>', body, re.S):
    if m.group(1) != "<summary>Abstract</summary>":
        fail("a <details class=\"abstract\"> holds more than <summary>Abstract</summary>; "
             "the abstract text belongs in the sibling <span class=\"abstract-text\">")

for m in re.finditer(r'<span class="abstract-text">(.*?)</span>', body, re.S):
    if "\n" in m.group(1):
        fail("an abstract spans several lines; it must stay on one line")

# every abstract must sit inside an action row -- a bare <details> would not line
# up with the others
if len(re.findall(r"<details", body)) != len(rows):
    fail("a <details> abstract sits outside a <div class=\"paper-actions\"> row")

# --- report ----------------------------------------------------------------
print("Site check: %s" % ROOT)
for n in notes:
    print("  - %s" % n)
if problems:
    print("\n%d problem(s):" % len(problems))
    for p in problems:
        print("  ! %s" % p)
    sys.exit(1)
print("\nAll checks pass.")
sys.exit(0)
