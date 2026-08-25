# Job Market 2026/27 — Website & Package Plan

**Created:** 25 August 2026
**Source:** *European Job Market Morning*, David Schindler (Tilburg), 41 slides, 17 August 2026
**Deck deadline for the site:** "Now until September: last iterations on the JMP; package assembled; **website live**."

---

## Decisions taken (25 Aug 2026)

| Question | Decision |
|---|---|
| Letter writers / references | **CV only** — no References section on the website |
| Ungated PDFs | **Host both** on the site, respecting self-archiving terms; preprint as fallback |
| Scholarly profiles | **Claude drafts the content, Moritz creates the accounts** |
| Site scope | **Lean, deck-minimal** — no Teaching section, no research/teaching statements, no separate Contact block |
| PDF link placement (25 Aug) | **Button next to the `Abstract` toggle**, same row — needs new SCSS under the existing `--- COLLAPSIBLE PAPER ABSTRACTS ---` block |
| PDF link label (25 Aug) | **`PDF` on both entries** — version status is carried by the CC-BY-NC-ND + DOI cover note on the EER file itself, not by the link text |

Dropped as a result: site References section, Teaching section, posted statements, Contact block
(sidebar email already satisfies the deck), X/Twitter link.

---

## Verified constraints

**Economics of Education Review (Elsevier).**
- Published version: **cannot** be posted publicly.
- Accepted manuscript (AAM): **may** go on a personal homepage **immediately, no embargo**.
- Two conditions attach to the file: it must carry a **CC-BY-NC-ND** notice and **link to the formal
  publication via DOI**.
- DOI: `10.1016/j.econedurev.2023.102483`
- Fallback if the AAM is lost: preprints may be shared "anywhere at any time."

**IZA DP 17896.** Imprint carries no license restriction and no redistribution clause. Authors retain
rights. Direct URL: `https://docs.iza.org/dp17896.pdf`

**Confirmed gaps.** IDEAS lists no ungated version of the EER paper and no registered RePEc author
profile. No Google Scholar profile exists. The ifo team page does not expose the website URL. The MGSE
placement page currently lists the 2025/26 cohort only.

---

## Next steps, lowest to highest priority

### 12 (lowest) — Update CLAUDE.md conventions  **[DONE 25 Aug 2026, alongside step 7]**
Bookkeeping that follows the work: the static-files list and the paper-entry convention both change
once PDFs are hosted. **Owner:** Claude. **When:** after step 7 lands.

### 11 — Request re-indexing in Search Console
Cannot happen before the content is live. **Owner:** Moritz. **When:** end of September.

### 10 — Draft date beside the JMP link  **[DONE 25 Aug 2026]**
Add "Draft: August 2026" in `index.md` so nobody wonders whether they hold the current version.
Two-minute edit, no dependencies. **Owner:** Claude.

### 9 — og_image and SEO description  **[DONE 25 Aug 2026]**
`og_image` in `_config.yml` pointing at the profile photo, so applications and shared JMP links stop
rendering as blank cards; amend `description:` to name the job market year so the Google snippet
identifies a 2026/27 candidate. **Owner:** Claude. No dependencies.

### 8 — Gemfile and build gate
Nothing is built locally before a push today. During the Oct/Nov marathon a broken `main` is a live
outage on the URL in 200+ applications. Add a `Gemfile` and gate pushes on `bundle exec jekyll build`.
**Owner:** Claude. **When:** must be in place before applications go out.

### 7 — Host and link the IZA DP  **[DONE 25 Aug 2026]**
`Multidimensional_Skills_LinkedIn_IZA_DP17896.pdf` in the repo root, surfaced as a `PDF` button on the
same row as the `Abstract` toggle. Carries the new SCSS that step 3 then reuses. Applies to two entries
only — the publication and the working paper; the JMP keeps its existing prominent link and the
alumni-networks entry stays title-only. Zero blockers, terms verified, **fully specified and ready to
run on go-ahead.** **Owner:** Claude.

### 6 — EJME Candidate Directory profile
Required for signals (up to 5 signals, deadline end of November, transmitted early December).
Later deadline than everything else, but the profile should exist before applications go out.
**Owner:** Moritz, content drafted by Claude.

### 5 — Google Scholar and RePEc/IDEAS author profiles
Neither exists. Indexing takes weeks to propagate, so creating them in August means they are populated
when committees search in November. Cheap, but the lead time is the reason this outranks the site edits.
**Owner:** Moritz, content drafted by Claude.

### 4 — CV: conferences refresh and September export
COPE 2026 and EEA-ESEM 2026 are still listed as "scheduled" but the JMP acknowledgements now cite both
as past. Export `CV_Academic_Moritz_Seebacher_09_26_English.pdf`, repoint `index.md`, delete the July
PDF, re-run `cv_audit.py`. **Owner:** Moritz (docx) + Claude (audit, site). **When:** September,
before applications.

### 3 — Locate the EER accepted manuscript  **[BUILT 25 Aug 2026 — awaiting review before hosting]**
Source found at `OneDrive/Roads and Bicycles in India/Revision Upload II/`. Rebuilt in
`F:/Academic Website/Pathways_to_Progress_AAM/` to the JMP layout, with the CC-BY-NC-ND + DOI
notice on the title page, dated October 2023 (accepted), not 	oday.
All approved corrections applied: six unambiguous typos, plus British/American spelling, a comma
splice, acknowledgements grammar, unit spacing (3km -> 3 km), en-dashes for numeric ranges, and
34 parenthesised citations converted to \citep so they read "(Author, Year)" like the JMP.
Table files normalised too, with \cmidrule column specs guarded. Verified by diffing the rendered
text against a pristine baseline build. Structure then aligned to the JMP and IZA convention: funding section dropped, references moved
ahead of the appendix, and the accepted-manuscript provenance note folded into the
acknowledgements footnote as one sentence carrying the DOI and CC-BY-NC-ND links. All eight
bibliography URLs wrapped so every link in the document is live. Final: 33 pages, no LaTeX
errors, no undefined references, no overfull boxes, 227 link annotations.
**Not yet copied into the repo root — awaiting go-ahead.**

