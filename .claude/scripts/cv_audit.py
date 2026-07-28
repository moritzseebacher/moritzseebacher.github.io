# -*- coding: utf-8 -*-
"""
CV format auditor — enforces the rules in .claude/commands/cv-check.md.

Usage:
    python .claude/scripts/cv_audit.py [path/to/CV.docx]

With no argument it audits the newest CV_Academic_Moritz_Seebacher_*.docx in the
repo root. Exits 0 if every rule passes, 1 otherwise.

Every check here corresponds to a numbered rule in the skill document. If you
change a design rule, change it in BOTH places.
"""
import sys, io, os, re, glob, zipfile, collections
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'

# ------------------------------------------------------------------ the spec
FONT = 'Arial'
SZ_BODY, SZ_SMALL, SZ_NAME, SZ_SUBTITLE = 22, 20, 56, 28
ALLOWED_SIZES = {SZ_BODY, SZ_SMALL, SZ_NAME, SZ_SUBTITLE}
TEXT_WIDTH, COL_DATE, COL_BODY = 10204, 2268, 7936
HEAD_SIG = ('240', '80', '240', 'bottom', 'single', '4', '1')   # before/after/line + border
BODY_SPACING = {'after': '80', 'line': '276', 'lineRule': 'auto'}
ALLOWED_SPACING = {
    'after=80,line=276,lineRule=auto',            # all body/table paragraphs
    'after=80,before=240,line=240,lineRule=auto',  # section headings
    'after=80,before=480,line=240,lineRule=auto',  # name
    'after=160,line=240,lineRule=auto',            # subtitle date
    'after=0,before=360,line=240,lineRule=auto',   # closing place/date line
}
SECTIONS = [
    'Contact Information', 'Fields', 'Current Position', 'Education',
    'Research Visits', 'Job Market Paper', 'Publications', 'Working Papers',
    'Work in Progress', 'Policy Publications',
    'Conferences, Workshops, and Invited Seminars', 'Teaching Experience',
    'Awards and Scholarships', 'Refereeing', 'Research Experience',
    'Outreach and Volunteering', 'Languages', 'Technical Skills',
]
LOWER_OK = {'a', 'an', 'the', 'and', 'or', 'in', 'of', 'for', 'to', 'on', 'at', 'by', 'vs.'}

fails, warns = [], []


def fail(rule, msg):
    fails.append('[%s] %s' % (rule, msg))


def warn(rule, msg):
    warns.append('[%s] %s' % (rule, msg))


# ------------------------------------------------------------------- loading
def find_docx():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    c = sorted(glob.glob(os.path.join(root, 'CV_Academic_Moritz_Seebacher_*.docx')),
               key=os.path.getmtime)
    if not c:
        print('No CV .docx found in %s' % root)
        sys.exit(1)
    return c[-1]


path = sys.argv[1] if len(sys.argv) > 1 else find_docx()
root = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
print('Auditing: %s\n' % path)


def ptext(p):
    buf = []
    for n in p.iter():
        t = n.tag[len(W):]
        if t == 't':
            buf.append(n.text or '')
        elif t == 'tab':
            buf.append('\t')
        elif t == 'br':
            buf.append('\n')
    return ''.join(buf)


def spacing_sig(sp):
    return ','.join('%s=%s' % (k[len(W):], v) for k, v in sorted(sp.attrib.items()))


paras = list(root.iter(W + 'p'))
tables = list(root.iter(W + 'tbl'))

# ------------------------------------------------- 1. no floating shapes/junk
n_shapes = (len(list(root.iter(MC + 'AlternateContent'))) +
            len(list(root.iter(W + 'drawing'))) + len(list(root.iter(W + 'pict'))))
if n_shapes:
    fail('R1', '%d floating shape(s) present. Section rules must be paragraph '
                'bottom borders, never anchored line shapes.' % n_shapes)

# ---------------------------------------------------- 2. section headings
heads = []
for p in paras:
    pPr = p.find(W + 'pPr')
    if pPr is None or pPr.find(W + 'pBdr') is None:
        continue
    sp, bd = pPr.find(W + 'spacing'), pPr.find(W + 'pBdr')[0]
    sig = (sp.get(W + 'before'), sp.get(W + 'after'), sp.get(W + 'line'),
           bd.tag[len(W):], bd.get(W + 'val'), bd.get(W + 'sz'), bd.get(W + 'space'))
    heads.append((ptext(p), sig, pPr))

names = [h[0] for h in heads]
if names != SECTIONS:
    fail('R2', 'Section list/order differs from spec.\n      expected: %s\n      found:    %s'
         % (SECTIONS, names))
