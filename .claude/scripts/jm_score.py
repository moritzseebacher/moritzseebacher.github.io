#!/usr/bin/env python3
"""Fit scoring for job postings, 0-100, calibrated with Moritz on 25 August 2026.

Imported by jm_scan.py. Kept separate so the scoring model can be re-tuned and the
whole cached history re-scored without touching the fetching code.

The model
---------
Four things can put a posting below 50 outright, regardless of everything else. They
are gates, not weights, because the calibration showed geography cannot rescue a bad
field: Moritz cut the IWH Halle W1 -- German, junior, a research institute, and right
on his doorstep -- purely because the field was financial economics.

    GATES          unrelated field | senior-only | outside Europe | starts before autumn 2027

Everything that passes the gates is scored on five components summing to 100:

    field match          40   core / adjacent / open
    geography            25   Munich and Karlsruhe heaviest, then BW+Bavaria, Germany, DACH, Europe
    position family      20   tenure-track first, then institute economist, lecturer, postdoc
    institution type      8   econ departments and institutes level, business schools just below
    infrastructure        7   named data access, research centre, ERC/SFB, start-up package

Calibration targets from the survey (the model is checked against these in --selftest):
    Zurich postdoc, econ of education and labor, Switzerland      -> IN
    OECD Paris junior economist                                   -> IN
    IWH Halle W1, financial economics, Germany                    -> OUT (field)
    Institut Polytechnique de Paris postdoc, experimental         -> OUT (field)
    Bonn W3 professorship                                         -> OUT (seniority)
"""

import re
from datetime import datetime, timezone

THRESHOLD = 50

# --------------------------------------------------------------------- fields
CORE = [
    "labor economics", "labour economics", "economics of education",
    "labor and demographic", "labour and demographic", "human capital",
    "education", "labor", "labour",
]
ADJACENT = [
    "applied micro", "microeconomics", "public economics", "public",
    "personnel", "network", "inequality", "big data", "data science",
    "development", "demographic", "political economy", "urban", "migration",
    "health economics", "econometrics",
]
OPEN = ["any field", "all fields", "open field", "any area"]
# Everything not matched above is UNRELATED and gated out: finance, macro,
# monetary, IO, trade, environmental, agricultural, experimental, behavioral,
# management information technology, operations, marketing, accounting.


def field_class(pos):
    # Match on the ad's own field list. The title is used only when no field list
    # exists: titles carry marketing words ("Empirical Management Research") that
    # collide with field keywords and drag unrelated postings into the choice set.
    hay = (pos.get("fields") or "").strip().lower()
    if not hay:
        hay = (pos.get("title") or "").strip().lower()
    if not hay:
        return "open"
    if any(k in hay for k in CORE):
        return "core"
    if any(k in hay for k in OPEN):
        return "open"
    if any(k in hay for k in ADJACENT):
        return "adjacent"
    return "unrelated"


FIELD_POINTS = {"core": 40, "adjacent": 28, "open": 24, "unrelated": 0}

# ------------------------------------------------------------------ geography
GEO_TIERS = [
    (25, ["munich", "münchen", "muenchen", "karlsruhe"]),
    (21, ["bavaria", "bayern", "baden-württemberg", "baden-wurttemberg",
          "stuttgart", "mannheim", "heidelberg", "freiburg", "konstanz",
          "augsburg", "nuremberg", "nürnberg", "regensburg", "ulm"]),
    (17, ["germany", "deutschland", "berlin", "bonn", "cologne", "köln",
          "frankfurt", "hamburg", "halle", "leipzig", "dresden", "essen",
          "düsseldorf", "münster", "göttingen", "kiel", "bremen", "hannover"]),
    (14, ["austria", "vienna", "wien", "switzerland", "schweiz", "zurich",
          "zürich", "basel", "bern", "geneva", "lausanne", "st. gallen",
          "fribourg", "lucerne", "brig", "wallis"]),
    (10, ["netherlands", "amsterdam", "rotterdam", "tilburg", "utrecht",
          "maastricht", "groningen", "leiden", "belgium", "brussels", "leuven",
          "ghent", "luxembourg", "france", "paris", "toulouse", "lyon",
          "marseille", "cergy", "palaiseau", "denmark", "copenhagen", "aarhus",
          "sweden", "stockholm", "uppsala", "lund", "gothenburg", "norway",
          "oslo", "bergen", "trondheim", "finland", "helsinki", "italy",
          "milan", "milano", "rome", "bologna", "turin", "florence", "spain",
          "madrid", "barcelona", "bellaterra", "valencia", "portugal", "lisbon",
          "ireland", "dublin", "united kingdom", "london", "oxford",
          "cambridge", "manchester", "edinburgh", "bristol", "warwick",
          "poland", "warsaw", "czech", "prague", "hungary", "budapest",
          "greece", "athens", "estonia", "latvia", "lithuania", "vilnius",
          "slovenia", "croatia", "romania", "bulgaria", "iceland", "europe"]),
]


