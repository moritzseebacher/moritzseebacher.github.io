# -*- coding: utf-8 -*-
"""
CV consistency auditor — the pre-push gate for the published CV.

Usage:
    python .claude/scripts/cv_audit.py [path/to/CV.pdf]

With no argument it audits the CV PDF that index.md links. Exits 0 if every
rule passes, 1 otherwise.

WHAT CHANGED (10 September 2026). The CV used to be a Word document that lived
untracked in the repo root and was exported to PDF by hand, and this script
audited that .docx: fonts, table grids, paragraph spacing, forty-odd rules that
existed because Word will silently let any of them drift. The CV is now built
from LaTeX in the application package, which makes every one of those rules
structurally impossible to break, so they are gone.

What LaTeX cannot guarantee is the part that was always the real risk: that the
CV and the website say the same thing, and that the copy served to the public
carries no referee contact details. That is what remains here. The rule numbers
of the surviving checks are unchanged (R31-R34, R37, R38) so that references to
them elsewhere -- CLAUDE.md, commit messages -- still point at the same rule.

The CV source is tex/cv.tex in the application package, which is deliberately
outside this repository. This script therefore reads the built PDF, not the
source: it checks the artefact that is actually served.
"""
import sys, io, os, re, glob, subprocess, datetime

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTACT_EMAIL = 'seebacher@ifo.de'
STALE_DAYS = 60

# The public CV's sections, in order. "References" is absent by design: the
# committee copy carries the four letter writers with their email addresses,
# the website copy does not. See the \ifdefined\publicCV branch in tex/cv.tex.
SECTIONS = [
    'Fields', 'Current Position', 'Education', 'Research Visits',
    'Job Market Paper', 'Publications', 'Working Papers', 'Work in Progress',
    'Policy Publications', 'Conferences, Workshops, and Invited Seminars',
    'Teaching Experience', 'Awards and Scholarships', 'Refereeing',
    'Research Experience', 'Outreach and Volunteering', 'Skills',
]

fails, warns = [], []


def fail(rule, msg):
    fails.append('%s  %s' % (rule, msg))


def warn(rule, msg):
    warns.append('%s  %s' % (rule, msg))


def squash(s):
    s = s.replace('’', "'").replace('‘', "'")
    s = s.replace('“', '"').replace('”', '"')
    s = s.replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


# ------------------------------------------------------- 1. find the artefact
idx_path = os.path.join(REPO, 'index.md')
if not os.path.exists(idx_path):
    print('index.md not found at %s' % idx_path)
    sys.exit(1)
md = io.open(idx_path, encoding='utf-8').read()

linked = re.findall(r'\(/(CV_Academic_[^)]+\.pdf)\)', md)
if not linked:
    fail('R32', 'index.md does not link a CV PDF')
elif len(set(linked)) > 1:
    fail('R32', 'index.md links more than one CV PDF: %s' % sorted(set(linked)))

if len(sys.argv) > 1:
    pdf = os.path.abspath(sys.argv[1])
elif linked:
    pdf = os.path.join(REPO, linked[0])
else:
    sys.exit(1)

if not os.path.exists(pdf):
    fail('R32', 'index.md links %r but that file is not on disk' % os.path.basename(pdf))
    print('FAILED (1)\n  x ' + fails[0])
    sys.exit(1)

stray = [os.path.basename(f) for f in glob.glob(os.path.join(REPO, 'CV_Academic_*.pdf'))
         if os.path.basename(f) not in linked]
if stray:
    warn('R33', 'Unlinked CV PDF(s) still in the repo: %s' % stray)

# The .docx is no longer the source of the CV. One left in the repo root means
# somebody edited the old artefact and the two will drift.
old_docx = [os.path.basename(f) for f in glob.glob(os.path.join(REPO, 'CV_Academic_*.docx'))]
if old_docx:
    warn('R33', 'Superseded CV .docx still in the repo root: %s. The CV is built '
                'from tex/cv.tex in the application package now; delete these so '
                'nobody edits the wrong file.' % old_docx)

# ------------------------------------------------------------ 2. extract text
# pdftotext is already a hard dependency of this workflow: build.ps1 refuses to
# distribute the job market paper without it. Same rule here -- an unverifiable
# CV does not get pushed.
try:
    out = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    text = out.stdout.decode('utf-8', 'replace')