for txt, sig, pPr in heads:
    if sig != HEAD_SIG:
        fail('R3', 'Heading %r format %s != spec %s' % (txt, sig, HEAD_SIG))
    if pPr.find(W + 'keepNext') is None:
        fail('R4', 'Heading %r missing <w:keepNext/> (may be orphaned at a page break)' % txt)
    if txt != txt.strip():
        fail('R5', 'Heading %r has leading/trailing whitespace' % txt)
    for i, wd in enumerate(txt.split()):
        if i and wd.lower() in LOWER_OK:
            continue
        if wd[:1].islower():
            fail('R6', 'Heading %r is not Title Case (word %r)' % (txt, wd))

# --------------------------------------------------------- 3. table geometry
for t in tables:
    tblPr = t.find(W + 'tblPr')
    w = tblPr.find(W + 'tblW').get(W + 'w')
    if w != str(TEXT_WIDTH):
        fail('R7', 'Table width %s != %d (page text width)' % (w, TEXT_WIDTH))
    ind = tblPr.find(W + 'tblInd')
    if ind is None or ind.get(W + 'w') != '0':
        fail('R8', 'Table indent must be 0 so content aligns with the section rule')
    cm = tblPr.find(W + 'tblCellMar')
    if cm is None or cm.find(W + 'left').get(W + 'w') != '0':
        fail('R9', 'Table left cell margin must be 0 (content flush with heading text)')
    grid = tuple(g.get(W + 'w') for g in t.find(W + 'tblGrid'))
    if grid not in ((str(TEXT_WIDTH),), (str(COL_DATE), str(COL_BODY))):
        fail('R10', 'Table grid %s is neither full-width nor the %d/%d two-column layout'
             % (list(grid), COL_DATE, COL_BODY))
    for tr in t.findall(W + 'tr'):
        trPr = tr.find(W + 'trPr')
        if trPr is None or trPr.find(W + 'cantSplit') is None:
            fail('R11', 'Row missing <w:cantSplit/> (entry could break across pages)')

if list(root.iter(W + 'trHeight')):
    fail('R12', 'Fixed row heights present. Row height must be content-driven, '
                'otherwise one-line entries get padded and gaps go uneven.')

# ------------------------------------------------------- 4. paragraph spacing
sigs = collections.Counter(spacing_sig(s) for s in root.iter(W + 'spacing'))
for s in sigs:
    if s not in ALLOWED_SPACING:
        fail('R13', 'Unapproved spacing spec %r (allowed: %s)' % (s, sorted(ALLOWED_SPACING)))
for p in paras:
    pPr = p.find(W + 'pPr')
    if pPr is None:
        fail('R14', 'Paragraph %r has no explicit formatting' % ptext(p)[:40])
        continue
    if pPr.find(W + 'spacing') is None:
        fail('R14', 'Paragraph %r has no explicit spacing' % ptext(p)[:40])

# ------------------------------------------------------------- 5. typography
for r in root.iter(W + 'r'):
    rPr = r.find(W + 'rPr')
    txt = ''.join(t.text or '' for t in r.iter(W + 't'))
    if not txt.strip():
        continue
    if rPr is None:
        fail('R15', 'Run %r has no run properties (font/size not pinned)' % txt[:40])
        continue
    rf = rPr.find(W + 'rFonts')
    if rf is None or rf.get(W + 'ascii') != FONT:
        fail('R15', 'Run %r is not %s' % (txt[:40], FONT))
    sz = rPr.find(W + 'sz')
    if sz is None or int(sz.get(W + 'val')) not in ALLOWED_SIZES:
        fail('R16', 'Run %r has size %s; allowed half-point sizes: %s'
             % (txt[:40], sz.get(W + 'val') if sz is not None else None, sorted(ALLOWED_SIZES)))

# ---------------------------------------------------------- 6. text hygiene
lines = [ptext(p) for p in paras if ptext(p).strip()]
joined = '\n'.join(lines)

for l in lines:
    if l != l.strip():
        fail('R17', 'Leading/trailing whitespace: %r' % l)
    if '  ' in l:
        fail('R18', 'Double space: %r' % l)
    if '\t' in l or '\n' in l:
        fail('R19', 'Manual tab or line break inside a paragraph: %r' % l)
    if '—' in l:
        fail('R20', 'Em dash (use en dash for ranges): %r' % l)
    if "'" in l:
        fail('R21', "Straight apostrophe (use ’): %r" % l)
    if ' ' in l:
        warn('R22', 'Non-breaking space: %r' % l)
    if re.search(r'\d\s*-\s*\d', l):
        fail('R23', 'Hyphen between numbers (ranges take an en dash): %r' % l)
    if re.search(r'\d{2}/\d{4}\s*-', l):
        fail('R23', 'Hyphen in a date range: %r' % l)
    if ';' in l:
        fail('R35', 'Semicolon: %r. Lists separate with commas throughout.' % l)

