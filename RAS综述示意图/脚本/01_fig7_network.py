#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 8 - the RAS signalling network, drawn as a cell-biology illustration.

Rebuilt 2026-11-02 (author: the previous version read as a flow chart of boxes and
text; draw it the way Nature/Science mechanism figures are drawn - membrane,
molecules and nucleus as pictures - with the same type size and page fit as
Figures 1-7). What changed against the box version:
  · the whole figure is one picture of a cell: lipid bilayer across the top, the
    four receptor classes as receptor glyphs with their ligands, RAS anchored to
    the inner leaflet by its lipidated tail, effectors as shaded domain bodies,
    the nucleus (with DNA) entered by ERK, vesicles and actin filaments drawn as
    the outputs they are; panel b is four small cell vignettes;
  · NF1/RASA1 sit at the membrane between RAS-GTP and RAS-GDP, on the hydrolysis
    arc they catalyse; SOS1 and the tissue-restricted GEFs feed the exchange arc;
  · one type size throughout (7.5 pt, printed about 6 pt after the 0.81 page fit),
    9 pt bold panel letters - the contract of Figures 1-7;
  · drug-class tags keep the marker code (circle approved / square in trials /
    triangle preclinical or abandoned), placed at the node they act on;
  · dropped: the tag "blocking one trunk de-represses the other" - section 3.3
    states the library holds no primary measurement for that claim; the
    "effector use differs by allele and tissue" line is now a note, not a tag.
Nodes, arrows and the ERK feedback are those of sections 3.1-3.5 (membrane
anchoring 2.2, PI3K-AKT-mTOR 3.3, ERK-dependent transcription 3.3/3.5).

The artwork is written as SVG (vector gradients, text kept as text) and converted:
PNG with rsvg-convert, PDF with headless Chrome (cairo, used by rsvg-convert,
embeds the space glyph as a Type 3 font, which the Arial-only gate rejects).

