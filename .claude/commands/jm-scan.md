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

## Moritz's profile — what counts as a match

Confirmed 25 August 2026.

**Geography: Europe, hard focus.** Non-European postings are heavily deprioritised but still
listed, because nothing is ever dropped. **Location preferences that genuinely matter:** his
partner lives in **Munich** and his family is near **Karlsruhe**. Munich and Karlsruhe postings
carry the heaviest weight in the profile, then Bavaria and Baden-Württemberg, then Germany, then
the rest of Europe. Treat a Munich or Karlsruhe posting as worth surfacing even if the field fit
is mediocre — and say why you are surfacing it.

**Position types: all four families count as strong matches** — academic (assistant professor,
tenure-track, junior professor, lecturer), postdocs and research fellowships, policy institutions
and central banks (ifo, ZEW, IZA, DIW, IAB, Bundesbank, ECB, OECD), and industry research. His
stated criterion is *a good worker-firm match with long-run career prospects within Europe*, not
an academic-only search. Do not quietly rank a good policy-institute role below a mediocre
professorship.

**Sources: EJM only** for now.

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

## Step 2 — Candidate list

Read the generated report. Do **not** paste it at him — it is raw. Then produce the
**candidate list**: every advert that passed pre-screening and has no decision yet.

```bash
cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/jm_decide.py --list
```

That prints each candidate with id, fit score, institution, country, deadline **and the
advert URL**. Present it as a short digest — one line per advert, always including the link,
because he checks the ad while deciding.

- **Lead with anything urgent.** A deadline or first-review date inside 14 days goes first,
  whatever the score. The deck: *"Watch for early deadlines."*
- **Read the field lists yourself.** The scorer is keyword matching with no judgement.
  Promote, demote, and say plainly where you disagree with it.
- **Say what is missing.** No deadline, no field list, unclear contract — flag it rather
  than padding the entry.
- If nothing new: say so in one sentence. Never manufacture content.

Adverts already marked `added` or `skipped` never reappear. Ones marked `pending` come back
every scan, tagged *(deferred earlier)*, until he decides.

## Step 2a — Check whether he is applying yet

```bash
cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/jm_decide.py --status
```

If it prints **NOT APPLYING YET**, `state/config.json` says he has not started applying.
As of 27 Aug 2026 that is the case: he is still finishing the job market paper and the
package, and does not intend to apply before **1 October 2026**.

While that holds:

- **Keep scanning and scoring every day he asks.** Nothing may be missed.
- **Present a watchlist, not a decision queue.** Report what is new and what is worth
  knowing about, and stop there.
- **Do NOT run Step 3.** Do not ask advert by advert. He skipped four top-scoring adverts
  on 27 August purely because it was too early, and reading that as a preference signal
  would have wrecked a correctly calibrated model.
- Adverts closing before `applying_from` are dropped from the list automatically — he
  cannot act on them, so listing them is noise rather than recall.

On the **first scan on or after `applying_from`**, do a catch-up pass over every live
advert still open, then resume Step 3 normally. Flip `applying` to true in `config.json`
when he says the package is ready — and tell him you have.

**A skip for timing is not a skip for fit.** If he ever declines adverts because it is too
early rather than because they are wrong, record them with `--defer`, not `--skip`, so they
return when he is ready.

## Step 3 — Ask advert by advert

**This is the required flow. Do not ask for a bulk yes/no.** Go through the candidate list
one advert at a time, using AskUserQuestion. It takes at most four questions per call, so
work in batches of four, highest score first.

For each advert, one question. Put the **URL in the option description** so he can open the ad
while deciding, and give four options:

| Option | Effect |
|---|---|
| **Add to tracker** | `--add <id>` — writes the row, never asked about again |
| **Skip** | `--skip <id>` — never asked about again |
| **Needs a closer look** | `--defer <id>` — reappears on the next scan |
| **Add, and it is a signal candidate** | `--add <id>`, plus note it on the signal shortlist |

Give him what he needs to decide in the question itself: institution, location, rank,
contract, field list, deadline, and the one thing that makes it a good or bad fit. Where the
score and your own reading disagree, say so in the question rather than hiding it.

Then record every decision:

```bash
python .claude/scripts/jm_decide.py --add 12601      # or --skip / --defer
```

Never write tracker rows by hand — the script handles CSV quoting, converts EJM's
`27 Sep 2026` into the ISO dates the deadline checker needs, and refuses to write a
duplicate row for an advert already tracked.

## Step 3a — After the approvals

Confirm what changed: how many added, skipped, deferred, and the tracker row count. Then for
each **added** advert, give the tailoring advice below.

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
- **Letter-writer notification — the rule Moritz set.** No routine emails. The tracker is the
  source of truth. Draft a chase **only** when a deadline is inside **14 days** *and* the writers
  have not confirmed in the tracker that the letter went. Run the check rather than eyeballing it:

  ```bash
  cd "f:/Academic Website/moseeb98.github.io" && python .claude/scripts/jm_deadlines.py
  ```

  Everything under `LETTER FLAG` needs a drafted email; nothing else does. The script suppresses
  the flag once `letters_in` is confirmed, so a chase never goes out twice. **Also read the
  `UNREADABLE DATES` section** — those rows are invisible to the check, which is worse than a late
  flag; fix them into ISO format and say you did.
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

## State files

| File | Holds |
|---|---|
| `state/seen_positions.json` | every advert ever fetched, with its parsed fields |
| `state/decisions.json` | added / skipped / pending, per advert |
| `06_application_tracker.csv` | the applications he actually committed to |
| `reports/scan_DATE.md` | that day's new adverts |
| `reports/rescore_DATE.md` | everything re-scored after a weight change |

Deleting `seen_positions.json` makes the next scan re-report everything. Deleting
`decisions.json` makes it re-ask about everything.

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
