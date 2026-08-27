#!/usr/bin/env python3
"""Scan job platforms for postings not yet seen, and score them against a profile.

Design notes
------------
* State lives OUTSIDE the public website repo, in the job market folder, because the
  set of positions Moritz is tracking is private. Only this script is public.
* "New" means "not in seen_positions.json". Postings are recorded as seen only when a
  report is actually written, so an interrupted run does not silently swallow listings.
* Detail pages are fetched only for unseen ids, so the first run is slow and every
  later run is cheap.
* Filtering is deliberately RECALL-ORIENTED. The profile config can only ever
  down-rank, never drop: everything fetched appears in the report, sorted, with
  low-relevance items in a separate section. Missing an opening is far more costly
  than reading three extra lines.

Usage
-----
    python .claude/scripts/jm_scan.py                # scan, write report
    python .claude/scripts/jm_scan.py --dry-run      # scan, print, do not record as seen
    python .claude/scripts/jm_scan.py --limit 20     # cap detail fetches (testing)
    python .claude/scripts/jm_scan.py --since 2026-08-01   # ignore deadlines before this
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

sys_path_added = os.path.dirname(os.path.abspath(__file__))

JM_DIR = r"F:\Academic Website\job_market_2026"
STATE = os.path.join(JM_DIR, "state", "seen_positions.json")
# Scoring weights live in jm_score.py, calibrated with Moritz on 25 Aug 2026.
REPORT_DIR = os.path.join(JM_DIR, "reports")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
EJM_LIST = "https://econjobmarket.org/positions"
EJM_POS = "https://econjobmarket.org/positions/%s"
POLITE_DELAY = 1.0  # seconds between detail fetches


# --------------------------------------------------------------------------- io
def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", errors="replace")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------- parsing
def strip_html(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)          # handles &#039;, &eacute;, &amp; and the rest
    s = s.replace("&reg;", "").replace("&times;", "")
    return re.sub(r"\s+", " ", s).strip()


def field_after(text, label, stop_labels, maxlen=400):
    """Pull the run of text following `label` up to the next known label."""
    i = text.find(label)
    if i < 0:
        return ""
    rest = text[i + len(label):]
    cut = len(rest)
    for s in stop_labels:
        j = rest.find(s)
        if 0 <= j < cut:
            cut = j
    return rest[:cut].strip(" :\u2013-")[:maxlen].strip()


# Exactly as EJM renders them. Guessing these wrong makes one field swallow the next.
LABELS = ["Advertiser:", "Field(s) of specialization:", "Position type(s):",
          "Location of job:", "Deadline:", "Application deadline:",
          "Posting end date:", "Ad text:",
          "Current search status:", "Target date for applications:",
          "Application procedure", "Submission materials required", "Recommenders:",
          "Salary:", "Job start date:", "Job duration:", "Degree required:",
          "Interviews:", "Announcement:", "Featured postings"]


def clean_deadline(raw):
    """'31 Dec 2026 midnight UTC ( accepting... )' -> '31 Dec 2026'."""
    if not raw:
        return ""
    for cut in (" midnight", " (", " Posting", " Current", " Ad text"):
        i = raw.find(cut)
        if i > 0:
            raw = raw[:i]
    return raw.strip(" :,")[:60]


def parse_position(html_text, pid):
    t = strip_html(html_text)
    anchor = "Login/Register Translate this website "
    k = t.find(anchor)
    if k >= 0:
        t = t[k + len(anchor):]
    title = t.split("Advertiser:")[0].strip()[:200] if "Advertiser:" in t else ""
    return {
        "id": pid,
        "source": "EJM",
        "url": EJM_POS % pid,
        "title": title,
        "advertiser": field_after(t, "Advertiser:", LABELS),
        "fields": field_after(t, "Field(s) of specialization:", LABELS),
        "position_type": field_after(t, "Position type(s):", LABELS, 120),
        "location": field_after(t, "Location of job:", LABELS, 160),
        "deadline": clean_deadline(field_after(t, "Deadline:", LABELS, 120)
                                   or field_after(t, "Application deadline:", LABELS, 120)),
        "target_date": clean_deadline(field_after(t, "Target date for applications:",
                                                  LABELS, 60)),
        "status": field_after(t, "Current search status:", LABELS, 60),
        "letters": field_after(t, "Recommenders:", LABELS, 20),
        "text_excerpt": t[:1200],
    }


def list_position_ids(max_pages=10):
    ids, page = [], 1
    while page <= max_pages:
        url = EJM_LIST if page == 1 else "%s?page=%d" % (EJM_LIST, page)
        try:
            html_text = fetch(url)
        except Exception as exc:            # noqa: BLE001 - report and stop paging
            sys.stderr.write("warn: listing page %d failed: %s\n" % (page, exc))
            break
        found = re.findall(r"/positions/(\d+)", html_text)
        fresh = [i for i in dict.fromkeys(found) if i not in ids]
        if not fresh:
            break
        ids.extend(fresh)
        page += 1
        time.sleep(POLITE_DELAY)
    return ids


# --------------------------------------------------------------------- scoring
if sys_path_added not in sys.path:
    sys.path.insert(0, sys_path_added)
import jm_score          # noqa: E402  (path must be set first)


# ---------------------------------------------------------------------- report
def write_report(new_positions, dry_run, prefix="scan"):
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # rescores go to their own file so they never clobber a daily new-postings report
    path = os.path.join(REPORT_DIR, "%s_%s.md" % (prefix, stamp))

    scored = []
    for p in new_positions:
        scored.append((jm_score.score(p), p))
    scored.sort(key=lambda r: -r[0]["total"])
    keep = [r for r in scored if r[0]["in_set"]]
    drop = [r for r in scored if not r[0]["in_set"]]

    lines = ["# Job market scan — %s" % stamp, "",
             "%d posting(s) scanned. **%d in the choice set** (fit score >= %d); "
             "%d below threshold." % (len(scored), len(keep), jm_score.THRESHOLD, len(drop)),
             "",
             "Fit scores are calibrated to the survey of 25 August 2026. Below-threshold "
             "postings are listed at the end rather than deleted, so a mis-tuned weight "
             "can be caught.", ""]

    lines.append("## In the choice set (%d)" % len(keep))
    lines.append("")
    if not keep:
        lines.append("_None._")
        lines.append("")
    for r, p in keep:
        lines.append("### %d — %s" % (r["total"], p["title"] or "(untitled)"))
        lines.append("")
        lines.append("- **Institution:** %s" % (p["advertiser"] or "?"))
        lines.append("- **Location:** %s" % (p["location"] or "?"))
        lines.append("- **Type:** %s" % (p["position_type"] or "?"))
        lines.append("- **Fields:** %s" % (p["fields"] or "?"))
        lines.append("- **Deadline:** %s%s" % (
            p["deadline"] or "not stated",
            ("   (target date: %s)" % p["target_date"]) if p.get("target_date") else ""))
        if p.get("status"):
            lines.append("- **Search status:** %s" % p["status"])
        lines.append("- **Letters:** %s" % (p["letters"] or "?"))
        lines.append("- **Link:** %s" % p["url"])
        lines.append("- **Score %d** — %s" % (r["total"], "; ".join(
            "%s: %s" % (k, v) for k, v in r["breakdown"].items())))
        lines.append("")

    lines.append("## Below threshold (%d) — not in the choice set" % len(drop))
    lines.append("")
    for r, p in drop:
        why = "; ".join(r["gates"]) if r["gates"] else "score %d below %d" % (
            r["total"], jm_score.THRESHOLD)
        lines.append("- **%d** · %s — *%s* — %s" % (
            r["total"], p["title"] or "(untitled)", p["advertiser"] or "?", why))
        lines.append("  %s" % p["url"])
    lines.append("")

    body = chr(10).join(lines)
    if dry_run:
        print(body)
        return None, keep, drop
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path, keep, drop


# ------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="cap detail fetches")
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--rescore", action="store_true",
                    help="re-score everything already cached, without fetching")
    args = ap.parse_args()

    seen = load_json(STATE, {"seen": {}, "last_scan": None})
    seen_ids = set(seen.get("seen", {}).keys())

    if args.rescore:
        cached = list(seen.get("seen", {}).values())
        sys.stderr.write("rescoring %d cached posting(s), no fetching" % len(cached) + chr(10))
        path, keep, drop = write_report(cached, args.dry_run, prefix="rescore")
        if path:
            print("report: %s" % path)
        print("in choice set: %d   below threshold: %d" % (len(keep), len(drop)))
        return 0

    ids = list_position_ids(args.max_pages)
    fresh = [i for i in ids if i not in seen_ids]
    sys.stderr.write("listing: %d ids, %d new\n" % (len(ids), len(fresh)))
    if args.limit:
        fresh = fresh[:args.limit]

    positions = []
    for n, pid in enumerate(fresh, 1):
        try:
            positions.append(parse_position(fetch(EJM_POS % pid), pid))
        except Exception as exc:            # noqa: BLE001
            sys.stderr.write("warn: position %s failed: %s\n" % (pid, exc))
            continue
        sys.stderr.write("  fetched %d/%d\r" % (n, len(fresh)))
        time.sleep(POLITE_DELAY)
    sys.stderr.write("\n")

    path, keep, drop = write_report(positions, args.dry_run)

    if not args.dry_run:
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for p in positions:
            rec = dict(p)
            rec["first_seen"] = stamp
            seen["seen"][p["id"]] = rec
        seen["last_scan"] = stamp
        save_json(STATE, seen)
        print("report: %s" % path)
        print("new: %d (%d in choice set, %d below threshold)   total tracked: %d"
              % (len(positions), len(keep), len(drop), len(seen["seen"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
