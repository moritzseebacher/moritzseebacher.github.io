# Job Market Scan

Daily sweep for new job market postings, triage against Moritz's profile, and — **only after he
approves** — tracker entry, document-tailoring advice, and the follow-up actions each application
triggers.

**Invoke:** `/jm-scan`

---

## Hard rules

1. **Never submit an application.** Ever. Under any phrasing of the request.
2. **Never send email.** You cannot. Draft it, show it, let Moritz send it.
3. **Nothing enters the tracker without explicit approval**, per position, in this conversation.
4. **Recall beats precision.** The deck's arithmetic — 600–800 applications per opening, 1 in 25
   interviewed, *"apply widely, unless you would never go, 200+ applications is normal"* — means a
   missed posting costs far more than three extra lines of reading. Show borderline items. Do not
   quietly filter.
5. **Never invent a deadline.** If the posting does not state one, say "not stated" and link out.
   A wrong deadline in the tracker is worse than no tracker.

---

## Step 1 — Scan

```bash
cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/jm_scan.py
```

Writes a report to `F:\Academic Website\job_market_2026\reports\scan_YYYY-MM-DD.md` and records
the postings as seen, so tomorrow's run shows only genuinely new ones.

- First run of the day: expect a handful. If it returns 40+, the state file was probably reset —
  check before dumping everything on him.
- `--dry-run` scans without recording as seen. Use it if you need to look twice.
- If the scan errors or returns nothing, **say so plainly**. A silent empty report reads as
  "nothing new today", which is a different and much worse claim.

## Step 2 — Triage and report

Read the generated report. Do **not** paste it at him — it is raw. Write a short digest:

- **Lead with anything urgent.** A first-review or target date inside 14 days goes first,
  regardless of relevance score. The deck: *"Watch for early deadlines"* — some 2026/27 positions
  close in mid-October.
- **Group by relevance,** using the report's ordering, but read the field lists yourself. The
  scorer is keyword matching; it has no judgement. Promote and demote as you see fit, and say when
  you disagree with it.
- **One line per posting:** institution, position, location, deadline, why it fits or does not.
- **Say what is missing.** If a posting has no deadline or no field list, flag that rather than
  padding it.
- If nothing new: say so in one sentence. Do not manufacture content.

Then ask which he wants to apply to. Offer a fourth option beyond yes/no/later: **"needs a look"**
for postings where the ad is ambiguous and he should read it himself before deciding.

## Step 3 — On approval, per approved position

### 3a. Tracker

Append a row to `F:\Academic Website\job_market_2026\06_application_tracker.csv`.

Columns: `institution, country, position, platform, ad_link, deadline, first_review_date,
documents_required, n_letters, letters_route, cover_letter_customised, submitted_date, letters_in,
signal_sent, interview_date, interview_outcome, flyout_date, offer, notes`

- Read the file first, append, never rewrite wholesale — he edits it by hand between runs.
- Quote any field containing a comma.
- `documents_required` comes from the posting's own list, not a guess.
- Leave `submitted_date` empty; that is his to fill.

### 3b. Tailoring advice

This is the part that earns its keep. For each approved position, give him:

**Cover letter — paragraph 4.** Name which of the four patterns in
`01_cover_letter_template.md` fits (research-group / data-infrastructure / teaching / personal),
and draft the actual two-to-four sentences. Check the department's people page and seminar series
before claiming a fit — a specific, checkable claim beats a generic one, and a wrong one is worse
than none. Respect the deck's caution about naming individuals: prefer a group, centre or seminar
unless the fit is genuinely specific.

**Which paper leads.** The JMP always, but the framing shifts. A labour department wants the
career-trajectories framing; an education group wants the college-to-work transition; a
public/development post may want the bicycles paper surfaced earlier than usual.

**Research statement.** Usually unchanged. Say so when it is — do not invent work.

**Teaching statement.** Flag when the post is teaching-weighted (UK, NL, liberal arts, anything
naming a teaching load) and say which courses from the statement to foreground.

**Extra documents.** Diversity statement, transcripts, separate portals, reference forms. The
deck: *"Read ads carefully: sometimes contain extra steps, separate portals, and first-review
dates."* Anything unusual goes in `notes`.

### 3c. Downstream actions

Work out what each application triggers and tell him — do not just note it:

- **Letters.** How many, and does the route differ from EJM's default? If it needs anything
  beyond the standard EJM upload, that is a letter-writer action with a lead time.
- **Supervisor notification.** If new deadlines have appeared since the last notification, draft
  the update email. Do not send it. The deck: writers should hear *"now, not in November"*, and
  the tracker — not your inbox — is the source of truth, so the email should point at it rather
  than restate it.
- **Signal candidates.** Flag postings worth an EJME or AEA signal: *"Spend a signal only where it
  flips the decision: places that might think you would not come otherwise."* Not safe bets, not
  unreachable places. Keep a running shortlist; signals are due end of November, 5 EJME and 2 AEA.
- **Calendar pressure.** If several deadlines cluster, say so, with the count and the week.
- **Missing prerequisites.** If a posting needs something not yet finished — the September CV,
  the teaching statement's evidence — say which, so the blocker is visible.

## Step 4 — Close

State plainly: how many scanned, how many new, how many approved, how many tracker rows added,
and what needs him next. If you drafted an email, show it and say it is unsent.

---

## Configuration

`F:\Academic Website\job_market_2026\state\profile.json` holds the scoring weights. It only ever
**ranks** — nothing is dropped for a low score. Edit it when the triage is consistently wrong,
and tell him when you do.

`F:\Academic Website\job_market_2026\state\seen_positions.json` is the memory. Deleting it makes
the next scan re-report everything.

**Sources.** EJM (`econjobmarket.org`) is the sweep. The other platforms in the deck — JOE, AJO,
Interfolio, SSRN, HigherEdJobs, jobs.ac.uk — are not scanned automatically; JOE skews US and the
rest need per-site parsers. If he asks about them, check manually and say that is what you did.

**Data lives outside the repo** in `F:\Academic Website\job_market_2026`, because where he is
applying is private and this repository is public. Never write tracker rows, reports, or state
into the website repo.
