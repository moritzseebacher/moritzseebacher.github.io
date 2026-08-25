# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Academic personal website for Moritz Seebacher (PhD student, ifo Institute / LMU Munich). Hosted on GitHub Pages at `https://moritzseebacher.github.io`. Repository: `github.com/moritzseebacher/moritzseebacher.github.io`. Research focus: education & labor economics, using LinkedIn data to study skills, social networks, and career trajectories.

## Tech Stack

- **Jekyll** static site generator using the **Minimal Mistakes** remote theme (`mmistakes/minimal-mistakes`)
- Markdown (Kramdown with GFM) for content
- SCSS for custom styling (`assets/css/main.scss`)
- Vanilla JS for mobile nav fix (`_includes/footer/custom.html`)
- Plugins: `jekyll-include-cache`, `jekyll-sitemap`, `jekyll-seo-tag`

## Build & Preview

```bash
bundle exec jekyll serve        # Local dev server (default: http://localhost:4000)
bundle exec jekyll build        # Build static site to _site/
```

No Gemfile is currently committed — if adding one, include `github-pages` gem or `jekyll` + `minimal-mistakes-jekyll` for local builds.

## File Structure

```
moseeb98.github.io/
├── _config.yml                          # Jekyll config, author profile, theme settings
├── _data/navigation.yml                 # Top nav bar entries (all anchor links to index.md)
├── _includes/footer/custom.html         # Mobile nav JS fix (moves nav items to hidden-links)
├── assets/css/main.scss                 # Custom SCSS overrides (avatar sizing, mobile layout)
├── index.md                             # Main page — all content sections live here
├── Seebacher-Moritz_2023_7_ret_pass_format.jpg    # Profile photo (served from root)
├── Seebacher_Career_Effects_Online_Social_Networks.pdf  # Job market paper (stable filename)
├── Multidimensional_Skills_LinkedIn_IZA_DP17896.pdf     # Working paper PDF (stable filename)
└── CV_Academic_Moritz_Seebacher_07_26_English.pdf  # CV (served from root)
```

## Architecture

Single-page academic site — all content lives on the index page:

- **`index.md`** — All content lives here as sections with anchor IDs: `#job-market-paper`, `#publications`, `#working-papers`, `#work-in-progress`, `#policy-papers-non-refereed`, `#cv`.
- **`_data/navigation.yml`** — Defines `main` nav (top bar) and `sections` sidebar nav, both pointing to anchors on the index page.
- **`_config.yml`** — Author profile (name, avatar, bio, email, LinkedIn), theme skin (`default`), plugins, locale, timezone.
- **`assets/css/main.scss`** — Responsive avatar/sidebar layout overrides (see below).
- **`_includes/footer/custom.html`** — JavaScript that runs on mobile (≤800px) to force all nav items into the Minimal Mistakes hidden-links dropdown, ensuring the `…` toggle works correctly.

## Content Conventions

### Publication / paper entries

Each entry is a Markdown bullet:
```markdown
- [Paper Title](https://url-to-paper) (with Co-Author Name)  
  <small><strong>Venue Name</strong>, Volume X (Year), pages.</small>
```

- Two trailing spaces after the first line are **critical** — they produce the `<br>` that separates the title/authors from the citation.
- Coauthors in parentheses after the title link, only when applicable.
- Citation in `<small><strong>Venue</strong>, details.</small>`.

### Abstracts

Every entry at working-paper stage or beyond (publications, working papers) carries a collapsible abstract. Non-refereed policy papers do **not**. Work-in-progress entries carry one only once an abstract exists (the alumni-networks project does); they stay title-only otherwise, and never link to a PDF. The job market paper is the exception: its abstract is always visible, not collapsed.

```markdown
- [Paper Title](https://url) (with Co-Author)  
  <small><strong>Venue</strong>, details.</small>
  <details class="abstract"><summary>Abstract</summary><span>Full abstract text…</span></details>
```

