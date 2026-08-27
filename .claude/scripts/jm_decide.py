#!/usr/bin/env python3
"""Per-advert approval: list candidates, record decisions, append tracker rows.

Moritz decides advert by advert. This script holds the state so that decisions
persist across scans:

    added    -> a row exists in the tracker; never asked about again
    skipped  -> he said no; never asked about again
    pending  -> he wants a closer look; ASKED AGAIN on the next scan

Without the pending state a scan either re-asks about everything already
decided, or silently loses the adverts he had not made his mind up about.

Usage:
    python .claude/scripts/jm_decide.py --list              # candidates awaiting a decision
    python .claude/scripts/jm_decide.py --add 12601
    python .claude/scripts/jm_decide.py --skip 12594
    python .claude/scripts/jm_decide.py --defer 12593       # ask me again next time
    python .claude/scripts/jm_decide.py --status            # counts by decision
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone

JM_DIR = r"F:\Academic Website\job_market_2026"
STATE = os.path.join(JM_DIR, "state", "seen_positions.json")
DECISIONS = os.path.join(JM_DIR, "state", "decisions.json")
CONFIG = os.path.join(JM_DIR, "state", "config.json")
TRACKER = os.path.join(JM_DIR, "06_application_tracker.csv")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jm_score  # noqa: E402

COLUMNS = ["institution", "country", "position", "platform", "ad_link", "deadline",
           "first_review_date", "documents_required", "n_letters", "letters_route",
           "cover_letter_customised", "submitted_date", "letters_in", "signal_sent",
           "interview_date", "interview_outcome", "flyout_date", "offer", "notes"]


def load(path, default):
    if not os.path.exists(path):
        return default
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


def iso(raw):
    """EJM prints '27 Sep 2026'. The tracker and the deadline checker want ISO."""
    if not raw:
        return ""
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return ""          # unparseable: leave blank rather than write a wrong date


def country_of(pos):
    loc = (pos.get("location") or "").strip()
    return loc.split(",")[-1].strip() if "," in loc else loc


def days_left(rec, today=None):
    """Days until the advert closes, using whichever of the target date and the
    deadline comes first. None when no date can be parsed."""
    today = today or datetime.now(timezone.utc).date()
    dates = [iso(rec.get("target_date")), iso(rec.get("deadline"))]
    dates = [d for d in dates if d]
    if not dates:
        return None
    first = min(dates)
    return (datetime.strptime(first, "%Y-%m-%d").date() - today).days


def is_urgent(rec, score, cfg, today=None):
    """A breakthrough: close fit AND closing soon.

    An advert that closes before Moritz starts applying must NOT be hidden -- that
    is exactly the case he asked to be told about, because he may accelerate for it.
    """
    d = days_left(rec, today)
    if d is None or d < 0:
        return False
    return (score >= cfg.get("alert_score_min", 70)
            and d <= cfg.get("alert_days", 30))


def candidates(seen, decisions, cfg=None, today=None):
    """Adverts that pass pre-screening and still need a decision.

    Returns (score, id, record, was_deferred, urgent, days_left). Only adverts whose
    deadline has already PASSED are dropped.
    """
    cfg = cfg or {}
    out = []
    for pid, rec in seen.items():
        d = decisions.get(pid, {}).get("decision")
        if d in ("added", "skipped"):
            continue
        r = jm_score.score(rec)
        if not r["in_set"]:
            continue
        dl = days_left(rec, today)
        if dl is not None and dl < 0:
            continue                      # already closed
        out.append((r["total"], pid, rec, d == "pending",
                    is_urgent(rec, r["total"], cfg, today), dl))
    out.sort(key=lambda x: (not x[4], -x[0]))     # urgent first, then by score
    return out


def append_row(rec, score):
    exists = os.path.exists(TRACKER)
    rows = []
    if exists:
        with io.open(TRACKER, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    if any((r.get("ad_link") or "") == rec.get("url") for r in rows):
        return False                      # already tracked; never duplicate
    row = {c: "" for c in COLUMNS}
    row.update({
        "institution": rec.get("advertiser", ""),
        "country": country_of(rec),
        "position": rec.get("title", ""),
        "platform": "EJM",
        "ad_link": rec.get("url", ""),
        "deadline": iso(rec.get("deadline")),
        "first_review_date": iso(rec.get("target_date")),
        "n_letters": rec.get("letters", ""),
        "letters_route": "EJM portal",
        "cover_letter_customised": "no",
        "letters_in": "no",
        "signal_sent": "no",
        "notes": "fit score %d; added %s%s" % (
            score, datetime.now(timezone.utc).date().isoformat(),
            "; deadline as printed: %s" % rec.get("deadline")
            if rec.get("deadline") and not iso(rec.get("deadline")) else ""),
    })
    with io.open(TRACKER, "a", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, fieldnames=COLUMNS).writerow(row)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--add")
    ap.add_argument("--skip")
    ap.add_argument("--defer")
    args = ap.parse_args()

    seen = load(STATE, {"seen": {}}).get("seen", {})
    dec = load(DECISIONS, {"decisions": {}})
    cfg = load(CONFIG, {})
    applying = cfg.get("applying", True)
    horizon = None if applying else cfg.get("applying_from")
    D = dec["decisions"]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if args.status:
        from collections import Counter
        c = Counter(v["decision"] for v in D.values())
        print("decisions:", dict(c) or "none yet")
        cands = candidates(seen, D, cfg)
        print("awaiting a decision:", len(cands))
        print("URGENT breakthrough alerts:", sum(1 for c in cands if c[4]))
        if horizon:
            print("NOT APPLYING YET - applying from %s. Watchlist only; nothing is" % horizon)
            print("dropped except adverts already closed. Urgent close fits still alert.")
        return 0

    for flag, name in ((args.add, "added"), (args.skip, "skipped"), (args.defer, "pending")):
        if not flag:
            continue
        pid = flag.strip()
        if pid not in seen:
            sys.stderr.write("unknown posting id %s\n" % pid)
            return 1
        rec = seen[pid]
        if name == "added":
            score = jm_score.score(rec)["total"]
            wrote = append_row(rec, score)
            print("%s tracker row for %s - %s" % (
                "wrote" if wrote else "already present, skipped duplicate for",
                pid, (rec.get("title") or "")[:60]))
        D[pid] = {"decision": name, "date": stamp,
                  "title": rec.get("title", ""), "url": rec.get("url", "")}
        save(DECISIONS, dec)
        print("recorded: %s -> %s" % (pid, name))
        return 0

    # default: --list
    cands = candidates(seen, D, cfg)
    if horizon:
        print("Not applying until %s - watchlist only, no decisions requested." % horizon)
        print()
    if not cands:
        print("No adverts awaiting a decision.")
        return 0
    print("%d advert(s) awaiting a decision\n" % len(cands))
    for score, pid, rec, was_pending, urgent, dl in cands:
        print("%s[%s] %d  %s%s" % ("** URGENT ** " if urgent else "", pid, score,
                                   (rec.get("title") or "?")[:60],
                                   "   (deferred earlier)" if was_pending else ""))
        print("      %s" % (rec.get("advertiser") or "?")[:70])
        print("      %s | deadline %s%s" % (
            country_of(rec) or "?", rec.get("deadline") or "not stated",
            ("  target %s" % rec["target_date"]) if rec.get("target_date") else ""))
        if dl is not None:
            print("      closes in %d day(s)%s" % (
                dl, "  -- BEFORE you start applying" if horizon and
                iso(rec.get("deadline")) and iso(rec.get("deadline")) < horizon else ""))
        print("      %s" % rec.get("url"))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