def geo_points(pos):
    hay = ((pos.get("location") or "") + " " + (pos.get("advertiser") or "")
           + " " + (pos.get("title") or "")).lower()
    for pts, keys in GEO_TIERS:
        if any(k in hay for k in keys):
            return pts, next(k for k in keys if k in hay)
    return 0, None


# ------------------------------------------------------------ position family
JUNIOR = ["assistant professor", "junior professor", "juniorprofessur", "w1",
          "postdoctoral", "postdoc", "post-doc", "lecturer", "research fellow",
          "research associate"]
# Neutral: says nothing about seniority either way. Must NOT rescue a senior title --
# the WZB "Director" posting was typed "Other academic" and slipped through as open rank.
NEUTRAL = ["other academic", "other nonacademic", "research assistant"]
SENIOR = ["full professor", "tenured professor", "associate professor", "w3",
          "w2", "chair", "director", "reader", "senior lecturer"]


def seniority(pos):
    hay = ((pos.get("position_type") or "") + " " + (pos.get("title") or "")).lower()
    has_j = any(k in hay for k in JUNIOR)
    has_s = any(k in hay for k in SENIOR)
    if has_s and not has_j:
        return "senior_only"
    if has_j and has_s:
        return "open_rank"
    if has_j:
        return "junior"
    return "unknown"


def family_points(pos):
    hay = ((pos.get("position_type") or "") + " " + (pos.get("title") or "")
           + " " + (pos.get("advertiser") or "")).lower()
    if any(k in hay for k in ["assistant professor", "junior professor",
                              "juniorprofessur", "tenure track", "tenure-track", "w1"]):
        return 20, "tenure-track / assistant professor"
    if any(k in hay for k in ["research economist", "senior economist", "economist",
                              "central bank", "bundesbank", "oecd", "ecb"]):
        return 16, "institute or central bank economist"
    if "lecturer" in hay:
        return 14, "lecturer"
    if any(k in hay for k in ["postdoc", "post-doc", "postdoctoral",
                              "research fellow", "research associate"]):
        return 12, "postdoc / fellow"
    return 8, "other"


# --------------------------------------------------------------- institution
INSTITUTE = ["institute", "institut", "ifo", "zew", "iza", "diw", "iab", "wzb",
             "iwh", "cesifo", "bundesbank", "central bank", "oecd",
             "federal reserve", "research center", "research centre", "cnrs",
             "max planck", "csic"]
BSCHOOL = ["business school", "school of management", "business administration",
           "management", "school of business", "bocconi", "insead", "hec"]


def institution_points(pos):
    hay = (pos.get("advertiser") or "").lower()
    if any(k in hay for k in INSTITUTE):
        return 8, "research institute / central bank"
    if any(k in hay for k in BSCHOOL):
        return 6, "business or management school"
    if "economics" in hay or "économie" in hay or "ökonom" in hay:
        return 8, "economics department"
    if any(k in hay for k in ["public policy", "public health", "social science"]):
        return 6, "policy or social science school"
    return 4, "other"


# ------------------------------------------------------------ infrastructure
INFRA = {
    "administrative data": 3, "register data": 3, "microdata": 3,
    "data access": 3, "research data": 2, "linked data": 2,
    "erc": 2, "sfb": 2, "cluster of excellence": 2, "crc ": 2,
    "start-up package": 2, "startup package": 2, "research budget": 2,
    "research funding": 1, "research centre": 1, "research center": 1,
    "graduate school": 1,
}


def infra_points(pos):
    hay = (pos.get("text_excerpt") or "").lower()
    pts, hits = 0, []
    for k, w in INFRA.items():
        if k in hay:
            pts += w
            hits.append(k.strip())
    return min(pts, 7), hits


# ------------------------------------------------------------------- language
OTHER_LANG = ["in french", "french language", "command of french",
              "in italian", "italian language", "in dutch", "dutch language",
              "in spanish", "spanish language", "in danish", "danish language",
              "in swedish", "swedish language", "in norwegian", "in portuguese",
              "in polish", "in czech"]


def language_penalty(pos):
    hay = (pos.get("text_excerpt") or "").lower()
    for k in OTHER_LANG:
        if k in hay:
            return 8, k
    return 0, None


# ----------------------------------------------------------------- start date
def start_too_early(pos, today=None):
    """True only when a start date is stated AND clearly before autumn 2027."""
    raw = (pos.get("start_date") or "")
    if not raw:
        m = re.search(r"job start date:?\s*([0-9]{1,2} \w+ [0-9]{4})",
                      (pos.get("text_excerpt") or ""), re.I)
        raw = m.group(1) if m else ""
    if not raw:
        return False, None
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(raw.strip(), fmt).date()
            return (d.year < 2027 or (d.year == 2027 and d.month < 7)), raw
        except ValueError:
            continue
    return False, None


