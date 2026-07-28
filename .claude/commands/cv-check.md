---
description: Rules, structure, and design spec for the academic CV — check and verify every time the CV is touched
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# CV Standards — Moritz Seebacher

The authoritative spec for `CV_Academic_Moritz_Seebacher_MM_YY_English.docx` and its
exported PDF. **Read this before any CV edit and run the audit after every edit.**
The CV is a job-market document: it must be flawless, and every comparable element
must be formatted identically.

**Source of truth:** the `.docx` in the repo root (gitignored — local only).
**Published artefact:** the same-named `.pdf` (committed, served from the repo root).
**Never** hand-edit the PDF, and never let the two drift.

---

## The one-command check

```bash
cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/cv_audit.py
```

Exits 0 when every rule below passes, 1 with a numbered list of violations.
Rule IDs (`R1`…`R33`) in the output map to the sections here. If you change a
design rule, change it in **both** this file and `cv_audit.py`.

---

## 1. Page and typography

| Property | Value |
|---|---|
| Page | A4 (11906 × 16838 twips) |
| Margins | 851 twips (1.5 cm) left/right/top, 1134 (2 cm) bottom |
| Text width | **10204 twips** — every table must equal this |
| Font | **Arial throughout.** No exceptions, no theme fonts |
| Body size | 11 pt (`w:sz` 22) |
| Location lines | 10 pt (`w:sz` 20) — the only smaller text |
| Name | 28 pt (`w:sz` 56), centred |
| Date under name | 14 pt (`w:sz` 28), centred |

Only these four sizes may appear (`R16`). Every run pins its own font and size
explicitly (`R15`) — never rely on inherited defaults, which differ between Word
versions and would silently change the rendering.

---

## 2. Section headings

Fifteen sections, in this order (`R2`):

`Contact Information` · `Current Position` · `Education` · `Research Visits` ·
`Publications in Refereed Journals` · `Publications in Non-Refereed Journals` ·
`Working Papers` · `Work in Progress` · `Teaching Experience` ·
`Conferences and Workshops` · `Refereeing` · `Work Experience` ·
`Extracurricular Activities` · `Languages` · `Technical Skills`

Every heading is formatted **identically** (`R3`):

- Arial 11 pt **bold**
- `spacing before=240 after=80 line=240 lineRule=auto`
- `<w:keepNext/>` — a heading may never be orphaned at the foot of a page (`R4`)
- Rule = **paragraph bottom border**, `single`, `sz=4` (0.5 pt), `space=1`, `color=auto`

> **Never draw section rules as floating line shapes** (`R1`). The pre-2026 CV used
> 15 hand-placed `v:line` anchors whose offsets had drifted to 11.95–13.90 pt
> vertically and −1.55 to +0.95 pt horizontally, and two shared a duplicated shape
> ID. A paragraph border is pinned to its heading, spans exactly the text width, and
> survives any reflow.

Headings are **Title Case** (`R6`): capitalise every word except `a an the and or
in of for to on at by vs.` when not first. No leading or trailing whitespace, no
trailing tabs or space padding (`R5`).

---

## 3. Table geometry

All content sits in borderless tables. Two layouts only (`R10`):

- **Two-column** `2268 / 7936` — dated entries. Left = dates + location, right = content.
- **Full-width** `10204` — bibliography-style entries (publications, working papers,
  work in progress) that start flush at the left margin.

Every table (`R7`–`R9`):

- `tblW = 10204`, all `tblBorders` = `none`
- `tblInd = 0` **and** `tblCellMar left = 0` — together these make cell text start
  exactly at the left margin, aligned with the heading text and the start of its rule.
  Word's default 108-twip cell margin would push content 0.19 cm right of the rule.
- `tblCellMar right = 108`

Every row:

- `<w:cantSplit/>` (`R11`) — an entry never breaks across a page boundary.
- **No `<w:trHeight>`** (`R12`). Row height is content-driven. The pre-2026 CV forced a
  1.00 cm minimum on every row, so one-line entries got ~0.45 cm of dead padding while
  two-line entries got none — the visibly uneven gaps in Conferences and Refereeing.

---

## 4. Paragraph spacing

Exactly five spacing specs are permitted document-wide (`R13`). Every paragraph
declares its spacing explicitly (`R14`).

| Where | Spec |
|---|---|
| All table/body paragraphs | `after=80 line=276 lineRule=auto` |
| Section headings | `before=240 after=80 line=240 lineRule=auto` |
| Name | `before=480 after=80 line=240 lineRule=auto` |
| Date under name | `after=160 line=240 lineRule=auto` |
| Closing place/date line | `before=360 after=0 line=240 lineRule=auto` |

Bullets use the `Listenabsatz` (List Paragraph) style with `numId 12` — Symbol `•`,
`ind left=720 hanging=360`. That style carries `contextualSpacing`, so consecutive
bullets sit tight as a group while still spacing away from the next entry. Never
type a literal `•` character with a manual indent.

---

## 5. Entry patterns

**Two-column dated entry:**

```
LEFT                          RIGHT
10/2022 – present             **Junior Economist**            <- bold, 11pt
Munich, Germany   (10pt)      ifo Center for the …            <- plain, 11pt
                              • bullet                        <- optional
```

