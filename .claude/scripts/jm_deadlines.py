#!/usr/bin/env python3
"""Read the application tracker and report what is at risk.

The rule Moritz specified: raise a letter-writer flag when an application's deadline
is inside 14 days AND the letter writers have not yet confirmed in the tracker that
they sent the letter. Quiet otherwise -- no routine emails.

Whichever of `first_review_date` and `deadline` comes first is what counts, because a
first-review or target date is a real deadline even when the ad calls the later date
the deadline.

Usage:
    python .claude/scripts/jm_deadlines.py            # default 14-day window
    python .claude/scripts/jm_deadlines.py --days 21
    python .claude/scripts/jm_deadlines.py --all      # list every open application
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime

TRACKER = r"F:\Academic Website\job_market_2026\06_application_tracker.csv"

DATE_FORMATS = [
    "%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%d.%m.%Y", "%d/%m/%Y",
    "%b %d, %Y", "%B %d, %Y", "%Y/%m/%d",
]

TRUTHY = {"yes", "y", "true", "done", "sent", "in", "confirmed", "1"}


def parse_date(raw):
    """Return a date, or None. Never guess -- an unparseable date is reported as such."""
    if not raw:
        return None
    s = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def truthy(v):
    return (v or "").strip().lower() in TRUTHY


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = ap.parse_args()

    today = parse_date(args.today) if args.today else date.today()

    if not os.path.exists(TRACKER):
        sys.stderr.write("tracker not found: %s\n" % TRACKER)
        return 1

    with open(TRACKER, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    urgent, upcoming, unparsed, submitted = [], [], [], []

    for r in rows:
        inst = (r.get("institution") or "").strip()
        if not inst or "example only" in (r.get("notes") or "").lower():
            continue

        d_dead = parse_date(r.get("deadline"))
        d_rev = parse_date(r.get("first_review_date"))
        candidates = [d for d in (d_dead, d_rev) if d]
        effective = min(candidates) if candidates else None

        if effective is None:
            unparsed.append((inst, r.get("deadline"), r.get("first_review_date")))
            continue

        days = (effective - today).days
        letters_ok = truthy(r.get("letters_in"))
        is_submitted = bool((r.get("submitted_date") or "").strip())

        rec = {
            "institution": inst,
            "position": (r.get("position") or "").strip(),
            "effective": effective,
            "days": days,
            "which": "first review" if (d_rev and effective == d_rev) else "deadline",
            "n_letters": (r.get("n_letters") or "?").strip(),
            "letters_route": (r.get("letters_route") or "").strip(),
            "letters_ok": letters_ok,
            "submitted": is_submitted,
            "link": (r.get("ad_link") or "").strip(),
        }

        if days < 0:
            continue                      # passed; nothing to chase
        if is_submitted and letters_ok:
            submitted.append(rec)
            continue
        if days <= args.days and not letters_ok:
            urgent.append(rec)
        else:
            upcoming.append(rec)

    urgent.sort(key=lambda r: r["days"])
    upcoming.sort(key=lambda r: r["days"])

    print("Deadline check - %s (window: %d days)" % (today.isoformat(), args.days))
    print("=" * 62)

    print("\nLETTER FLAG - within %d days, letters NOT confirmed (%d)"
          % (args.days, len(urgent)))
    if not urgent:
        print("  none")
    for r in urgent:
        print("  ! %-38s %s in %d day(s)  [%s]" %
              (r["institution"][:38], r["which"], r["days"], r["effective"]))
        print("      %s | %s letters via %s%s" %
              (r["position"][:44] or "?", r["n_letters"],
               r["letters_route"] or "route not recorded",
               "" if r["submitted"] else " | NOT YET SUBMITTED"))

    if args.all:
        print("\nOTHER OPEN APPLICATIONS (%d)" % len(upcoming))
        for r in upcoming:
            print("  - %-38s %s in %d day(s)  letters_in=%s" %
                  (r["institution"][:38], r["which"], r["days"],
                   "yes" if r["letters_ok"] else "no"))
        print("\nDONE - submitted with letters in (%d)" % len(submitted))
        for r in submitted:
            print("  . %s" % r["institution"])

    if unparsed:
        print("\nUNREADABLE DATES (%d) - fix these, they are invisible to the check"
              % len(unparsed))
        for inst, d1, d2 in unparsed:
            print("  ? %-38s deadline=%r first_review=%r" % (inst[:38], d1, d2))

    print("\n%d application(s) tracked, %d need a letter chase." % (len(rows), len(urgent)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
