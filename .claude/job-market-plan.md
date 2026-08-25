# Job Market 2026/27 — Website Plan and Status

**Scope:** this file covers the **website** only. The broader job market plan — every document,
every deadline, interviews, flyouts, offers — lives outside this repository at
`F:\Academic Website\job_market_2026\00_guide_and_timeline.md`.

**Source:** *European Job Market Morning*, David Schindler (Tilburg), 17 August 2026.
**Last updated:** 25 August 2026.

---

## The requirement, and whether it is met

The deck asks four things of a candidate's website:

| Requirement | Status |
|---|---|
| *"Website live and findable: papers with abstracts and PDFs, CV, email"* | **Met** |
| *"One stable link to the current version. Not Dropbox, not Google Drive"* | **Met** |
| *"Link it from your department/placement page"* | **ifo met; MGSE open** |
| *"Now until September: … website live"* | **Met, ahead of deadline** |

---

## Decisions taken

| Question | Decision |
|---|---|
| Letter writers on the site | **CV only** — no References section on the website |
| Ungated PDFs | **Host both**, respecting self-archiving terms |
| Scholarly profiles | Claude drafts content, Moritz creates the accounts |
| Site scope | **Lean, deck-minimal** — no Teaching section, no posted statements, no separate Contact block |
| PDF link placement | Button on the same row as the `Abstract` toggle, **link first** so both pack left |
| PDF link label | `PDF` on both entries; version status carried by a notice on the file itself |
| Abstract toggle | Same boxed style as the PDF button, applied to every abstract on the page |

---

## Done

| # | Item | Notes |
|---|---|---|
| 1 | Letter writers — preferences conversation | Names settled; CV section deferred to end September |
| 3 | EER accepted manuscript hosted | Rebuilt to JMP layout: title page merged, visible hyperlinks, references before the appendix, funding section dropped, provenance note with DOI and CC-BY-NC-ND in the acknowledgements. 33 pages. Source in `F:\Academic Website\Pathways_to_Progress_AAM` |
| 5 | Google Scholar + RePEc profiles | Both public and verified, linked in the sidebar and in the `sameAs` list |
| 7 | IZA DP hosted and linked | `Multidimensional_Skills_LinkedIn_IZA_DP17896.pdf` |
| 8 | Build gate | `.claude/scripts/site_check.py` — verified against six deliberately broken trees. A `Gemfile` is committed but untested |
| 9 | `og_image` and SEO description | Link previews render; snippet names the job market year |
| 10 | JMP draft date | "Draft: August 2026" beside the link |
| 12 | Conventions documented | `CLAUDE.md` covers the action-row markup and the self-archiving rules |
| — | ifo profile link | Already in place; no action needed |

---

## Open — website

### W1. MGSE placement listing
The one unmet part of *"link it from your department/placement page."* The
[placement page](https://www.econ.lmu.de/en/faculty/mgse/job-market-candidates-and-placement/)
lists the 2025/26 cohort, each name linked to a personal site; the 2026/27 cohort is not yet
posted. Email drafted in `job-market-drafts.md`. **Owner: Moritz. Send in August** — it sits in
someone else's queue.

### W2. CV refresh — the last website-visible change
Two edits to the `.docx`, then one export:
- Add the **References** section (names settled, goes public end of September)
- Update **conferences**: COPE 2026 and EEA-ESEM 2026 still read "scheduled" but the JMP
  acknowledgements now thank participants at both as past events

Then export `CV_Academic_Moritz_Seebacher_09_26_English.pdf`, repoint `index.md`, delete the July
PDF, re-run `cv_audit.py`, run `site_check.py`. **Owner: Moritz (docx) + Claude (rest).
Due 30 September.**

### W3. Switch the RePEc link to the IDEAS mirror
`ideas.repec.org/f/pse845.html` still returns 404 — IDEAS regenerates author pages on a schedule.
The sidebar currently uses `authors.repec.org/pro/pse845/`, which works. Once the IDEAS URL
resolves, switch, since that is the URL economists recognise. **Owner: Claude. Re-check early
September.**

### W4. Search Console re-index
Best done once, after the CV lands, rather than after each change.
`search.google.com/search-console` → URL Inspection → Request Indexing; confirm the sitemap is
submitted. **Owner: Moritz. After W2.**

---

## Open — adjacent, not website

Tracked here only so nothing falls between the two plans. Full detail in
`F:\Academic Website\job_market_2026\00_guide_and_timeline.md`.

| Item | Owner | Due |
|---|---|---|
| Research statement, teaching statement, cover letter master | Moritz | 30 Sep — drafts ready in the job market folder |
| JMP introduction polish, 4–5 pages | Moritz | 30 Sep |
| JM spiel drafted and memorised | Moritz | draft Sep, memorised Oct |
| ifo Working Paper deposit for the JMP | Moritz + advisors | decision open; start early Sep if yes |
| Letter writers sent package + targets | Moritz | mid-Sep |
| EJME Candidate Directory profile | Moritz | mid-Nov; text drafted |
| Signals — EJME up to 5, AEA 2 | Moritz | end Nov |

---

## Next actions, in order

1. **Moritz:** send the MGSE email (W1) — slowest to come back
2. **Moritz:** retrieve teaching evaluations — the teaching statement is blocked on nothing else
3. **Moritz:** react to the research and teaching statement drafts
4. **Moritz + advisors:** decide on the ifo Working Paper deposit
5. **Claude:** re-check the IDEAS URL in early September (W3)
6. **Moritz → Claude:** reference names when the CV goes public, then W2 and W4 in one pass

---

## Working notes

**Self-archiving.** Elsevier permits the accepted manuscript on a personal homepage immediately,
never the typeset version; the file must carry a CC-BY-NC-ND notice and a DOI link. IZA
Discussion Papers carry no such restriction.

**Two corrections worth remembering**, both cases of reporting "my tools could not see it" as
"it is not there":
- The EER paper *did* have an ungated version all along — ifo Working Paper 382 (2022), under the
  earlier title *Infrastructure and Girls' Education*. It reports different magnitudes than the
  published paper, so the hosted accepted manuscript is still the right thing on the site.
- The ifo profile page *does* link the website. ifo.de sits behind bot protection, so this can
  only be checked in a browser.

**RePEc items:** four are indexed, not two. Full list with handles in `job-market-drafts.md`.