except (OSError, FileNotFoundError):
    print('BLOCKED: pdftotext not found, so the published CV cannot be read and')
    print('         none of the consistency rules can run. Install poppler/xpdf')
    print('         (it is already required to publish the job market paper), or')
    print('         check the CV by hand. Not verified means do not push.')
    sys.exit(1)

if not text.strip():
    fail('R31', 'No text extracted from %s -- is it a real PDF?' % os.path.basename(pdf))
    print('FAILED (1)\n  x ' + fails[0])
    sys.exit(1)

# Page footers have to come out before anything is compared. An abstract that
# spans a page break otherwise has "2 of 3" extracted into the middle of it, and
# the verbatim check below fails on a document that is in fact correct.
FOOTER_RE = re.compile(r'^\s*\d+\s+of\s+\d+\s*$')
lines = [l.rstrip() for l in text.splitlines() if l.strip() and not FOOTER_RE.match(l)]
flat = squash('\n'.join(lines))
pages = len([pg for pg in text.split('\f') if pg.strip()])

# ------------------------------------------- 3. referee details stay off the web
# The single most consequential rule in this file. The public CV is built with
# \publicCV defined, which drops the References section; this verifies the
# artefact rather than trusting the build.
mails = sorted({m.lower() for m in re.findall(r'[\w.\-]+@[\w.\-]+\w', text)})
leaked = [m for m in mails if m != CONTACT_EMAIL]
if leaked:
    fail('R34', 'The published CV carries %s. Only %s may appear: this copy is '
                'public, and the letter writers\' addresses are not. Rebuild with '
                '".\\build.ps1 web", which drops the References section.'
         % (', '.join(leaked), CONTACT_EMAIL))
if re.search(r'(?m)^\s*References\s*$', text):
    fail('R34', 'The published CV has a References section. The website copy '
                'must be the \\publicCV build, which omits it.')

# --------------------------------------------------------- 4. sections present
found = [l.strip() for l in lines if l.strip() in SECTIONS]
seen = []
for s in found:
    if s not in seen:
        seen.append(s)
if seen != SECTIONS:
    missing = [s for s in SECTIONS if s not in seen]
    extra = [s for s in seen if s not in SECTIONS]
    fail('R2', 'Section list/order differs from spec.\n      expected: %s\n'
               '      found:    %s%s%s'
         % (SECTIONS, seen,
            '\n      missing:  %s' % missing if missing else '',
            '\n      unexpected: %s' % extra if extra else ''))

# ------------------------------------------------------------ 5. text hygiene
if '—' in text:
    fail('R20', 'Em dash in the CV (ranges take an en dash)')
if re.search(r'\bIfo\b', text):
    fail('R27', '"Ifo" must be lowercase "ifo"')
if 'Ludwig-Maximilians-University' in text:
    fail('R28', 'Use "LMU Munich" (matches the Teaching Experience entries)')
for bad in ('today', 'now', 'ongoing'):
    if re.search(r'–\s*%s\b' % bad, flat):
        fail('R26', 'Ongoing date uses %r; the CV says "present"' % bad)

for m in re.finditer(r'\(with ([^)]+)\)', flat):
    a = m.group(1)
    if a.count(',') >= 1 and ' and ' not in a:
        fail('R29', 'Coauthor list %r missing serial "and"' % a)
    if ' and ' in a and a.count(',') >= 2 and not re.search(r',\s+and ', a):
        fail('R29', 'Coauthor list %r missing the serial (Oxford) comma' % a)

for l in lines:
    m = re.match(r'^(\d{2}/\d{4}\s*\S?\s*\d{2}/\d{4}|\d{2}/\d{4}\s*\S?\s*present)', l.strip())
    if re.match(r'^\d{2}/\d{4}', l.strip()) and not m:
        fail('R24', 'Malformed date range %r (want "MM/YYYY - MM/YYYY" or '
                    '"MM/YYYY - present", en dash)' % l.strip()[:40])
    if m and '–' not in m.group(0):
        fail('R23', 'Date range %r does not use an en dash' % m.group(0))

# --------------------------------------- 6. the CV and the site say the same thing
# R37 — anything stated in both places must agree. Separator style may differ
# (the site uses "·", the CV uses ", "); the set of entries may not.
def norm(s):
    return {x.strip().rstrip('.').lower() for x in re.split(r'[·,]', s) if x.strip()}

