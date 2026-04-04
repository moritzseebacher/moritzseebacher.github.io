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
├── abstract_facebook.md                 # Standalone abstract page (/abstract_facebook)
├── Seebacher-Moritz_2023_7_ret_pass_format.jpg  # Profile photo (served from root)
└── CV_Academic_Moritz_Seebacher_01_26.pdf       # CV (served from root)
```

## Architecture

Single-page academic site with one additional detail page:

- **`index.md`** — All primary content lives here as sections with anchor IDs: `#publications`, `#working-papers`, `#work-in-progress`, `#policy-papers-non-refereed`, `#cv`.
- **`abstract_facebook.md`** — Standalone abstract for the Facebook/career paper. Uses `permalink: /abstract_facebook`. Linked from the Work in Progress section.
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

### Section headings

Use `## Title {#anchor-id}` so navigation links (`/#anchor-id`) resolve correctly.

### Static files

CV PDF and profile photo are served from the repo root (no subdirectory).

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
