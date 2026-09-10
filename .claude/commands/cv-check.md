---
description: Rules, structure, and design spec for the academic CV — check and verify every time the CV is touched
allowed-tools: Bash, Read, Edit, Glob, Grep
---

# CV Standards — Moritz Seebacher

The authoritative spec for the CV. **Read this before any CV edit and run the audit after
every edit.** The CV is a job-market document: it must be flawless, and every comparable
element must be formatted identically.

**Source of truth:** `tex/cv.tex` in the application package, which lives outside this
repository with the rest of the job market material. **Never** hand-edit a PDF.

**Superseded 10 September 2026.** The CV used to be a Word document in this repo root,
exported by hand. Everything about fonts, table grids, row heights and paragraph spacing
that used to be in this file is gone: those rules existed because Word will silently break
any of them, and LaTeX cannot. What is left is the part LaTeX cannot check — what the CV
says, and whether it still agrees with the website.

---

## One source, two builds

| Build | Output | References section |
|---|---|---|
| `.\build.ps1 core` | `pdf\Seebacher_CV.pdf` | **Yes** — the four letter writers with email addresses |
| `.\build.ps1 web` | the dated `CV_Academic_*.pdf` in this repo root | **No** |

The website build defines `\publicCV`, which drops the References section. Everything above
it is identical in both by construction, so the committee copy and the public copy cannot
drift. Referee contact details never go on the public site.

The `web` command also deletes the superseded dated PDF from this repo and relinks
`index.md` when the month has rolled over, so only one CV is ever served.

## The one-command check

```bash
cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/cv_audit.py
```

Exits 0 when every rule below passes, 1 with a numbered list of violations. It reads the
published PDF through `pdftotext`; if `pdftotext` is missing it **blocks** rather than
passing unverified. Rule IDs map to the sections here. If you change a rule, change it in
**both** this file and `cv_audit.py`.

---

## 1. Sections

Sixteen sections, in this order (`R2`):

`Fields` · `Current Position` · `Education` · `Research Visits` · `Job Market Paper` ·
`Publications` · `Working Papers` · `Work in Progress` · `Policy Publications` ·
`Conferences, Workshops, and Invited Seminars` · `Teaching Experience` ·
`Awards and Scholarships` · `Refereeing` · `Research Experience` ·
`Outreach and Volunteering` · `Skills`

The ordering is a **job-market CV**: fields and position first, research output
(JMP → publications → working papers → work in progress) before teaching and service, and
non-research history last. Policy work sits *below* the academic output, never above it.

Contact details are the masthead under the name, not a section. `Skills` carries `Languages`
and `Technical` as row labels rather than two separate sections — the CV is kept compact
(Moritz, 10 Sep 2026).

---

## 2. Entry patterns

Three macros, defined in `cv.tex`:

| Macro | Use |
|---|---|
| `\cventry{date}{body}` | a dated entry — narrow date column, wide body column |
| `\cvplain{body}` | an undated entry that still aligns with the dated ones |
| `\cvpaper{title}{outlet}{abstract}` | a paper; outlet and abstract are both optional |

**Dated entry:** the body's first line is the role or title, **in bold in every section**;
subsequent lines are detail and take **no date of their own**. A date beside a detail line
makes the entry read as two entries — this is what went wrong with the YES! entry and why it
now carries one date cell (`2024, 2025`) over a bold title line and an undated detail line.

Two separate spells in one role stack the ranges in the date column, most recent first — but
only where the body is a single line, for the same reason.

**Paper entry:** title bold, outlet line small, abstract in `\footnotesize`. Every paper
carries an abstract, work in progress included (restored 10 Sep 2026, matching the website);
**policy publications do not**, also matching the website. Omitting either the outlet or the
abstract must not leave a blank line behind, which is why `\cvpaper` guards both.

**Coauthors are never bold and never smaller than the title.** `\coauthors` is redefined in
`cv.tex` to reset to `\normalfont`, because `\cvpaper` sets its title in bold and the group
would otherwise inherit it. Before 10 Sep 2026 the working paper's coauthors were bold while
the work-in-progress entry's were not. The website shows coauthors as plain text after the
linked title; the CV now matches.

Every abstract must be **verbatim** identical to the website (`R38`), never paraphrased. The
audit checks all four.

**Paper titles are never hyperlinked.** The contact email is the only link in the document
(`R34`). Plain text keeps every entry visually equal and keeps the printed PDF, which is how
a CV is usually read, from losing information.

---

## 3. Text conventions

| Rule | Requirement | ID |
|---|---|---|
| Ranges | **En dash `--` in the source**, never a hyphen or em dash | `R20`, `R23` |
| Date format | `MM/YYYY -- MM/YYYY` or `MM/YYYY -- present`; bare years for one-off events | `R24` |
| Ongoing roles | `present` — never `today`, `now`, `ongoing` | `R26` |
| Institution | `ifo` is always lowercase, even sentence-initial | `R27` |
| University | `LMU Munich` — not `Ludwig-Maximilians-University` | `R28` |
| Coauthors | Serial (Oxford) comma and `and`, via `\coauthors{}` | `R29` |
| Teaching | Every entry carries `(Bachelor)` or `(Master)` | — |
| Conferences | Spell out `Verein für Socialpolitik`; `EEA-ESEM`/`EALE`/`IAB` may stay abbreviated | — |
| Lists | **Commas only.** No semicolons | — |
| Emails | Only `seebacher@ifo.de` may appear in the published copy | `R34` |