# ---------------------------------------------------------------- expiry / EU
def expired(pos, today=None):
    raw = (pos.get("deadline") or "").strip()
    if not raw:
        return False
    today = today or datetime.now(timezone.utc).date()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).date() < today
        except ValueError:
            continue
    return False


# ------------------------------------------------------------------- scoring
def score(pos, today=None):
    """Return dict with total, breakdown, gates, and a one-line explanation."""
    gates = []

    fc = field_class(pos)
    if fc == "unrelated":
        gates.append("field is unrelated (%s)" % (pos.get("fields") or "none stated")[:60])

    sen = seniority(pos)
    if sen == "senior_only":
        gates.append("senior-only posting (%s)" % (pos.get("position_type") or "?")[:50])

    geo, geo_hit = geo_points(pos)
    if geo == 0:
        gates.append("outside Europe")

    early, when = start_too_early(pos, today)
    if early:
        gates.append("starts before autumn 2027 (%s)" % when)

    if expired(pos, today):
        gates.append("deadline passed (%s)" % pos.get("deadline"))

    fam, fam_label = family_points(pos)
    inst, inst_label = institution_points(pos)
    infra, infra_hits = infra_points(pos)
    lang, lang_hit = language_penalty(pos)

    total = FIELD_POINTS[fc] + geo + fam + inst + infra - lang
    total = max(0, min(100, total))

    if gates:
        total = min(total, 35)      # gated postings are never in the choice set

    breakdown = {
        "field": "%s (+%d)" % (fc, FIELD_POINTS[fc]),
        "geography": "%s (+%d)" % (geo_hit or "none", geo),
        "family": "%s (+%d)" % (fam_label, fam),
        "institution": "%s (+%d)" % (inst_label, inst),
        "infrastructure": "%s (+%d)" % (", ".join(infra_hits) or "none", infra),
    }
    if lang:
        breakdown["language"] = "%s (-%d)" % (lang_hit, lang)

    return {"total": total, "in_set": total >= THRESHOLD and not gates,
            "gates": gates, "breakdown": breakdown, "field_class": fc,
            "seniority": sen}


# ------------------------------------------------------------------ selftest
CALIBRATION = [
    (dict(title="Postdoc in Economics of Education and Labor Economics",
          fields="Labor and Demographic Economics - Economics of Education",
          advertiser="Department of Business Administration, University of Zurich",
          location="Plattenstrasse 14, Zurich, 8032, Switzerland",
          position_type="Postdoctoral Scholar", deadline="1 Sep 2026",
          text_excerpt="research data access and a strong research centre"), True,
     "Zurich postdoc"),
    (dict(title="Junior Economists/ Economists", fields="Any field",
          advertiser="Economics Department, OECD",
          location="2 rue Andre Pascal, Paris, 75016, France",
          position_type="Other academic, Other nonacademic", deadline="1 Nov 2026",
          text_excerpt="microdata and research funding"), True, "OECD Paris"),
    (dict(title="Assistant Professor (W1) in Financial Economics",
          fields="Finance - Macroeconomics; Monetary",
          advertiser="Halle Institute for Economic Research (IWH)",
          location="Halle an der Saale, SA, 06108, Germany",
          position_type="Assistant Professor", deadline="29 Nov 2026",
          text_excerpt=""), False, "IWH Halle (field)"),
    (dict(title="Post-doctoral position in Experimental Economics",
          fields="Behavioral Economics - Experimental Economics",
          advertiser="Economics, Institut Polytechnique de Paris",
          location="CREST, Palaiseau, 91220, France",
          position_type="Postdoctoral Scholar", deadline="1 Nov 2026",
          text_excerpt=""), False, "IP Paris (field)"),
    (dict(title="W3 Professorships in Economics", fields="Any field",
          advertiser="Department of Economics, University of Bonn",
          location="Adenauerallee 24-42, Bonn, 53113, Germany",
          position_type="Full Professor", deadline="1 Sep 2026",
          text_excerpt=""), False, "Bonn W3 (seniority)"),
]


def selftest():
    ok = True
    print("Calibration self-test (survey answers of 25 Aug 2026)")
    print("-" * 64)
    for pos, want_in, label in CALIBRATION:
        r = score(pos)
        good = (r["in_set"] == want_in)
        ok &= good
        print("%-28s score %3d  in_set=%-5s expected=%-5s  %s"
              % (label, r["total"], r["in_set"], want_in, "OK" if good else "MISMATCH"))
        if r["gates"]:
            print("%-28s   gated: %s" % ("", "; ".join(r["gates"])))
    print("-" * 64)
    print("ALL PASS" if ok else "FAILURES -- model does not match the calibration")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