# italic is reserved for publication venues and status markers, never field labels
for r in root.iter(W + 'r'):
    rPr = r.find(W + 'rPr')
    if rPr is None or rPr.find(W + 'i') is None:
        continue
    txt = ''.join(t.text or '' for t in r.iter(W + 't')).strip()
    if txt.endswith(':'):
        fail('R36', 'Italic field label %r. Italic marks journal/series names and '
                    'status only; inline labels (Host:, Supervisor:, Invited '
                    'seminars:) are roman.' % txt)

# date ranges must be  MM/YYYY – MM/YYYY  or  MM/YYYY – present
for l in lines:
    if re.fullmatch(r'\d{2}/\d{4}.*', l) and '–' in l:
        if not re.fullmatch(r'\d{2}/\d{4} – (\d{2}/\d{4}|present)', l):
            fail('R24', 'Malformed date range %r (want "MM/YYYY – MM/YYYY" or '
                        '"MM/YYYY – present")' % l)

# location lines need a comma between place and country
PLACES = ('Germany', 'Spain', 'U.S.')
for l in lines:
    if l.endswith(PLACES) and ',' not in l:
        fail('R25', 'Location line missing comma: %r' % l)

# ongoing roles say "present", never "today"/"now"
for bad in ('today', 'now', 'ongoing'):
    if re.search(r'– %s\b' % bad, joined):
        fail('R26', 'Ongoing date uses %r; the CV says "present"' % bad)

# institution name casing
if re.search(r'\bIfo\b', joined):
    fail('R27', '"Ifo" must be lowercase "ifo"')
if 'Ludwig-Maximilians-University' in joined:
    fail('R28', 'Use "LMU Munich" (matches the Teaching Experience entries)')

# serial comma in coauthor lists
for m in re.finditer(r'\(with ([^)]+)\)', joined):
    a = m.group(1)
    if a.count(',') >= 1 and ' and ' not in a:
        fail('R29', 'Coauthor list %r missing serial "and"' % a)
    if ' and ' in a and a.count(',') >= 2 and not re.search(r',\s+and ', a):
        fail('R29', 'Coauthor list %r missing the serial (Oxford) comma' % a)

# every teaching entry carries a level tag
teach = False
for i, l in enumerate(lines):
    if l == 'Teaching Experience':
        teach = True
        continue
    if teach and l == 'Conferences and Workshops':
        break
    if teach and (l.startswith('Supervisor') or l.startswith('Teaching Assistant')):
        if '(Bachelor)' not in lines[i - 1] and '(Master)' not in lines[i - 1]:
            fail('R30', 'Teaching entry %r has no (Bachelor)/(Master) level tag' % lines[i - 1])

# --------------------- 7. hyperlinks: contact email only, never paper titles
rels = ET.fromstring(zipfile.ZipFile(path).read('word/_rels/document.xml.rels'))
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
targets = {r.get('Id'): r.get('Target') for r in rels
           if r.get('Type', '').endswith('/hyperlink')}
for h in root.iter(W + 'hyperlink'):
    rid = h.get(RNS + 'id')
    tgt = targets.get(rid, '')
    if tgt != 'mailto:seebacher@ifo.de':
        fail('R34', 'Hyperlink to %r. The CV links the contact email only — paper '
                    'titles stay plain text so no entry looks more "clickable" than '
                    'another.' % tgt)

# --------------------------------------------------- 8. PDF is in sync
pdf = os.path.splitext(path)[0] + '.pdf'
if not os.path.exists(pdf):
    fail('R31', 'No exported PDF next to the .docx (%s)' % os.path.basename(pdf))
elif os.path.getmtime(pdf) < os.path.getmtime(path):
    fail('R31', 'PDF is older than the .docx — re-export before committing')

# --------------------------------------------------- 9. website link matches
repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
idx = os.path.join(repo, 'index.md')
if os.path.exists(idx):
    md = open(idx, encoding='utf-8').read()
    linked = re.findall(r'\(/(CV_Academic_[^)]+\.pdf)\)', md)
    if not linked:
        fail('R32', 'index.md does not link a CV PDF')
    for name in linked:
        if not os.path.exists(os.path.join(repo, name)):
            fail('R32', 'index.md links %r but that file is not on disk' % name)
        elif name != os.path.basename(pdf):
            fail('R32', 'index.md links %r but the current PDF is %r'
                 % (name, os.path.basename(pdf)))
    stray = [os.path.basename(f) for f in glob.glob(os.path.join(repo, 'CV_Academic_*.pdf'))
             if os.path.basename(f) not in linked]
    if stray:
        warn('R33', 'Unlinked CV PDF(s) still in the repo: %s' % stray)

# ------------------------------------------------------------------- report
print('Sections:   %d' % len(heads))
print('Tables:     %d   Rows: %d' % (len(tables), sum(len(t.findall(W + 'tr')) for t in tables)))
print('Paragraphs: %d' % len(paras))
print('Spacing specs in use: %d' % len(sigs))
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
print('All format rules pass.')
