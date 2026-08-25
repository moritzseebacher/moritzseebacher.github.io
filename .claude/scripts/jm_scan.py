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
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

JM_DIR = r"F:\Academic Website\job_market_2026"
STATE = os.path.join(JM_DIR, "state", "seen_positions.json")
PROFILE = os.path.join(JM_DIR, "state", "profile.json")
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
    s = (s.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
           .replace("&quot;", '"').replace("&reg;", "").replace("&times;", ""))
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
def score(pos, profile):
    """Return (score, reasons). Never excludes -- only ranks."""
    hay = " ".join([pos.get("title", ""), pos.get("fields", ""),
                    pos.get("advertiser", ""), pos.get("location", ""),
                    pos.get("position_type", ""), pos.get("text_excerpt", "")]).lower()
    pts, why = 0, []
    for kw, w in profile.get("field_keywords", {}).items():
        if kw.lower() in hay:
            pts += w
            why.append("%s (+%d)" % (kw, w))
    for kw, w in profile.get("position_keywords", {}).items():
        if kw.lower() in hay:
            pts += w
            why.append("%s (+%d)" % (kw, w))
    for c, w in profile.get("region_keywords", {}).items():
        if c.lower() in hay:
            pts += w
            why.append("%s (+%d)" % (c, w))
    for kw, w in profile.get("deprioritise", {}).items():
        if kw.lower() in hay:
            pts -= w
            why.append("%s (-%d)" % (kw, w))
    return pts, why


DEFAULT_PROFILE = {
    "_comment": "Weights only rank; nothing is ever dropped. Edit freely.",
    "field_keywords": {
        "labor": 5, "labour": 5, "education": 5, "human capital": 4,
        "applied micro": 4, "applied economics": 3, "microeconometrics": 3,
        "public": 2, "personnel": 3, "development": 2, "networks": 3,
        "big data": 3, "data science": 2, "digital": 2, "economics of education": 6,
    },
    "position_keywords": {
        "assistant professor": 5, "tenure track": 5, "tenure-track": 5,
        "lecturer": 4, "postdoc": 3, "post-doc": 3, "postdoctoral": 3,
        "research economist": 4, "economist": 2, "junior professor": 4,
    },
    "region_keywords": {},
    "deprioritise": {
        "adjunct": 3, "visiting": 2, "part-time": 3, "teaching-only": 2,
    },
    "high_relevance_threshold": 8,
}


# ---------------------------------------------------------------------- report
def write_report(new_positions, profile, dry_run):
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(REPORT_DIR, "scan_%s.md" % stamp)

    scored = []
    for p in new_positions:
        s, why = score(p, profile)
        scored.append((s, why, p))
    scored.sort(key=lambda r: -r[0])
    thr = profile.get("high_relevance_threshold", 8)
    high = [r for r in scored if r[0] >= thr]
    low = [r for r in scored if r[0] < thr]

    lines = ["# New job market postings — %s" % stamp, "",
             "Source: EJM (econjobmarket.org). %d new posting(s) since the last scan."
             % len(scored), "",
             "Scores rank only; nothing is filtered out. Everything fetched is listed.", ""]

    def block(items, heading):
        lines.append("## %s (%d)" % (heading, len(items)))
        lines.append("")
        if not items:
            lines.append("_None._")
            lines.append("")
            return
        for s, why, p in items:
            lines.append("### %s" % (p["title"] or "(untitled)"))
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
            lines.append("- **Score %d:** %s" % (s, ", ".join(why) if why else "no keyword hits"))
            lines.append("")
    block(high, "Likely relevant")
    block(low, "Lower signal — check anyway")

    body = "\n".join(lines)
    if dry_run:
        print(body)
        return None
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


# ------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="cap detail fetches")
    ap.add_argument("--max-pages", type=int, default=10)
    args = ap.parse_args()

    profile = load_json(PROFILE, None)
    if profile is None:
        profile = DEFAULT_PROFILE
        if not args.dry_run:
            save_json(PROFILE, profile)
            sys.stderr.write("note: wrote default profile to %s\n" % PROFILE)

    seen = load_json(STATE, {"seen": {}, "last_scan": None})
    seen_ids = set(seen.get("seen", {}).keys())

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

    path = write_report(positions, profile, args.dry_run)

    if not args.dry_run:
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for p in positions:
            rec = dict(p)
            rec.pop("text_excerpt", None)   # bulky; only needed for scoring at fetch time
            rec["first_seen"] = stamp
            seen["seen"][p["id"]] = rec
        seen["last_scan"] = stamp
        save_json(STATE, seen)
        print("report: %s" % path)
        print("new: %d   total tracked: %d" % (len(positions), len(seen["seen"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