- **No blank line** before `<details>` — the list item must stay "tight". A blank line makes kramdown wrap the item in `<p>`, which invalidly nests `<details>` inside a paragraph.
- Keep the whole `<details>` on **one line**; the abstract text must not contain blank lines.
- The abstract must match the published/working-paper version **verbatim** (fix only line-break artifacts from PDF extraction, e.g. `ageskill` → `age-skill`).
- Styling lives in `assets/css/main.scss` under `--- COLLAPSIBLE PAPER ABSTRACTS ---`.
- Abstracts are website-only — **never** add them to the CV.

### Hosted paper PDFs

Publications and working papers that have an ungated PDF hosted in the repo root carry a `PDF`
button on the same row as the `Abstract` toggle. The `<details>` is wrapped in a
`<div class="paper-actions">` together with the link:

```markdown
- [Paper Title](https://publisher-url) (with Co-Author)  
  <small><strong>Venue</strong>, details.</small>
  <div class="paper-actions"><details class="abstract"><summary>Abstract</summary><span>Abstract text…</span></details><a class="paper-pdf" href="/File_Name.pdf">PDF</a></div>
```

- Same tightness rules as the bare `<details>`: no blank line before the `<div>`, whole block on one line.
- Styling lives in `assets/css/main.scss` under `--- PAPER ACTION ROW ---`.
- Label is always `PDF`, for every entry. Version status (accepted manuscript vs. published
  version) is carried by a notice on the file itself, not by the link text.
- Hosted PDFs use **stable filenames**, like the JMP — never dated ones.
- Before hosting a published paper, check the publisher's self-archiving terms. For Elsevier
  (Economics of Education Review), the accepted manuscript may go on a personal homepage
  immediately, but the typeset version may **not**; the file must carry a CC-BY-NC-ND notice and
  a DOI link to the version of record. IZA Discussion Papers carry no such restriction.

### Section headings

Use `## Title {#anchor-id}` so navigation links (`/#anchor-id`) resolve correctly.

### Static files

CV PDF, job market paper PDF, and profile photo are served from the repo root (no subdirectory).

### Job market paper update workflow

Unlike the CV, the JMP PDF keeps a **stable filename** — `Seebacher_Career_Effects_Online_Social_Networks.pdf` — so that links shared on the job market never break. New drafts are dated in the paper itself, not in the filename.

**When a new draft arrives:**
1. Overwrite `Seebacher_Career_Effects_Online_Social_Networks.pdf` with the new PDF, keeping the filename unchanged. Do not add a dated copy to the repo root.
2. Diff the new title page against `index.md` (`pdftotext -f 1 -l 1 <pdf> -`) — the title in the `## Job Market Paper` heading and the `**Abstract.**` paragraph must match the PDF verbatim.
3. If the title changed, update it in `index.md` **and** in the CV (rule `R37` in `.claude/scripts/cv_audit.py` enforces this).
4. Commit and push — the new PDF goes live at the same URL.

### CV update workflow

The CV is maintained in a Word document (`.docx`) that lives in the repo root locally but is excluded from git via `.gitignore`. Only the exported PDF is committed and served.

**When updating the CV:**
1. Edit `CV_Academic_Moritz_Seebacher_MM_YY_English.docx` locally.
2. Export/save as PDF with the updated filename (e.g. `CV_Academic_Moritz_Seebacher_03_26_English.pdf`).
3. Update the CV link in `index.md` to point to the new PDF filename.
4. Delete the old PDF from the repo (or it will accumulate).
5. Commit and push — the new PDF goes live automatically.

## Responsive Layout (CSS)

**Desktop (≥1024px):** Sidebar avatar is circular, 85% of sidebar width, portrait crop (`aspect-ratio: 5/6`, `object-position: 50% 15%`).

**Mobile (≤800px):** Two-column CSS grid — photo fills the left column, name/bio and contact links stack in the right column. Avatar is rectangular (no border-radius, `object-fit: contain`). The `…` button replaces the hamburger icon; the footer JS moves all nav items to the hidden-links dropdown.

## Deployment

Push to `main` branch → GitHub Pages builds and deploys automatically. No CI/CD config needed.

Repository: `https://github.com/moritzseebacher/moritzseebacher.github.io`
Live site: `https://moritzseebacher.github.io`