Two separate spells in one role: stack the ranges as two paragraphs in the left
column, most recent first — never join them with a comma on one wrapped line.

**Full-width bibliography entry:**

```
**Title in Bold**, *Journal or Series in Italics*, locator, year
**Title in Bold** (with A, B, and C), *Series*, No. NNNNN, year
```

Title **bold**; journal/series *italic*; everything else roman. Coauthors in
parentheses directly after the title, with a serial (Oxford) comma and `and` (`R29`).

**Paper titles are never hyperlinked** (`R34`). The contact email is the only link in
the document. Before the 2026 polish exactly one of four titles carried a link, which
made that entry read as the important one; linking all four was considered and
rejected. Plain text keeps every entry visually equal and keeps the printed PDF —
which is how a CV is usually read — from losing information.

---

## 6. Text conventions

| Rule | Requirement | ID |
|---|---|---|
| Ranges | **En dash `–` with spaces**, never a hyphen or em dash | `R20`, `R23` |
| Date format | `MM/YYYY – MM/YYYY` or `MM/YYYY – present` | `R24` |
| Ongoing roles | `present` — never `today`, `now`, `ongoing` | `R26` |
| Page ranges | En dash: `33–38` | `R23` |
| Locations | Always `City, Country` — the comma is mandatory | `R25` |
| Country | `U.S.` (with periods); `Washington, D.C., U.S.` | `R25` |
| Apostrophes | Curly `’` only | `R21` |
| Institution | `ifo` is always lowercase, even sentence-initial | `R27` |
| University | `LMU Munich` — not `Ludwig-Maximilians-University` | `R28` |
| Teaching | Every entry carries `(Bachelor)` or `(Master)` | `R30` |
| Conferences | Spell out `Verein für Socialpolitik`; `EEA`/`EALE`/`IAB` may stay abbreviated | — |
| Whitespace | No double spaces, no leading/trailing spaces, no manual tabs or line breaks inside a paragraph | `R17`–`R19` |
| Non-breaking spaces | Flagged as warnings — use only where a break would be genuinely bad | `R22` |

Set `w:lang="de-DE"` on German-language runs (the ifo Schnelldienst title) and
`en-US` everywhere else, so spell-check does not litter the source with false errors.

---

## 7. Editing workflow

1. **Edit** `CV_Academic_Moritz_Seebacher_MM_YY_English.docx` (Word, or by rebuilding
   `word/document.xml`). Keep the header date and the closing `Munich, <date>` line
   in sync with the actual revision date.
2. **Export to PDF** — same basename, `.pdf`:
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass \
     -File .claude/scripts/cv_to_pdf.ps1 \
     -In "<abs path>.docx" -Out "<abs path>.pdf"
   ```
3. **Audit**: `python .claude/scripts/cv_audit.py` — must exit 0.
4. **Read the PDF back** page by page and look at it. The audit catches structure;
   only your eyes catch a bad line break, a widow, or a lopsided page.
5. **If the month changed**, rename both files to the new `MM_YY`, update the link in
   `index.md`, and `git rm` the old PDF so only one is served.
6. **Publish** with `/update-website`.

Do not commit the `.docx` — `.gitignore` excludes `*.docx` by design.

---

## 8. Consistency with the website

`index.md` and the CV must agree (`R32`):

- The linked PDF filename must exist on disk and be the current one.
- Citations use the same order in both: **`Journal, volume(issue), locator, year.`**
- Coauthor lists use the serial comma and `and` in both.
- Only one `CV_Academic_*.pdf` lives in the repo (`R33`).

**Verified bibliographic facts** (re-check before changing them):

- *Pathways to Progress…* — Economics of Education Review, **97, 102483, 2023**.
  Article-number journal; there is **no page range**. DOI `10.1016/j.econedurev.2023.102483`.
- *Wie Fahrräder…* — ifo Schnelldienst, **77(3), 33–38, 2024**.
- *Multidimensional Skills on LinkedIn Profiles…* — **IZA Discussion Paper No. 17896, May 2025**;
  authors David Dorn, Florian Schoner, Moritz Seebacher, Lisa Simon, Ludger Woessmann.

---

## 9. Deliberate design choices (do not "fix" these)

- **Current Position before Education.** A German-convention ordering the CV keeps.
- **Awards nested under Education** as bullets rather than a separate Awards section.
- **Both a header date and a closing `Munich, <date>` line.** Header carries month +
  year, the closing line the full revision date.
- **Contact, Languages and Technical Skills use the two-column layout with an empty
  left cell**, so their content aligns with the dated sections above them.
- **`(Bachelor)` appears on thesis-supervision entries** even though the line below
  says "Supervisor of bachelor thesis" — the redundancy keeps every teaching entry
  parallel.

## 10. Known open items

- No **References** section. Standard on a job-market CV; add before applications.
- No **Research Fields** line, though `index.md` lists Labor Economics · Economics of
  Education.
- **Stacked date ranges** (YES!, Tintenklecks) put the second range beside the role's
  second line, which can read as if it belongs to that line. No better option exists
  in a two-column layout; revisit only if the layout changes.
