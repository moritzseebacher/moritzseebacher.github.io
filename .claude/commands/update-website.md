---
description: Validate, commit, push, and verify the academic website deployment on GitHub Pages
allowed-tools: Bash, Read, Glob, Grep
---

# Academic Website Updater

Validate, commit, push, and confirm deployment of `https://moritzseebacher.github.io`.

**Repo:** `f:/Academic Website/moseeb98.github.io/`
**Remote:** `https://github.com/moritzseebacher/moritzseebacher.github.io.git` (branch: `main`)
**Deployed via:** GitHub Pages (auto-builds on every push to `main`)

Run all steps in order. Report status as each step completes. Stop and ask only if there is a blocking issue you cannot resolve.

---

## Step 1 — Pre-flight: Required Files

Verify these files exist at the repo root:

- `index.md` — main content
- `_config.yml` — Jekyll config
- `_data/navigation.yml` — nav menu
- `Seebacher-Moritz_2023_7_ret_pass_format.jpg` — profile photo
- At least one `CV_Academic_Moritz_Seebacher_*.pdf` — CV document

Use Glob or Bash `ls` to check. Then:
- Grep `index.md` for `.pdf` to find the exact CV filename referenced.
- Confirm that filename matches the actual PDF on disk.
- If they differ, warn the user — this is a blocker.

---

## Step 2 — Internal Consistency Check

**Navigation anchors:**
- Read `_data/navigation.yml`, extract all `url:` values starting with `/#`.
- Read `index.md`, extract all heading anchors (`{#anchor-id}` patterns or auto-generated from `##` headings).
- Confirm each nav anchor resolves to a real heading. Report any mismatches.

**Abstract page:**
- If `index.md` links to `/abstract_facebook`, confirm `abstract_facebook.md` exists.

**CV filename:**
- Re-confirm the PDF filename in `index.md` matches the actual file on disk (carry over result from Step 1).

---

## Step 3 — External Link Check

Read `index.md` and `_config.yml`. Extract all `http://` and `https://` URLs. For each, run:

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 10 "<URL>"
```

- **200 / 301 / 302:** OK
- **403 / 401:** OK — expected for paywalled journal articles
- **404 / connection error:** Report as broken

Summarise: `N links OK`, then list any failures.

---

## Step 4 — Git Status

```bash
cd "f:/Academic Website/moseeb98.github.io" && git status && git diff HEAD --stat
```

Show the user what changed. If the tree is clean, inform the user, skip Steps 5–6, and jump to Step 7 (deployment health check only).

---

## Step 5 — Stage and Commit

Stage modified files explicitly — never `git add -A` blindly:

```bash
cd "f:/Academic Website/moseeb98.github.io"
git add index.md _config.yml _data/navigation.yml
git add assets/css/main.scss _includes/
git add abstract_facebook.md
git add *.pdf    # CV if updated
git add *.jpg *.png  # profile photo if updated
```

Check `git status` to confirm what is staged, then run the commit with a short imperative message (e.g. `Update CV and publication list`). Use HEREDOC format:

```bash
git commit -m "$(cat <<'EOF'
<message here>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

If the commit fails due to a pre-commit hook, report the hook error verbatim and do **not** retry with `--no-verify`.

---

## Step 6 — Push to GitHub Pages

```bash
cd "f:/Academic Website/moseeb98.github.io" && git push origin main
```

Report the push output. If the push is rejected (non-fast-forward), diagnose with:

```bash
git log --oneline origin/main..HEAD
```

Then inform the user — do **not** force push under any circumstances.

---

## Step 7 — Deployment Verification

GitHub Pages rebuilds automatically after push. Build time is typically 30–90 seconds.

**If `gh` CLI is available:**
```bash
gh run list --repo moritzseebacher/moritzseebacher.github.io --limit 3
```
Poll until the latest run shows `completed` / `success`. If it fails, show the failure URL for the user to inspect.

**If `gh` CLI is not available:**
Wait ~60 seconds, then check the site is reachable:
```bash
curl -s -o /dev/null -w "%{http_code}" https://moritzseebacher.github.io
```
A 200 confirms the site is up. Note: CDN caching may delay new content — inform the user.

---

## Final Summary

End every run with this block:

```
## Website Update Summary

Pre-flight:     ✓ / ✗  All required files present
CV match:       ✓ / ✗  <filename> linked and on disk
Nav anchors:    ✓ / ✗  N anchors checked
External links: ✓ / ⚠  N OK, M paywalled, K broken
Commit:         ✓ / –  <short-hash> — <message>   (– = nothing to commit)
Push:           ✓ / ✗  Pushed to origin/main
Deployment:     ✓ / ⏳  Build succeeded / in progress
Live site:      https://moritzseebacher.github.io
```

List any warnings or failures below the summary so the user can follow up.

---

## Edge Cases

- **CV filename changed:** Remind the user to delete the old PDF and commit the deletion — otherwise both files are served from root.
- **Old CV still on disk:** Run `ls *.pdf` to detect multiple PDF versions; warn the user.
- **Local Jekyll available:** Optionally run `bundle exec jekyll build` before committing to catch template/YAML errors early.
- **Merge conflict / diverged branch:** Do not force push. Report the situation and ask the user how to proceed.