**Conferences that have happened move out of the `(scheduled)` row.** The scheduled row sits
at the top of the section and holds only events still ahead; past events for the same year go
in the plain year row below it. Check this whenever a conference date passes.

---

## 4. Editing workflow

1. **Edit** `tex/cv.tex` in the application package. Facts that repeat across documents live
   in `personal.tex`, never inline.
2. **Build both**: `.\build.ps1 core` and `.\build.ps1 web`.
3. **Audit**: `python .claude/scripts/cv_audit.py` — must exit 0.
4. **Read the PDF back** page by page and look at it. The audit catches consistency; only
   your eyes catch a bad line break, a widow, or a lopsided page.
5. **Publish** with `/update-website`.

---

## 5. Consistency with the website

`index.md` and the CV must agree (`R32`, `R37`):

- The linked PDF filename must exist on disk and be the current one, and only one
  `CV_Academic_*.pdf` may live in the repo (`R33`).
- The `**Fields:**` line and the CV's Fields section must list the same entries.
- Expected graduation must match.
- Every paper title on one side must be on the other, verbatim.
- The job market paper abstract must be verbatim in both (`R38`).

**Verified bibliographic facts** (re-check before changing them):

- *Pathways to Progress…* — Economics of Education Review, **97, 102483, 2023**.
  Article-number journal; there is **no page range**. DOI `10.1016/j.econedurev.2023.102483`.
- *Wie Fahrräder…* — ifo Schnelldienst, **77(3), 33–38, 2024**.
- *Multidimensional Skills on LinkedIn Profiles…* — **IZA Discussion Paper No. 17896, May 2025**;
  authors David Dorn, Florian Schoner, Moritz Seebacher, Lisa Simon, Ludger Woessmann.

---

## 6. Deliberate design choices (do not "fix" these)

- **Current Position before Education.** A German-convention ordering the CV keeps.
- **Masthead carries the name, address, email, phone and website** — no revision month and no
  closing `Munich, <date>` signature line. The revision date sits at the **foot** as
  `Last updated: <date>`, floated there with `\vfill` so it settles on whatever page the CV
  ends on rather than claiming a page of its own.
- **The page footer carries the page number only.** `jmstyle` prints the candidate's name in
  every footer so that a loose printed page still belongs to someone; the CV overrides that
  (Moritz, 10 Sep 2026) because the name is already the masthead. The statements and cover
  letters keep the jmstyle footer.
- **Journal and series names are italic**, including `IZA Discussion Paper`. The website sets
  them bold instead. Confirmed by Moritz 10 Sep 2026 as correct in both places, not drift: the
  CV sets paper titles in bold, so a bold venue would put two bold elements in every entry and
  the title would stop leading; the website makes the title a coloured link instead, so a bold
  venue there competes with nothing and makes the list scannable. The citation text, punctuation
  and ordering are identical either way, and the audit checks those. If the two are ever to be
  matched, change the **website** to italic — the CV's hierarchy depends on bold being reserved
  for titles, the website's does not depend on bold at all. The website also ends each citation
  with a period and the CV does not; both are internally consistent.
- **No location lines.** Entries name the institution; the institution carries the location.
- **`MM/YYYY` dates for spans, bare years for one-off events** (awards, refereeing,
  conference years, the YES! cycles).
- **Research Visits stays its own section** rather than folding into Education.
- **Job Market Paper is its own section**, title and year, followed by its abstract.
- **`(Bachelor)` appears on thesis-supervision entries** even though the line below says
  "Supervisor of bachelor thesis" — the redundancy keeps every teaching entry parallel.
- **No course-evaluation line** (Moritz, 10 Sep 2026). The seminar scored 1.1 against a
  departmental average of 1.6, but that evidence belongs in the teaching statement, which
  states it twice and attaches the full evaluation. The CV stays short.
- **`(Bachelor Seminar)`, not `(Bachelor)`, for the Worker Skills seminar** — it is the more
  accurate description.
- **`EEA-ESEM`**, the official congress name, not `EEA`.

---

## 7. Known open items

- **The YES! entry lost month precision** when it was collapsed to one entry (`2024, 2025`
  rather than two `MM/YYYY -- MM/YYYY` ranges). The alternative reads as two separate
  engagements, which it is not.
- **`Google Cloud` in Technical skills** is the wording Moritz asked for (10 Sep 2026), chosen
  to signal that he builds and runs the big-data infrastructure himself without saying so.
  It is the broader and more accurate term: the project code he writes and runs himself covers
  warehouse queries, cloud storage, and the pipeline between them, not one product. A single
  product name would be one word and would signal large-scale data harder to a reader who knows
  the tool, but it names only the warehouse and drops the rest. Evidence for this sits in the
  project repositories on the network drive, which is where it stays — this file is public.
- **Award years are inferred**, not sourced: the two VEUK awards are dated to the degree
  completion years (2022, 2020) and the Deutschlandstipendium to the combined study period
  (2017–2022). Replace with the actual award years when known.
- **Four pages for the committee copy, three for the public one.** Restoring the
  work-in-progress abstract on 10 Sep 2026 cost a page, bought back by tightening three
  spacing values: inter-entry `0.45em` to `0.30em`, after-paper `0.7em` to `0.5em`, and
  section spacing `1.1/0.45` to `0.95/0.40` baselineskip. **Do not tighten further** —
  `0.22em/0.42em` was tried and the entries start to run together. If the CV ever has to be
  shorter, condense the abstracts before cutting entries.
- `index.md` states the job-market year; the CV deliberately does not duplicate it.