Blocker for the highest-value site change, with unknown resolution time — it may take a search through
email, Overleaf, or a coauthor. Starting the hunt early is what makes it cheap. If only the preprint
survives, that is a valid fallback. Once found: add the CC-BY-NC-ND + DOI cover note, host as
`Seebacher_Pathways_to_Progress.pdf`, link from the citation line. **Owner:** Moritz to supply the file.

### 2 — ifo team page and MGSE placement links
The deck's explicit requirement: "Link it from your department/placement page." Both are controlled by
other people, which is exactly why they rank this high — the lead time is not yours to compress. Ask
ifo web comms to expose `https://moritzseebacher.github.io` on the team page, and ask MGSE to include
you with a link when the 2026/27 cohort posts. **Owner:** Moritz (Claude can draft both emails on request).

### 1 (highest) — Letter writers: preferences conversation, then CV References
**Conversation DONE (25 Aug 2026).** Remaining: the CV References section, which now has its names and
is no longer blocked. This moves step 4 (CV export) up to become the top open people-dependent item.

The deck is unambiguous about the timing: "Tell your writers where you apply and what you prefer;
**now, not in November**. Choose letter writers early enough, discuss with advisors." Highest stakes in
the entire package, entirely dependent on other people's calendars, and it gates the CV References
section (step 4). Nothing else on this list matters as much if the letters are weak or late.
**Owner:** Moritz. The CV section follows through the `cv-check` skill once names are settled.

---

## Today — 25 August 2026

**Moritz, in roughly an hour:**
1. ~~Book the advisor conversation on letter writers (step 1).~~ **DONE 25 Aug 2026.**
2. Spend ten minutes hunting the EER accepted manuscript (step 3) — email, Overleaf, coauthor. Report
   found / preprint-only either way, because that answer unblocks the site work.
3. Create the Google Scholar profile (step 5) — needs your login, ~10 minutes, and the indexing clock
   starts the moment it exists. Setup instructions issued 25 Aug 2026, see below.
4. Now unblocked by step 1: hand over the agreed reference names for the CV References section (step 4).

**Claude, on your go-ahead, needs no input from you:**
Steps 7, 9, 10 in a single commit series — IZA PDF hosted and linked, `og_image`, SEO description,
JMP draft date. Then step 8 (Gemfile) as a second commit.

**Deliberately not today:** the CV export (step 4) waits for the reference names; step 12 waits for
step 7; step 11 waits for everything.

---

## Timeline

| When | Steps |
|---|---|
| Today | ~~1 (done)~~, 3 (start), 5 — plus 7, 9, 10 on go-ahead |
| This week | 2, 8, 6 |
| Mid-September | 4, 3 (finish), 12 |
| End September | Deck's "website live" deadline; 11 |
| Oct/Nov | Applications. Site frozen except JMP draft swaps via the stable-filename workflow |
| End November | EJME signals due |

---

## Appendix A — Google Scholar profile setup (issued 25 Aug 2026)

Step 5 in the priority list. ~10 minutes. Needs your login, so it cannot be delegated.

### Field values to enter

| Field | Value |
|---|---|
| Name | `Moritz Seebacher` |
| Affiliation | `PhD Candidate, ifo Institute and LMU Munich` |
| Email for verification | `seebacher@ifo.de` — **must** be the institutional address, a personal address will not verify |
| Areas of interest | `Labor Economics`, `Economics of Education`, `Human Capital`, `Social Networks`, `Big Data Economics` |
| Homepage | `https://moritzseebacher.github.io` |

Sign in with a **personal** Google account, not an ifo-managed one — the profile has to outlive the
current affiliation.

### Procedure

1. `scholar.google.com` → hamburger menu → **My profile**.
2. Fill the fields above. The homepage field is what links Scholar back to the site — do not skip it.
3. **Articles step.** Scholar proposes article groups matching the name. Claim:
   - *Pathways to Progress: The Complementarity of Bicycles and Road Infrastructure for Girls' Education*
     — Economics of Education Review 97, 102483, 2023
   - *Multidimensional Skills on LinkedIn Profiles: Measuring Human Capital and the Gender Skill Gap*
     — IZA DP 17896, 2025
   - *Wie Fahrraeder die Bildungschancen von Maedchen in Entwicklungslaendern verbessern koennen*
     — ifo Schnelldienst 77(3), 2024
   Reject everything by **Stefan Seebacher** and **Frank Seebacher** — both are active researchers and
   are the reason for the settings choice in the next step.
4. **Settings step.** Choose **"Email me updates to review"**, not automatic application. With the name
   collisions above, automatic updates will eventually attach someone else's paper to the profile.
5. **Make the profile public.** It is private by default and invisible to search until this is toggled.
   This is the single step most often missed.
6. **Verify the email** from the ifo inbox. Until verified, the profile does not appear in Scholar search.
7. Add a photo — the same one the website uses, for recognisability across profiles.

### Do not add manually

The job market paper and the alumni-networks project. Scholar crawls PDFs from personal sites and will
index the JMP on its own; a manual entry cannot carry a link and would later collide with the crawled
version. The alumni-networks paper has no public draft, so there is nothing to index.

This is a direct argument for step 7 and step 3: **hosting the PDFs is what makes Scholar find them.**

### Afterwards

Send the profile URL over. Adding it to the `_config.yml` sidebar links is a Claude step, alongside the
RePEc profile when that exists.