Usage: python3 01_fig7_network.py <root>
Out:   <root>/figures/Fig7_RAS_signalling_network.{svg,pdf,png}
"""
import math, os, shutil, subprocess, sys, tempfile
from PIL import ImageFont

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '..')
FIG = os.path.join(ROOT, 'figures')
NAME = 'Fig7_RAS_signalling_network'
os.makedirs(FIG, exist_ok=True)

W, H = 180.0, 0.0                        # mm; double column, as Figures 1-7
PT = 25.4 / 72
FS = 7.5 * PT                             # the one text size
PNs = 9.0 * PT                            # panel letters
LH = FS * 1.27                            # line pitch
INK, GREY, WHITE = '#1A1A1A', '#59656B', '#FFFFFF'
COL = {'rec': '#8FB3CC', 'adapt': '#4F86B4', 'gef': '#5F8FA8', 'off': '#9AAAB8',
       'on': '#D7263D', 'gap': '#7D8A93', 'mapk': '#2E6F9E', 'pi3k': '#1C7C54',
       'ral': '#6A4C93', 'other': '#A0522D', 'lig': '#E9A23B', 'red': '#C8102E'}
SANS = "Arial, Helvetica, sans-serif"

_F = {k: ImageFont.truetype('/System/Library/Fonts/Supplemental/%s.ttf' % f, 1000)
      for k, f in (('r', 'Arial'), ('b', 'Arial Bold'), ('i', 'Arial Italic'),
                   ('bi', 'Arial Bold Italic'))}


# ------------------------------------------------------------ primitives -----
def mix(c, t, f):
    a = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(t[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(round(x + (y - x) * f) for x, y in zip(a, b))


def segs(s, bold=False):
    """'<i>KRAS</i> G12C' -> [(text, italic, bold)]."""
    out, it, bd = [], False, bold
    while s:
        k = min([p for p in (s.find('<i>'), s.find('</i>'), s.find('<b>'),
                             s.find('</b>')) if p >= 0] or [len(s)])
        if k:
            out.append((s[:k], it, bd))
            s = s[k:]
            continue
        for tag, f in (('<i>', 'it1'), ('</i>', 'it0'), ('<b>', 'bd1'), ('</b>', 'bd0')):
            if s.startswith(tag):
                if f == 'it1': it = True
                elif f == 'it0': it = False
                elif f == 'bd1': bd = True
                else: bd = bold
                s = s[len(tag):]
                break
    return out


def tw(s, bold=False, size=FS):
    w = 0.0
    for t, it, bd in segs(s, bold):
        w += _F[('b' if bd else 'r') if not it else ('bi' if bd else 'i')].getlength(t)
    return w / 1000.0 * size


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Doc:
    def __init__(self):
        self.L = {k: [] for k in ('bg', 'mem', 'under', 'link', 'body', 'over', 'text')}
        self.grad = {}
        self.boxes = []                   # text extents, for the overlap audit

    def add(self, layer, s):
        self.L[layer].append(s)

    def gradient(self, col):
        gid = 'g' + col[1:]
        if gid not in self.grad:
            self.grad[gid] = (
                '<radialGradient id="%s" cx="0.36" cy="0.30" r="0.80" fx="0.32" '
                'fy="0.24"><stop offset="0" stop-color="%s"/><stop offset="0.55" '
                'stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
                % (gid, mix(col, WHITE, 0.50), col, mix(col, '#000000', 0.25)))
        return 'url(#%s)' % gid

    def text(self, x, y, s, anchor='start', color=INK, bold=False, size=FS,
             layer='text', rot=None, audit=True, opacity=None):
        """y is the visual centre of the line (cap height centred)."""
        w = tw(s, bold, size)
        yb = y + size * 0.355
        tf = ' transform="rotate(%.1f %.2f %.2f)"' % (rot, x, y) if rot else ''
        op = ' fill-opacity="%.2f"' % opacity if opacity else ''
        spans = ''.join(
            '<tspan%s%s>%s</tspan>' % (' font-style="italic"' if it else '',
                                        ' font-weight="bold"' if bd else '', esc(t))
            for t, it, bd in segs(s, bold))
        self.add(layer, '<text x="%.2f" y="%.2f" font-size="%.3f" fill="%s" '
                 'text-anchor="%s"%s%s xml:space="preserve">%s</text>'
                 % (x, yb, size, color, anchor, tf, op, spans))
        if audit and not rot:
            x0 = x - (w if anchor == 'end' else w / 2 if anchor == 'middle' else 0)
            self.boxes.append((x0, y - size * 0.40, x0 + w, y + size * 0.40, s))
        return w

    def lines(self, x, y, rows, **kw):
        for k, r in enumerate(rows):
            self.text(x, y + k * LH, r, **kw)

    def svg(self):
        body = ''.join(''.join(self.L[k]) for k in self.L)
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" '
                'viewBox="0 0 %g %g" font-family="%s">'
                '<defs>%s%s</defs>%s</svg>' % (W, H, W, H, SANS,
                                               ''.join(self.grad.values()), DEFS, body))


DEFS = (
    '<linearGradient id="exo" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#E4EEF6"/><stop offset="1" stop-color="#F1F6FA"/>'
    '</linearGradient>'
    '<linearGradient id="cyto" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FCF7F0"/><stop offset="1" stop-color="#F8F1E8"/>'
    '</linearGradient>'
    '<radialGradient id="head" cx="0.38" cy="0.32" r="0.75">'
    '<stop offset="0" stop-color="#F4D9A8"/><stop offset="1" stop-color="#D9A75A"/>'
    '</radialGradient>'
    '<radialGradient id="headpk" cx="0.38" cy="0.32" r="0.75">'
    '<stop offset="0" stop-color="#C6E5D2"/><stop offset="1" stop-color="#3E9A68"/>'
    '</radialGradient>'
    '<radialGradient id="nuc" cx="0.45" cy="0.25" r="0.8">'
    '<stop offset="0" stop-color="#EFE9F5"/><stop offset="1" stop-color="#DCD2E8"/>'
    '</radialGradient>'
    '<linearGradient id="card" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#F6F9FB"/><stop offset="1" stop-color="#EDF2F5"/>'
    '</linearGradient>'
    '<clipPath id="clipA"><rect x="0" y="0" width="180" height="123" rx="2.2"/></clipPath>'
)

D = Doc()


def pts_path(pts, close=True):
    return 'M' + ' L'.join('%.2f %.2f' % p for p in pts) + (' Z' if close else '')


def ell_pts(cx, cy, rx, ry, rot=0.0, n=56):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def body(lobes, col, layer='body', lw=0.32, shadow=True, hl=None):
    """Shaded molecule: union of lobes (cx, cy, rx, ry, rot) under one gradient.
    Drawn as stroke-then-fill so only the outer outline shows."""
    d = ' '.join(pts_path(ell_pts(*lo)) for lo in lobes)
    if shadow:
        D.add(layer, '<path d="%s" fill="#3A2A1A" fill-opacity="0.12" '
                     'transform="translate(0.45 0.6)"/>' % d)
    D.add(layer, '<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                 'stroke-linejoin="round"/>' % (d, mix(col, '#000000', 0.45), 2 * lw))
    # one gradient over the bounding box of all lobes
    D.add(layer, '<path d="%s" fill="%s"/>' % (d, D.gradient(col)))
    if hl:
        hx, hy, hrx, hry = hl
        D.add(layer, '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="#FFFFFF" '
                     'fill-opacity="0.28"/>' % (hx, hy, hrx, hry))


SHAPES = {
    'bi': lambda w, h: [(-0.19 * w, 0.02 * h, 0.33 * w, 0.48 * h, -8),
                        (0.20 * w, -0.03 * h, 0.31 * w, 0.45 * h, 10)],
    'tri': lambda w, h: [(-0.31 * w, 0.03 * h, 0.22 * w, 0.43 * h, 0),
                         (0.00 * w, -0.03 * h, 0.25 * w, 0.50 * h, 0),
                         (0.31 * w, 0.04 * h, 0.21 * w, 0.42 * h, 0)],
    'round': lambda w, h: [(0, 0, 0.5 * w, 0.5 * h, 0)],
    'kidney': lambda w, h: [(-0.22 * w, 0.06 * h, 0.30 * w, 0.44 * h, 20),
                            (0.18 * w, -0.05 * h, 0.34 * w, 0.48 * h, -12),
                            (0.05 * w, 0.22 * h, 0.22 * w, 0.26 * h, 0)],
}


def protein(cx, cy, w, h, label, col, shape='bi', tc=WHITE, rows=None,
            layer='body'):
    lobes = [(cx + a, cy + b, rx, ry, r) for a, b, rx, ry, r in SHAPES[shape](w, h)]
    body(lobes, col, layer=layer,
         hl=(cx - 0.20 * w, cy - 0.24 * h, 0.16 * w, 0.10 * h))
    rows = rows or [label]
    y0 = cy - (len(rows) - 1) * LH / 2
    for k, r in enumerate(rows):
        D.text(cx, y0 + k * LH, r, anchor='middle', color=tc, bold=(k == 0),
               audit=False)
        if tw(r, k == 0) > w * 0.92:
            print('  ! label wider than body:', r)


def head(p, q, col, size=1.25, layer='link'):
    """Filled arrowhead at q pointing away from p."""
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    a, b = size, size * 0.42
    pts = [q, (q[0] - a * math.cos(ang) + b * math.sin(ang),
               q[1] - a * math.sin(ang) - b * math.cos(ang)),
           (q[0] - a * math.cos(ang) - b * math.sin(ang),
            q[1] - a * math.sin(ang) + b * math.cos(ang))]
    D.add(layer, '<path d="%s" fill="%s"/>' % (pts_path(pts), col))


def arrow(p0, p1, c1=None, c2=None, col=INK, lw=0.42, end='head', dash=None,
          layer='link', hs=1.25):
    """Cubic connector p0 -> p1; end = head | tee | none."""
    c1 = c1 or p0
    c2 = c2 or p1
    tail = c2 if c2 != p1 else c1 if c1 != p1 else p0
    ang = math.atan2(p1[1] - tail[1], p1[0] - tail[0])
    q = p1
    if end == 'head':                    # stop the line inside the head
        q = (p1[0] - hs * 0.7 * math.cos(ang), p1[1] - hs * 0.7 * math.sin(ang))
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    D.add(layer, '<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f" fill="none" '
                 'stroke="%s" stroke-width="%.2f" stroke-linecap="round"%s/>'
          % (p0[0], p0[1], c1[0], c1[1], c2[0], c2[1], q[0], q[1], col, lw, da))
    if end == 'head':
        head(tail, p1, col, hs, layer)
    elif end == 'tee':
        nx, ny = -math.sin(ang), math.cos(ang)
        D.add(layer, '<path d="M%.2f %.2f L%.2f %.2f" stroke="%s" stroke-width="%.2f" '
                     'stroke-linecap="round"/>'
              % (p1[0] + nx, p1[1] + ny, p1[0] - nx, p1[1] - ny, col, lw * 1.6))


def marker(x, y, status, col=INK, s=1.0):
    if status == 'approved':
        D.add('text', '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>'
              % (x, y, 0.80 * s, col))
    elif status == 'clinical':
        D.add('text', '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
              % (x - 0.72 * s, y - 0.72 * s, 1.44 * s, 1.44 * s, col))
    else:
        D.add('text', '<path d="%s" fill="%s"/>' % (pts_path(
            [(x, y - 0.95 * s), (x + 0.88 * s, y + 0.62 * s),
             (x - 0.88 * s, y + 0.62 * s)]), col))


def tag(x, y, rows, status, color=INK):
    """Drug-class tag: status marker then text; rows wrap under the first."""
    if isinstance(rows, str):
        rows = [rows]
    marker(x + 0.9, y, status, color)
    D.lines(x + 2.6, y, rows, color=color)
    return x + 2.6 + max(tw(r) for r in rows)


# ============================================================ panel a ========
M = 22.0                     # membrane mid-plane
HR, HD = 0.60, 2.05          # head radius, head offset from mid-plane
BOT = 123.0                  # bottom of panel a

D.add('bg', '<g clip-path="url(#clipA)">')
D.add('bg', '<rect x="0" y="0" width="180" height="%.2f" fill="url(#exo)"/>' % M)
D.add('bg', '<rect x="0" y="%.2f" width="180" height="%.2f" fill="url(#cyto)"/>'
      % (M, BOT - M))
D.add('bg', '</g>')

# ---- receptors (drawn before the bilayer so heads can be omitted around them)
REC = '#8FB3CC'
gaps = []


def helix(x, y0, y1, w=1.35, col=REC, layer='body'):
    D.add(layer, '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
                 'fill="%s" stroke="%s" stroke-width="0.25"/>'
          % (x - w / 2, y0, w, y1 - y0, w / 2, D.gradient(col),
             mix(col, '#000000', 0.45)))


def rtk(cx):
    for s in (-1, 1):
        x = cx + s * 2.25
        body([(x + s * 0.3, 9.6, 1.9, 2.5, 0), (x + s * 0.1, 14.4, 1.7, 2.3, 0)], REC,
             shadow=False)
        helix(x, 16.5, 27.0, w=1.2)
        body([(x + s * 0.4, 28.6, 2.3, 1.9, 0)], REC, shadow=False)   # kinase domain
        for k, yy in enumerate((31.0,)):
            D.add('over', '<circle cx="%.2f" cy="%.2f" r="0.62" fill="%s" stroke="%s" '
                          'stroke-width="0.2"/>' % (x + s * 1.3, yy, '#F2C14E', '#9A6B00'))
    body([(cx, 6.3, 1.9, 1.3, 0)], COL['lig'], shadow=False)        # growth factor
    gaps.append((cx - 3.6, cx + 3.6))


def integrin(cx):
    for s, top in ((-1, 9.0), (1, 10.4)):
        x = cx + s * 1.6
        D.add('body', '<path d="M%.2f %.2f L%.2f %.2f L%.2f %.2f" fill="none" '
                      'stroke="%s" stroke-width="1.15" stroke-linecap="round" '
                      'stroke-linejoin="round"/>'
              % (x, top + 1.5, x, M + HD + 1.0, x + s * 0.9, 27.6,
                 mix(REC, '#000000', 0.15)))
        body([(x + s * 0.5, top, 2.0, 1.6, s * 20)], REC, shadow=False)
    # extracellular-matrix fibre
    pts = [(cx - 8 + k * 0.4, 5.6 + 0.55 * math.sin(k * 0.55)) for k in range(41)]
    D.add('body', '<path d="%s" fill="none" stroke="#B9A68F" stroke-width="0.9" '
                  'stroke-linecap="round"/>' % pts_path(pts, False))
    gaps.append((cx - 2.6, cx + 2.6))


def gpcr(cx):
    xs = [cx - 4.2 + k * 1.4 for k in range(7)]
    for k in range(6):                         # loops
        y = 16.9 if k % 2 else 27.1
        D.add('body', '<path d="M%.2f %.2f Q%.2f %.2f %.2f %.2f" fill="none" '
                      'stroke="%s" stroke-width="0.45"/>'
              % (xs[k], y, (xs[k] + xs[k + 1]) / 2, y + (-1.2 if k % 2 else 1.2),
                 xs[k + 1], y, mix(REC, '#000000', 0.3)))
    for k, x in enumerate(xs):
        helix(x, 17.0 - (k % 2) * 0.5, 27.0 + (k % 2) * 0.5, w=1.15)
    body([(cx + 0.3, 13.6, 1.3, 1.0, 0)], COL['lig'], shadow=False)
    gaps.append((cx - 5.0, cx + 5.0))


def immune(cx):
    for s in (-1, 1):
        x = cx + s * 1.25
        body([(x, 10.2, 1.4, 1.9, 0), (x, 14.6, 1.4, 1.9, 0)], REC, shadow=False)
        helix(x, 16.6, 27.0, w=1.1)
    for s in (-1, 1):                          # signalling chains with ITAM tails
        x = cx + s * 4.0
        helix(x, 18.0, 27.0, w=1.0, col='#6E9CC0')
        D.add('body', '<path d="M%.2f 27 L%.2f 30.2" stroke="#6E9CC0" '
                      'stroke-width="0.8" stroke-linecap="round"/>' % (x, x + s * 0.4))
    body([(cx, 6.6, 2.6, 1.5, 0)], '#C97B84', shadow=False)        # antigen
    gaps.append((cx - 4.8, cx + 4.8))


RX = {'rtk': 11.0, 'int': 31.0, 'gpcr': 48.0, 'imm': 66.0}
rtk(RX['rtk']); integrin(RX['int']); gpcr(RX['gpcr']); immune(RX['imm'])
for k, lb in (('rtk', 'RTK'), ('int', 'Integrin'), ('gpcr', 'GPCR'),
              ('imm', 'Immune receptor')):
    D.text(RX[k], 2.6, lb, anchor='middle')

# ---- lipid bilayer -----------------------------------------------------------
STEP = 1.36
PIP = []
x = 0.7
while x < 180:
    if not any(a - HR <= x <= b + HR for a, b in gaps):
        for side in (-1, 1):
            y = M + side * HD
            for dx in (-0.25, 0.25):
                D.add('mem', '<path d="M%.2f %.2f Q%.2f %.2f %.2f %.2f" fill="none" '
                             'stroke="#E2C89E" stroke-width="0.26"/>'
                      % (x + dx, y - side * 0.4, x + dx * 2.2, y - side * 1.1,
                         x + dx, M - side * 0.12))
            D.add('mem', '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="url(#head)"/>'
                  % (x, y, HR))
    x += STEP
D.text(178.5, 17.6, 'Plasma membrane', anchor='end', color=GREY)

# ---- marker key, in the free extracellular space -----------------------------
KX = 128.0
for k, (st, lb) in enumerate((('approved', 'Approved drug class'),
                              ('clinical', 'In clinical trials (phase I–III)'),
                              ('preclinical', 'Preclinical only, or abandoned'))):
    tag(KX, 3.6 + k * LH, lb, st)

# ---- adaptor / exchange-factor layer -----------------------------------------
protein(10.6, 35.4, 10.0, 6.4, 'GRB2', COL['adapt'], 'tri')
protein(23.6, 36.6, 13.0, 8.0, 'SOS1', COL['adapt'], 'bi')
protein(36.6, 38.4, 10.0, 6.4, 'SHP2', COL['adapt'], 'tri')
protein(59.0, 36.8, 15.0, 7.2, 'GEFs', COL['gef'], 'kidney')
D.text(47.0, 43.2, 'tissue-restricted', color=GREY)

arrow((32.0, 28.6), (35.4, 34.8), (33.2, 30.6), (34.8, 32.6))              # integrin
arrow((14.2, 30.6), (33.2, 35.4), (22.0, 28.0), (29.0, 29.6))              # RTK -> SHP2
arrow((47.0, 30.4), (55.0, 33.6), (48.6, 32.4), (52.0, 33.2))              # GPCR
arrow((65.0, 30.6), (62.0, 33.6), (64.6, 31.8), (63.2, 32.8))              # immune

# ---- the switch ----------------------------------------------------------------
GDP, GTP, SY = 89.0, 125.0, 39.6


def ras(cx, cy, col, nuc, tside, tc):
    # lipidated hypervariable tail into the inner leaflet
    tx = cx + tside * 4.2
    D.add('under', '<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f" fill="none" '
                   'stroke="%s" stroke-width="0.55" stroke-linecap="round"/>'
          % (cx + tside * 2.5, cy - 5.0, cx + tside * 3.5, cy - 8.0, tx, cy - 10.0,
             tx, M + HD + 0.6, mix(col, '#000000', 0.25)))
    zz = [(tx + (0.45 if k % 2 else -0.45), M + HD + 0.6 - k * 0.75) for k in range(5)]
    D.add('over', '<path d="%s" fill="none" stroke="#E07B00" stroke-width="0.5" '
                  'stroke-linejoin="round"/>' % pts_path(zz, False))
    body([(cx, cy, 7.6, 6.0, 0), (cx + 2.6, cy - 3.0, 3.2, 2.4, 0)], col,
         hl=(cx - 2.4, cy - 2.8, 2.6, 1.3))
    D.text(cx, cy - 1.7, 'RAS', anchor='middle', color=tc, bold=True, audit=False)
    nw = 9.0
    D.add('body', '<rect x="%.2f" y="%.2f" width="%.2f" height="3.2" rx="1.6" '
                  'fill="#FFFFFF" stroke="%s" stroke-width="0.3"/>'
          % (cx - nw / 2, cy + 0.6, nw, mix(col, '#000000', 0.3)))
    D.text(cx, cy + 2.2, nuc, anchor='middle', color=mix(col, '#000000', 0.35),
           bold=True, audit=False)


ras(GDP, SY, COL['off'], 'GDP', -1, INK)
ras(GTP, SY, COL['on'], 'GTP', 1, WHITE)
# GAP at the membrane, catalysing the hydrolysis arc right beneath it
protein(107.0, 29.2, 19.0, 6.0, 'NF1, RASA1', COL['gap'], 'bi')
D.text(107.0, 33.9, 'GAPs', anchor='middle', color=GREY)
arrow((117.4, 37.4), (96.8, 37.4), (113.0, 35.6), (101.2, 35.6), lw=0.6)    # hydrolysis
arrow((96.8, 44.2), (117.4, 44.2), (101.2, 46.6), (113.0, 46.6), lw=0.6)    # exchange
D.text(107.0, 40.7, 'hydrolysis', anchor='middle', color=GREY)
D.text(107.0, 49.6, 'exchange', anchor='middle', color=GREY)
# SOS1 and the tissue GEFs catalyse the exchange arc
arrow((26.4, 40.6), (104.0, 46.2), (30.0, 50.0), (86.0, 51.2), col=COL['adapt'])
arrow((66.4, 40.0), (103.6, 46.0), (70.5, 46.0), (90.0, 49.2), col=COL['gef'])

# ---- right-hand note on the switch ---------------------------------------------
NX = 135.5
D.lines(NX, 28.0, ['G12, G13 and Q61 substitutions', 'blunt GAP-stimulated hydrolysis:',
                   'mutant RAS accumulates GTP-bound'], color=COL['red'])
D.lines(NX, 28.0 + 3 * LH + 1.0, ['NF1 is lost in <i>NF1</i>-mutant tumours;',
                                  'germline loss causes RASopathies'], color=GREY)

# ---- drug-class strip under the upstream layer ---------------------------------
TY = 54.4
tag(6.0, TY, 'SHP2 and SOS1 inhibitors', 'clinical')
tag(61.0, TY, 'OFF-state covalent (<i>KRAS</i> G12C)', 'approved')
tag(61.0, TY + LH, 'OFF-state, non-cysteine alleles', 'clinical')
tag(131.0, TY - 2 * LH + 0.4, ['RAS(ON) tri-complex inhibitors,',
                               'allele- and multi-selective'], 'approved')
tag(131.0, TY + LH, 'Degraders; effector-interface binders', 'clinical')

# ---- effector fan ----------------------------------------------------------------
T1, T2, T3 = 73.4, 86.0, 98.4
BR = {'mapk': 20.0, 'pi3k': 78.0, 'ral': 120.0, 'plc': 147.0, 'tiam': 168.0}
FY = 62.6
arrow((GTP, SY + 6.1), (GTP, FY), end='none', lw=0.6)
D.text(GTP - 1.6, FY - 1.4, 'effector binding', anchor='end', color=GREY)
for k, x in BR.items():
    arrow((GTP, FY), (x, T1 - 5.4), (GTP, FY + 3.0), (x, FY + 1.2), lw=0.5)

protein(BR['mapk'], T1, 22.0, 9.4, None, COL['mapk'], 'bi', rows=['RAF', '(BRAF, CRAF)'])
protein(BR['mapk'], T2, 20.0, 7.4, 'MEK1/2', COL['mapk'], 'bi')
protein(BR['mapk'], T3, 20.0, 7.4, 'ERK1/2', COL['mapk'], 'bi')
protein(BR['pi3k'], T1, 20.0, 9.4, None, COL['pi3k'], 'bi', rows=['PI3K', '(p110)'])
protein(BR['pi3k'], T2, 16.0, 7.4, 'AKT', COL['pi3k'], 'bi')
protein(BR['pi3k'], T3, 20.0, 7.4, 'mTORC1', COL['pi3k'], 'tri')
protein(BR['ral'], T1, 20.0, 8.2, 'RALGDS', COL['ral'], 'bi')
protein(BR['ral'], T2, 11.0, 7.0, 'RAL', COL['ral'], 'round')
protein(BR['plc'], T1, 16.0, 8.2, 'PLCε', COL['other'], 'bi')
protein(BR['tiam'], T1, 17.0, 8.2, 'TIAM1', COL['other'], 'bi')
protein(BR['plc'], T2, 19.0, 7.4, 'DAG, PKC', COL['other'], 'tri')
protein(BR['tiam'], T2, 11.0, 7.0, 'RAC', COL['other'], 'round')

for x, a, b, ha, hb in ((BR['mapk'], T1, T2, 4.7, 3.7), (BR['mapk'], T2, T3, 3.7, 3.7),
                        (BR['pi3k'], T1, T2, 4.7, 3.7), (BR['pi3k'], T2, T3, 3.7, 3.7),
                        (BR['ral'], T1, T2, 4.1, 3.5), (BR['plc'], T1, T2, 4.1, 3.7),
                        (BR['tiam'], T1, T2, 4.1, 3.5)):
    arrow((x, a + ha + 0.5), (x, b - hb - 0.4))

# RAL -> vesicle traffic and secretion: a vesicle train budding toward the edge
for k, (vx, vy, r) in enumerate(((114.2, 98.6, 2.0), (119.8, 97.2, 1.7),
                                 (125.0, 98.8, 1.45))):
    D.add('body', '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#EFE7F7" stroke="%s" '
                  'stroke-width="0.45"/>' % (vx, vy, r, COL['ral']))
    for j in range(4):
        a = j * 1.6 + k
        D.add('body', '<circle cx="%.2f" cy="%.2f" r="0.32" fill="%s"/>'
              % (vx + 0.5 * r * math.cos(a), vy + 0.5 * r * math.sin(a), COL['ral']))
arrow((BR['ral'], T2 + 4.0), (BR['ral'] - 0.6, 94.6))
D.lines(BR['ral'], 104.6, ['vesicle traffic,', 'secretion'], anchor='middle',
        color=COL['ral'])

# PLCε (DAG, PKC) and TIAM1 (RAC) -> actin: a branched filament network
AX0, AX1, AY = 138.0, 177.0, 98.6
for k in range(3):
    y = AY - 1.4 + k * 1.4
    pts = [(AX0 + j * 0.55, y + 0.28 * math.sin(j * 1.1 + k)) for j in range(72)]
    D.add('body', '<path d="%s" fill="none" stroke="%s" stroke-width="0.55" '
                  'stroke-dasharray="0.42 0.12" stroke-linecap="round"/>'
          % (pts_path(pts, False), COL['other']))
for bx in (143.0, 151.0, 160.0, 169.0):
    D.add('body', '<path d="M%.2f %.2f l2.2 -2.1" stroke="%s" stroke-width="0.5" '
                  'stroke-dasharray="0.42 0.12"/>' % (bx, AY - 1.4, COL['other']))
for x in (BR['plc'], BR['tiam']):
    arrow((x, T2 + 4.2), (x, AY - 3.6))
D.lines((AX0 + AX1) / 2, 104.6, ['actin remodelling,', 'migration and invasion'],
        anchor='middle', color=COL['other'])

# ---- nucleus (partially in view) entered by ERK ----------------------------------
NCX, NCY, NRX, NRY = 30.0, 134.0, 36.0, 25.0
D.add('bg', '<g clip-path="url(#clipA)">')
D.add('bg', '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="url(#nuc)" '
            'stroke="#9C88B8" stroke-width="0.55"/>' % (NCX, NCY, NRX, NRY))
D.add('bg', '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="none" '
            'stroke="#9C88B8" stroke-width="0.3"/>' % (NCX, NCY, NRX - 1.0, NRY - 1.0))
for ang in (-132, -104, -78, -40):                 # nuclear pores
    t = math.radians(ang)
    px, py = NCX + (NRX - 0.5) * math.cos(t), NCY + (NRY - 0.5) * math.sin(t)
    D.add('bg', '<circle cx="%.2f" cy="%.2f" r="0.75" fill="#FCF7F0" stroke="#9C88B8" '
                'stroke-width="0.35"/>' % (px, py))
# DNA double helix
for ph, colr in ((0.0, '#5B3F86'), (math.pi, '#8E78B0')):
    pts = [(4.0 + j * 0.5, 120.3 + 1.3 * math.sin(j * 0.32 + ph)) for j in range(66)]
    D.add('bg', '<path d="%s" fill="none" stroke="%s" stroke-width="0.6"/>'
          % (pts_path(pts, False), colr))
for j in range(2, 66, 4):
    xx = 4.0 + j * 0.5
    D.add('bg', '<path d="M%.2f %.2f L%.2f %.2f" stroke="#B9A9D2" stroke-width="0.35"/>'
          % (xx, 120.3 + 1.3 * math.sin(j * 0.32), xx, 120.3 + 1.3 * math.sin(j * 0.32 + math.pi)))
D.add('bg', '</g>')
protein(22.6, 114.4, 8.4, 4.6, 'ERK', COL['mapk'], 'round', layer='over')
arrow((BR['mapk'], T3 + 3.9), (21.8, 111.8), (BR['mapk'], 106.0), (21.4, 108.4))
D.lines(27.4, 114.3, ['ERK-dependent', 'transcription'], color='#5B3F86')
D.text(38.6, 120.5, 'Nucleus', color='#5B3F86', audit=False)

# ---- drug tags on the branches ---------------------------------------------------
tag(33.4, (T1 + T2) / 2, 'RAF and MEK inhibitors', 'approved')
tag(33.4, T3, 'ERK inhibitors', 'clinical')
tag(68.0, 106.0, 'PI3K, AKT and mTOR inhibitors', 'approved')
tag(68.0, 110.6, 'RAL, PLCε and TIAM1 branches: no selective agent in the clinic',
    'preclinical')
D.text(70.6, 110.6 + LH, 'Effector use differs by allele and by tissue', color=GREY)

# ---- ERK negative feedback (red dashes) ------------------------------------------
RD, DSH = COL['red'], '1.1 0.7'
FX = 3.6
arrow((BR['mapk'] - 9.2, T3), (FX, T3), end='none', col=RD, dash=DSH, lw=0.5)
arrow((FX, T3), (FX, 30.0), end='none', col=RD, dash=DSH, lw=0.5)
arrow((FX, 30.0), (6.4, 30.0), end='tee', col=RD, dash=DSH, lw=0.5)        # receptors
arrow((FX, T1), (BR['mapk'] - 10.6, T1), end='tee', col=RD, dash=DSH, lw=0.5)  # CRAF
arrow((FX, 45.2), (20.4, 45.2), end='none', col=RD, dash=DSH, lw=0.5)
arrow((20.4, 45.2), (20.4, 41.4), end='tee', col=RD, dash=DSH, lw=0.5)      # SOS1
D.text(2.0, (T1 + T3) / 2 + 3.0, 'ERK negative feedback', anchor='middle', color=RD,
       rot=-90)

D.text(0.6, 2.0, 'a', bold=True, size=PNs, audit=False)

# ============================================================ panel b ========
BY = 126.0
CW, CG = 43.5, 2.0
CARDS = [
    ('Metabolic reprogramming',
     'More glucose uptake, rewired glutamine use, scavenging of extracellular nutrients',
     'Metabolic co-targeting', 'preclinical'),
    ('Macropinocytosis and autophagy',
     'Protein and amino-acid recycling sustains growth and is a survival route under drug pressure',
     'Autophagy inhibition', 'clinical'),
    ('Immunosuppressive microenvironment',
     'Higher PD-L1, recruitment of myeloid suppressor cells, reduced antigen presentation',
     'Checkpoint blockade; mutant-RAS vaccines and TCR-T cells', 'clinical'),
    ('Senescence and oncogenic stress',
     'A barrier that must be bypassed: carrying a mutation is not the same as depending on it',
     'No therapeutic use; constrains how mutation data are read', 'preclinical'),
]


def wrap(s, width, bold=False):
    out, cur = [], ''
    for wd in s.split(' '):
        t = (cur + ' ' + wd).strip()
        if tw(t, bold) <= width or not cur:
            cur = t
        else:
            out.append(cur)
            cur = wd
    return out + [cur]


def cell(x, y, w, h, col, nuc=True, layer='body'):
    """A small cell: membrane rim, cytoplasm, nucleus."""
    D.add(layer, '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
                 'fill="%s" stroke="%s" stroke-width="0.9"/>'
          % (x, y, w, h, min(w, h) / 2, mix(col, WHITE, 0.82), mix(col, WHITE, 0.25)))
    if nuc:
        D.add(layer, '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="%.2f" fill="url(#nuc)" '
                     'stroke="#9C88B8" stroke-width="0.35"/>'
              % (x + w * 0.62, y + h * 0.52, min(w, h) * 0.24, min(w, h) * 0.20))


def hexa(x, y, r, col):
    D.add('body', '<path d="%s" fill="#FFFFFF" stroke="%s" stroke-width="0.4"/>'
          % (pts_path([(x + r * math.cos(math.pi / 3 * k + math.pi / 6),
                        y + r * math.sin(math.pi / 3 * k + math.pi / 6))
                       for k in range(6)]), col))


def icon_metabolic(x, y):
    cell(x + 10.0, y + 0.4, 30.0, 14.6, COL['on'], nuc=False)
    # mitochondrion
    D.add('body', '<rect x="%.2f" y="%.2f" width="9.6" height="4.6" rx="2.3" '
                  'fill="#F6D3B0" stroke="#C0702A" stroke-width="0.4"/>'
          % (x + 27.0, y + 6.4))
    D.add('body', '<path d="M%.2f %.2f q0.8 1.6 1.6 0 q0.8 -1.6 1.6 0 q0.8 1.6 1.6 0 '
                  'q0.8 -1.6 1.6 0" fill="none" stroke="#C0702A" stroke-width="0.35"/>'
          % (x + 28.4, y + 8.7))
    # transporter in the membrane, glucose entering
    for s in (-0.9, 0.9):
        D.add('body', '<rect x="%.2f" y="%.2f" width="1.4" height="3.6" rx="0.7" '
                      'fill="%s" stroke="%s" stroke-width="0.25"/>'
              % (x + 10.2 + s - 0.7, y + 5.6, D.gradient(REC), mix(REC, '#000000', 0.4)))
    for hx, hy in ((3.0, 4.2), (5.4, 9.6), (2.4, 12.0), (15.2, 7.4)):
        hexa(x + hx, y + hy, 1.15, '#C0702A')
    for gx, gy in ((19.0, 11.4), (21.6, 4.4), (23.6, 11.0)):
        D.add('body', '<circle cx="%.2f" cy="%.2f" r="0.75" fill="#7BB08F"/>'
              % (x + gx, y + gy))
    arrow((x + 6.8, y + 7.4), (x + 12.8, y + 7.4), hs=1.0)


def icon_macro(x, y):
    cell(x + 2.0, y + 2.6, 38.0, 12.4, COL['on'], nuc=False)
    # ruffle closing around extracellular protein
    D.add('body', '<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f" fill="none" '
                  'stroke="%s" stroke-width="0.9" stroke-linecap="round"/>'
          % (x + 6.0, y + 3.0, x + 4.0, y - 1.6, x + 12.0, y - 1.4, x + 12.6, y + 2.0,
             mix(COL['on'], WHITE, 0.25)))
    for dx, dy in ((8.0, 0.4), (9.6, 1.4), (7.2, 1.8), (10.4, -0.2)):
        D.add('body', '<circle cx="%.2f" cy="%.2f" r="0.5" fill="#C0702A"/>'
              % (x + dx, y + dy))
    # macropinosome
    D.add('body', '<circle cx="%.2f" cy="%.2f" r="2.6" fill="#FBEFE4" stroke="%s" '
                  'stroke-width="0.5"/>' % (x + 17.0, y + 8.6, mix(COL['on'], WHITE, 0.25)))
    for dx, dy in ((-0.9, -0.6), (0.8, -0.2), (0.0, 1.0)):
        D.add('body', '<circle cx="%.2f" cy="%.2f" r="0.5" fill="#C0702A"/>'
              % (x + 17.0 + dx, y + 8.6 + dy))
    # autophagosome: double membrane around cargo
    for r, sw in ((3.2, 0.45), (2.5, 0.35)):
        D.add('body', '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="#6A4C93" '
                      'stroke-width="%.2f"/>' % (x + 30.0, y + 8.6, r, sw))
    D.add('body', '<rect x="%.2f" y="%.2f" width="2.6" height="1.5" rx="0.6" '
                  'fill="#F6D3B0" stroke="#C0702A" stroke-width="0.3"/>'
          % (x + 28.7, y + 7.85))
    arrow((x + 20.4, y + 8.6), (x + 25.8, y + 8.6), hs=1.0)


def icon_immune(x, y):
    cell(x + 1.0, y + 1.0, 17.0, 14.0, COL['on'])
    cell(x + 25.0, y + 2.6, 14.0, 11.0, COL['adapt'])
    # PD-L1 lollipops on the tumour cell facing the T cell, PD-1 opposite
    for yy in (5.2, 8.0, 10.8):
        D.add('body', '<path d="M%.2f %.2f h2.1" stroke="#B5525C" stroke-width="0.45"/>'
                      '<circle cx="%.2f" cy="%.2f" r="0.6" fill="#B5525C"/>'
              % (x + 18.0, y + yy, x + 20.5, y + yy))
    arrow((x + 24.8, y + 8.0), (x + 21.8, y + 8.0), end='tee', col=INK, lw=0.45)
    # myeloid suppressor cell
    body([(x + 21.6, y + 14.2, 2.4, 1.6, 0), (x + 23.2, y + 13.2, 1.4, 1.2, 0)], '#8C6BB1',
         shadow=False)


def icon_senescence(x, y):
    # a flattened, enlarged cell with a large nucleus and arrest bar on the cycle
    D.add('body', '<path d="M%.2f %.2f C%.2f %.2f %.2f %.2f %.2f %.2f C%.2f %.2f %.2f %.2f '
                  '%.2f %.2f Z" fill="%s" stroke="%s" stroke-width="0.9"/>'
          % (x + 2.0, y + 9.6, x + 4.0, y + 1.6, x + 26.0, y + 0.8, x + 30.0, y + 6.6,
             x + 33.0, y + 13.0, x + 6.0, y + 15.6, x + 2.0, y + 9.6,
             mix(COL['on'], WHITE, 0.82), mix(COL['on'], WHITE, 0.25)))
    D.add('body', '<ellipse cx="%.2f" cy="%.2f" rx="5.2" ry="3.6" fill="url(#nuc)" '
                  'stroke="#9C88B8" stroke-width="0.35"/>' % (x + 15.0, y + 8.4))
    cx, cy, r = x + 36.6, y + 7.8, 2.6
    D.add('body', '<path d="M%.2f %.2f A%.2f %.2f 0 1 1 %.2f %.2f" fill="none" '
                  'stroke="%s" stroke-width="0.5"/>'
          % (cx + r, cy, r, r, cx + r * math.cos(-1.1), cy + r * math.sin(-1.1), GREY))
    head((cx + r * math.cos(-1.5), cy + r * math.sin(-1.5)),
         (cx + r * math.cos(-1.1), cy + r * math.sin(-1.1)), GREY, 1.0, 'body')
    D.add('body', '<path d="M%.2f %.2f L%.2f %.2f" stroke="%s" stroke-width="0.9" '
                  'stroke-linecap="round"/>' % (cx + 1.4, cy - 3.6, cx + 3.8, cy - 1.0,
                                                COL['red']))


ICONS = [icon_metabolic, icon_macro, icon_immune, icon_senescence]
TW = CW - 4.2
WR = [(wrap(t, TW, True), wrap(b, TW), wrap(g, TW - 2.6), st) for t, b, g, st in CARDS]
Y_T = BY + 20.6                                   # titles start
Y_B = Y_T + max(len(w[0]) for w in WR) * LH + 0.4  # bodies start, aligned
Y_G = Y_B + max(len(w[1]) for w in WR) * LH + 1.0  # tags start, aligned
BH = Y_G + (max(len(w[2]) for w in WR) - 1) * LH + 3.0 - BY
H = BY + BH + 0.4
for k, (tt, bb, gg, st) in enumerate(WR):
    x = k * (CW + CG)
    D.add('bg', '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="2.2" '
                'fill="url(#card)" stroke="#D5DEE4" stroke-width="0.3"/>'
          % (x, BY, CW, BH))
    ICONS[k](x + 1.6, BY + 2.4)
    D.lines(x + 2.1, Y_T, tt, bold=True)
    D.lines(x + 2.1, Y_B, bb, color=GREY)
    tag(x + 2.1, Y_G, gg, st)
D.text(0.6, BY + 2.6, 'b', bold=True, size=PNs, audit=False)


# ============================================================ audit + out ====
def audit():
    """Text boxes must not overlap each other, nor leave the canvas."""
    bad = 0
    B = D.boxes
    for i in range(len(B)):
        a = B[i]
        if a[0] < 0.2 or a[2] > W - 0.2:
            print('  ! off canvas: %s' % a[4]); bad += 1
        for j in range(i + 1, len(B)):
            b = B[j]
            if a[0] < b[2] - 0.1 and b[0] < a[2] - 0.1 and a[1] < b[3] - 0.1 and b[1] < a[3] - 0.1:
                print('  ! overlap: %r / %r' % (a[4], b[4])); bad += 1
    return bad


bad = audit()
svg_path = os.path.join(FIG, NAME + '.svg')
with open(svg_path, 'w') as fh:
    fh.write(D.svg())
subprocess.run(['rsvg-convert', '--dpi-x', '400', '--dpi-y', '400', '-b', 'white',
                '-o', os.path.join(FIG, NAME + '.png'), svg_path], check=True)
CHROME = os.environ.get('CHROME',
                        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
if not os.path.exists(CHROME):           # fallback: same artwork, cairo PDF
    print('  ! Chrome not found: PDF written by rsvg-convert (space glyph as Type 3)')
    subprocess.run(['rsvg-convert', '-f', 'pdf', '-o',
                    os.path.join(FIG, NAME + '.pdf'), svg_path], check=True)
    sys.exit(1 if bad else 0)
tmp = tempfile.mkdtemp()
try:
    html = os.path.join(tmp, 'f.html')
    with open(html, 'w') as fh:
        fh.write('<html><head><style>@page{size:%gmm %gmm;margin:0}html,body{margin:0}'
                 'svg{display:block}</style></head><body>%s</body></html>'
                 % (W, H, D.svg()))
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    '--user-data-dir=' + os.path.join(tmp, 'u'),
                    '--print-to-pdf=' + os.path.join(FIG, NAME + '.pdf'),
                    'file://' + html], check=True, capture_output=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print('  ->', NAME, '(%d layout warnings)' % bad)
sys.exit(1 if bad else 0)