cv_fields = None
for i, l in enumerate(lines):
    if l.strip() == 'Fields' and i + 1 < len(lines):
        cv_fields = norm(lines[i + 1])
        break
m = re.search(r'^\*\*Fields:\*\*\s*(.+)$', md, re.M)
site_fields = norm(m.group(1)) if m else None
if cv_fields is None:
    fail('R37', 'No Fields section found in the CV')
elif site_fields is None:
    fail('R37', 'index.md has no "**Fields:**" line to check the CV against')
elif cv_fields != site_fields:
    fail('R37', 'Fields differ.\n      CV only:   %s\n      site only: %s'
         % (sorted(cv_fields - site_fields) or '-',
            sorted(site_fields - cv_fields) or '-'))

# Expected graduation is stated in both places and is the fact most likely to
# go stale in one of them.
m_cv = re.search(r'Expected graduation:\s*([A-Za-z]+ \d{4})', flat, re.I)
m_site = re.search(r'Expected graduation:\s*([A-Za-z]+ \d{4})', md, re.I)
if m_cv and m_site and m_cv.group(1).lower() != m_site.group(1).lower():
    fail('R37', 'Expected graduation differs: CV says %r, site says %r'
         % (m_cv.group(1), m_site.group(1)))

# Titles that appear on both sides must match verbatim.
for label, needle in (('JMP', 'Career Effects of Online Social Network Access at Labor Market Entry'),
                      ('working paper', 'Multidimensional Skills on LinkedIn Profiles'),
                      ('publication', 'Complementarity of Bicycles and Road Infrastructure'),
                      ('work in progress', 'Alumni Networks, First Job Placements'),
                      ('policy paper', 'Wie Fahrräder die Bildungschancen')):
    in_cv = squash(needle) in flat
    in_site = needle in md
    if in_cv != in_site:
        fail('R37', '%s title is on the %s but not the %s: %r'
             % (label, 'CV' if in_cv else 'site', 'site' if in_cv else 'CV', needle))

# R38 — every abstract the site shows is quoted verbatim in the CV too. A new
# paper draft must land in both places in the same pass; a CV still carrying
# last month's abstract is exactly the drift this rule exists to catch. Widened
# 10 Sep 2026 from the job market paper alone to all four abstracts, once the
# work-in-progress abstract came back into the CV.
sections = re.split(r'(?m)^##\s+', md)[1:]
checked = 0
for sec in sections:
    heading = sec.splitlines()[0].split('{')[0].strip()
    for span in re.findall(r'<span class="abstract-text">(.*?)</span>', sec, re.S):
        checked += 1
        if squash(span) not in flat:
            fail('R38', 'The %s abstract on the site is not in the CV verbatim — '
                        'rebuild the CV from tex/cv.tex (".\\build.ps1 web") or fix '
                        'index.md' % heading)
if not checked:
    fail('R38', 'index.md has no abstract-text spans at all — has the page changed shape?')

# ------------------------------------------------------------- 7. freshness
m = re.search(r'Last updated:\s*([A-Za-z]+ \d{1,2}, \d{4})', flat)
if not m:
    warn('R39', 'No "Last updated" line found in the CV')
else:
    try:
        d = datetime.datetime.strptime(m.group(1), '%B %d, %Y').date()
        age = (datetime.date.today() - d).days
        if age > STALE_DAYS:
            warn('R39', 'CV was last updated %s (%d days ago)' % (m.group(1), age))
    except ValueError:
        warn('R39', 'Unparseable "Last updated" date: %r' % m.group(1))

# ------------------------------------------------------------------- report
print('CV:         %s' % os.path.basename(pdf))
print('Pages:      %d' % pages)
print('Sections:   %d' % len(seen))
print('Abstracts:  %d checked against index.md' % checked)
print('Emails:     %s' % (', '.join(mails) or 'none'))
print()
if warns:
    print('WARNINGS (%d)' % len(warns))
    for w in warns:
        print('  ~ ' + w)
    print()
if fails:
    print('FAILED (%d)' % len(fails))
    for f in fails:
        print('  x ' + f)
    sys.exit(1)
print('All CV consistency rules pass.')
