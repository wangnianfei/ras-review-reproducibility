#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 8 - the RAS signalling network, drawn as a cell schematic.

Redrawn 2026-11-01 (author: the plain box-and-arrow form was not acceptable for a
top journal), second pass the same day (author: the rest of the figure should be
drawn the way the membrane is, and several connectors were too short to read).
The content is unchanged throughout - same nodes, same labels, same arrows, same
drug tags and the same negative-feedback line as the box version it replaces; only
the depiction changed:
  · plasma membrane as a lipid bilayer, the four input classes as receptor glyphs;
  · every protein is a lobed body (domain lobes hinted by the silhouette), every
    small GTPase a smooth globule, every cellular process a flat plate, so shape
    alone separates molecule from process;
  · the switch carries its bound nucleotide in a pocket;
  · connectors are laid out with real clearance between bodies and drawn without
    end shrink, so no arrow is shorter than it needs to be.

Content follows the review outline sections 3.1-3.5 one to one (upstream input ->
switch -> downstream branches -> cellular phenotypes -> negative feedback), and every
layer that can be drugged carries a tag naming the drug class, with the marker shape
telling how far that class has got clinically (circle approved / square in trials /
triangle preclinical or abandoned). No numbers are plotted here: this is a schematic.

Usage: python3 01_fig7_network.py <root>
Out:   <root>/figures/Fig7_RAS_signalling_network.{pdf,svg,png}
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
S = import_module('00_style')
import numpy as np
from matplotlib.patches import (Rectangle, Circle, Ellipse, FancyBboxPatch,
                                FancyArrowPatch, Polygon, Wedge)
from matplotlib.colors import to_rgb

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '..')
FIG = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)
C, FS, LW, GI = S.C, S.FS, S.LW, S.GI
tee, tag = S.tee, S.drug_tag
DASH = (0, (3, 2))


def arrow(ax, p0, p1, style='-|>', ls='-', color=None, lw=None, rad=0.0,
          z=2, ms=2.2, shrink=0.0):
    """Like S.arrow but with the end shrink under control (default none)."""
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms * 3,
                                 linewidth=lw or LW['arrow'], linestyle=ls,
                                 color=color or C['edge'], zorder=z,
                                 connectionstyle='arc3,rad=%.2f' % rad,
                                 shrinkA=shrink, shrinkB=shrink,
                                 joinstyle='miter'))


def tint(col, f=0.80):
    r, g, b = to_rgb(col)
    return (r + (1 - r) * f, g + (1 - g) * f, b + (1 - b) * f)


# ---------------------------------------------------------------- glyph kit ---
MEM_Y = 107.0            # mid-plane of the bilayer, mm
MEM_T = 5.0              # head-to-head thickness
EXO = '#EDF3F8'          # extracellular space
CYT = '#FBFAF8'          # cytoplasm
HEAD = '#AFC2D2'         # phospholipid head groups
TAIL = '#C8D4DE'


def bilayer(ax, x0, x1, gaps=(), step=2.45, r=0.78):
    """Two leaflets of head groups with tails; `gaps` are x-intervals left open."""
    yo, yi = MEM_Y + MEM_T / 2, MEM_Y - MEM_T / 2
    ax.add_patch(Rectangle((0, yi - r), 172, 2 * (MEM_T / 2 + r),
                           facecolor='#F6F8FA', edgecolor='none', zorder=0.5))
    n = int((x1 - x0) / step)
    for k in range(n + 1):
        x = x0 + k * step
        if any(a - r <= x <= b + r for a, b in gaps):
            continue
        for y, s in ((yo, -1), (yi, 1)):
            ax.add_patch(Circle((x, y), r, facecolor=HEAD, edgecolor='none',
                                zorder=1))
            for dx in (-0.42, 0.42):
                ax.plot([x, x + dx], [y + s * r * 0.5, MEM_Y - s * 0.15],
                        color=TAIL, linewidth=0.5, solid_capstyle='round',
                        zorder=1)


# --- protein bodies: the outline is the union of a few domain lobes -----------
def _ray(c0, lobe, ct, st):
    """Distance from c0 along (ct, st) to the far side of one elliptical lobe."""
    ex, ey, w, h = lobe
    a, b = w / 2.0, h / 2.0
    qa = (ct / a) ** 2 + (st / b) ** 2
    qb = 2 * ((c0[0] - ex) * ct / a ** 2 + (c0[1] - ey) * st / b ** 2)
    qc = ((c0[0] - ex) / a) ** 2 + ((c0[1] - ey) / b) ** 2 - 1.0
    d = qb * qb - 4 * qa * qc
    if d < 0:
        return 0.0
    return max((-qb + np.sqrt(d)) / (2 * qa), 0.0)


def blob(ax, lobes, c0, fc, ec=None, lw=None, z=4, n=220):
    """Single clean outline around a set of overlapping lobes (star-shaped union)."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    r = np.max([[_ray(c0, lo, c, s) for c, s in zip(ct, st)] for lo in lobes],
               axis=0)
    pts = np.column_stack([c0[0] + r * ct, c0[1] + r * st])
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc,
                         edgecolor=ec or C['edge'], linewidth=lw or LW['box'],
                         joinstyle='round', zorder=z))


def protein(ax, cx, cy, w, h, label, fc, shape='bi', tc='white', fs=None,
            bold=True, z=4, dy=0.0):
    """Lobed protein body with its name on it. shape: bi | tri | round."""
    if shape == 'tri':                      # three domains in a row
        lobes = [(cx - w * 0.30, cy + h * 0.02, w * 0.52, h * 0.86),
                 (cx, cy + h * 0.05, w * 0.56, h),
                 (cx + w * 0.30, cy - h * 0.04, w * 0.52, h * 0.84)]
    elif shape == 'round':                  # one compact globule
        lobes = [(cx, cy, w, h)]
    else:                                   # two lobes with a shallow waist
        lobes = [(cx - w * 0.17, cy + h * 0.03, w * 0.74, h * 0.98),
                 (cx + w * 0.19, cy - h * 0.05, w * 0.68, h * 0.88)]
    blob(ax, lobes, (cx, cy), fc, z=z)
    ax.text(cx, cy + dy, label, ha='center', va='center',
            fontsize=fs or FS['anno'], color=tc, zorder=z + 1,
            fontweight='bold' if bold else 'normal', linespacing=1.25)


def plate(ax, cx, cy, w, h, label, col, fs=None, z=4):
    """A cellular process, not a molecule: flat tinted plate, no body outline."""
    ax.add_patch(FancyBboxPatch((cx - w / 2 + 1.1, cy - h / 2 + 1.1),
                                w - 2.2, h - 2.2,
                                boxstyle='round,pad=1.1,rounding_size=1.3',
                                facecolor=tint(col, 0.82), edgecolor=col,
                                linewidth=LW['thin'], zorder=z))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fs or FS['anno'],
            color=col, zorder=z + 1, linespacing=1.25)


def nucleotide(ax, cx, cy, text, fc):
    """Bound nucleotide shown in the switch's pocket."""
    w, h = 11.0, 4.6
    ax.add_patch(FancyBboxPatch((cx - w / 2 + h / 2, cy), w - h, 1e-6,
                                boxstyle='round,pad=%.3f' % (h / 2),
                                facecolor='white', edgecolor=fc,
                                linewidth=0.5, zorder=6))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=FS['small'],
            color=fc, fontweight='bold', zorder=7)


def switch(ax, cx, cy, state, fc, tc, nuc, nfc):
    ax.add_patch(Ellipse((cx, cy), 32, 18, facecolor=fc, edgecolor=C['edge'],
                         linewidth=LW['box'], zorder=4))
    ax.text(cx, cy + 4.6, 'RAS', ha='center', va='center', fontsize=FS['head'],
            fontweight='bold', color=tc, zorder=6)
    ax.text(cx, cy + 0.9, state, ha='center', va='center', fontsize=FS['small'],
            color=tc, zorder=6)
    nucleotide(ax, cx, cy - 4.6, nuc, nfc)


# --- receptor glyphs: each returns the x-interval it occupies in the bilayer --
def tm_helix(ax, cx, w=2.3, fc=None, y0=None, y1=None):
    y0 = MEM_Y - MEM_T / 2 - 1.1 if y0 is None else y0
    y1 = MEM_Y + MEM_T / 2 + 1.1 if y1 is None else y1
    ax.add_patch(FancyBboxPatch((cx, y0 + w / 2), 1e-6, y1 - y0 - w,
                                boxstyle='round,pad=%.3f' % (w / 2),
                                facecolor=fc or C['receptor'],
                                edgecolor=C['edge'], linewidth=LW['thin'],
                                zorder=5))


def rtk(ax, cx):
    fc = C['receptor']
    for s in (-1, 1):
        tm_helix(ax, cx + s * 2.6, fc=fc)
        ax.add_patch(Ellipse((cx + s * 3.1, 113.6), 5.6, 7.8, facecolor=fc,
                             edgecolor=C['edge'], linewidth=LW['thin'], zorder=5))
        ax.add_patch(Ellipse((cx + s * 3.3, 101.6), 5.8, 5.2, facecolor=fc,
                             edgecolor=C['edge'], linewidth=LW['thin'], zorder=5))
    ax.plot([cx - 3.1, cx + 3.1], [115.8, 115.8], color=C['edge'],
            linewidth=LW['thin'], zorder=4)
    return (cx - 6.2, cx + 6.2)


def integrin(ax, cx):
    fc = C['receptor']
    for s, top in ((-1, 116.5), (1, 114.5)):
        ax.plot([cx + s * 2.4, cx + s * 2.4, cx + s * 4.0],
                [top, MEM_Y - MEM_T / 2 - 0.4, 100.8], color=fc,
                linewidth=2.1, solid_capstyle='round',
                solid_joinstyle='round', zorder=5)
        ax.add_patch(Ellipse((cx + s * 2.4, top + 0.6), 4.2, 3.4, facecolor=fc,
                             edgecolor=C['edge'], linewidth=LW['thin'], zorder=5))
    return (cx - 5.0, cx + 5.0)


def gpcr(ax, cx):
    fc = C['receptor']
    xs = [cx - 4.5 + i * 1.8 for i in range(6)]
    for i, x in enumerate(xs):
        dy = 0.6 if i % 2 else 0.0
        tm_helix(ax, x, w=1.5, fc=fc,
                 y0=MEM_Y - MEM_T / 2 - 1.0 - dy,
                 y1=MEM_Y + MEM_T / 2 + 1.0 + dy)
    for i in range(0, 5, 2):
        ax.plot([xs[i], xs[i + 1]], [110.3, 110.3], color=fc, linewidth=0.8,
                zorder=4, solid_capstyle='round')
    for i in range(1, 4, 2):
        ax.plot([xs[i], xs[i + 1]], [103.7, 103.7], color=fc, linewidth=0.8,
                zorder=4, solid_capstyle='round')
    return (cx - 5.6, cx + 5.6)


def immune_receptor(ax, cx):
    fc = C['receptor']
    for s in (-1, 1):
        tm_helix(ax, cx + s * 1.4, w=2.0, fc=fc)
        for k, y in enumerate((112.3, 116.6)):
            ax.add_patch(Ellipse((cx + s * 1.8, y), 4.3, 4.2, facecolor=fc,
                                 edgecolor=C['edge'], linewidth=LW['thin'],
                                 zorder=5))
    for s in (-1, 1):                       # accessory chains
        tm_helix(ax, cx + s * 5.2, w=1.6, fc=C['adaptor'])
        ax.plot([cx + s * 5.2 + 0.8] * 2, [103.2, 100.4], color=C['adaptor'],
                linewidth=0.9, solid_capstyle='round', zorder=5)
    return (cx - 6.4, cx + 6.4)


# ============================================================== the figure ====
fig = S.figure(180.0)
A = S.mm_axes(fig, 4, 50, 172, 126)
B = S.mm_axes(fig, 4, 6, 172, 36)

A.add_patch(Rectangle((0, MEM_Y), 172, 126 - MEM_Y, facecolor=EXO,
                      edgecolor='none', zorder=0))
A.add_patch(Rectangle((0, 0), 172, MEM_Y, facecolor=CYT, edgecolor='none',
                      zorder=0))

# --- the membrane and the four input classes ----------------------------------
RX = {'rtk': 16.0, 'int': 42.0, 'gpcr': 66.0, 'imm': 90.0}
gaps = [rtk(A, RX['rtk']), integrin(A, RX['int']), gpcr(A, RX['gpcr']),
        immune_receptor(A, RX['imm'])]
bilayer(A, 1.0, 171.0, gaps=gaps)
A.text(1.0, 125.5, 'Extracellular inputs', fontsize=FS['small'], color=C['grey'],
       ha='left', va='top')
A.text(171.0, MEM_Y, 'plasma membrane', fontsize=FS['tiny'], color=C['grey'],
       ha='right', va='center', zorder=3)
A.text(118.0, 103.0, 'cytoplasm', fontsize=FS['tiny'], color=C['grey'],
       ha='right', va='top', zorder=3)
for key, lbl in (('rtk', 'Receptor tyrosine\nkinases'), ('int', 'Integrins'),
                 ('gpcr', 'G-protein-coupled\nreceptors'),
                 ('imm', 'Antigen and\nimmune receptors')):
    A.text(RX[key], 122.0, lbl, ha='center', va='top', fontsize=FS['small'],
           color=C['ink'], linespacing=1.3)

# --- adaptor / exchange-factor layer ------------------------------------------
AC, AH = 90.0, 10.0                      # body centre line and body height
ATOP, ABOT = AC + AH / 2, AC - AH / 2
protein(A, 10.0, AC, 18, AH, 'GRB2', C['adaptor'], shape='tri')
protein(A, 36.0, AC, 23, AH, 'SOS1\nGEF', C['adaptor'], shape='bi', fs=FS['small'])
protein(A, 62.0, AC, 19, AH, 'SHP2', C['adaptor'], shape='tri')
protein(A, 90.0, AC, 30, AH, 'Tissue-restricted\nGEFs', C['adaptor'], shape='bi',
        fs=FS['tiny'], bold=False)

arrow(A, (14.0, 99.4), (10.5, ATOP + 0.3))                 # RTK -> GRB2
arrow(A, (20.4, 100.2), (58.0, ATOP + 0.3), rad=-0.26)     # RTK -> SHP2
arrow(A, (45.6, 100.4), (63.5, ATOP + 0.3), rad=-0.12)     # integrins -> SHP2
arrow(A, (68.4, 100.4), (84.0, ATOP + 0.3), rad=-0.12)     # GPCRs -> GEFs
arrow(A, (90.0, 99.2), (92.0, ATOP + 0.3))                 # immune -> RasGRP
arrow(A, (19.4, AC), (24.2, AC))                           # GRB2 -> SOS1
arrow(A, (55.0, ABOT - 0.4), (41.0, ABOT - 0.4), rad=0.26,
      color=C['grey'])                                     # SHP2 -> GRB2-SOS1
tag(A, 6, 79.5, 'SHP2 and SOS1 inhibitors act on this layer', status='clinical',
    fs=FS['tiny'])

# --- the nucleotide switch ----------------------------------------------------
SY = 69.0
switch(A, 48, SY, 'OFF state', C['off'], C['ink'], 'GDP', '#4A5560')
switch(A, 104, SY, 'ON state', C['on'], 'white', 'GTP', C['on'])

arrow(A, (64.6, 73.4), (87.4, 73.4), rad=-0.40, lw=0.9)    # exchange
arrow(A, (87.4, 64.6), (64.6, 64.6), rad=-0.40, lw=0.9)    # hydrolysis
A.text(78, 78.8, 'nucleotide exchange (GEF: SOS1)', ha='center', va='bottom',
       fontsize=FS['small'], color=C['adaptor'])
A.text(78, 59.2, 'GTP hydrolysis (GAP: NF1)', ha='center', va='top',
       fontsize=FS['small'], color=C['grey'])
arrow(A, (36.0, ABOT - 0.2), (68.0, 77.4), rad=-0.10,
      color=C['adaptor'])                                  # SOS1 -> exchange

protein(A, 142.0, 63.0, 30, 11, 'NF1, RASA1\nGAPs', C['gap'], shape='bi',
        fs=FS['small'])
A.text(126, 55.8, 'lost in ' + GI('NF1') + '-mutant tumours; germline\n'
       'loss causes RASopathies', fontsize=FS['tiny'], color=C['grey'],
       ha='left', va='top', linespacing=1.3)
arrow(A, (126.0, 63.6), (88.5, 62.6), rad=0.08, color=C['gap'])   # GAP -> hydrolysis

A.add_patch(FancyBboxPatch((125.3, 89.3), 44.4, 11.4,
                           boxstyle='round,pad=1.3,rounding_size=1.6',
                           facecolor=C['light'], edgecolor=HEAD,
                           linewidth=LW['thin'], zorder=1))
A.text(125.5, 100.6, 'Substitutions at codons 12, 13 and 61 impair\n'
                     'GAP-stimulated hydrolysis, so the switch accumulates\n'
                     'in the GTP-bound state; the residual nucleotide cycling\n'
                     'left to each allele decides which drug class can work.',
       fontsize=FS['tiny'], ha='left', va='top', linespacing=1.35, zorder=2)

tag(A, 12, 56.2, 'OFF-state covalent inhibitors (' + GI('KRAS') + ' G12C)',
    status='approved')
tag(A, 12, 52.4, 'OFF-state inhibitors of non-cysteine alleles', status='clinical')
tag(A, 124, 77.5, 'RAS(ON) tri-complex inhibitors: allele-selective\n'
                  'and multi-selective (pan-RAS)', status='approved')
tag(A, 124, 72.5, 'RAS degraders; effector-interface binders', status='clinical')

# --- effector fan -------------------------------------------------------------
arrow(A, (104, 59.6), (104, 50.4), lw=0.9)
A.plot([13, 161], [50.0, 50.0], color=C['edge'], linewidth=LW['arrow'], zorder=2)
A.text(101, 50.6, 'effector binding (switch I and the interswitch surface)',
       fontsize=FS['tiny'], color=C['grey'], ha='right', va='bottom')

TC = [42.5, 30.75, 19.0]                 # centre line of each effector tier
EH = 7.6
CHAIN = [(C['mapk'], 23.0, 34, [('RAF (BRAF, CRAF)', 'bi'), ('MEK1/2', 'bi'),
                                ('ERK1/2', 'bi')],
          [('RAF and MEK inhibitors', 'approved'),
           ('ERK inhibitors', 'clinical')]),
         (C['pi3k'], 62.0, 32, [('PI3K (p110)', 'bi'), ('AKT', 'bi'),
                                ('mTORC1', 'tri')],
          [('PI3K, AKT and mTOR inhibitors', 'approved'),
           ('blocking one trunk de-represses the other', 'clinical')]),
         (C['ral'], 99.0, 30, [('RALGDS', 'bi'), ('RAL', 'round'),
                               ('vesicle traffic,\nsecretion', 'plate')],
          [('no selective agent in the clinic', 'preclinical')])]
for col, cx, w, nodes, tags in CHAIN:
    for i, (lbl, shp) in enumerate(nodes):
        cy = TC[i]
        fs = FS['small'] if '\n' in lbl else FS['anno']
        if shp == 'plate':
            plate(A, cx, cy, w, EH, lbl, col, fs=fs)
        else:
            protein(A, cx, cy, w if shp != 'round' else w * 0.62, EH, lbl, col,
                    shape=shp, fs=fs, bold=(i < 2))
        if i:
            arrow(A, (cx, TC[i - 1] - EH / 2 - 0.2), (cx, cy + EH / 2 + 0.2))
    arrow(A, (cx, 49.6), (cx, TC[0] + EH / 2 + 0.2))
    for j, (tg, st) in enumerate(tags):
        tag(A, cx - w / 2, 12.2 - 3.3 * j, tg, status=st, fs=FS['tiny'])

# fourth branch: two parallel effectors feeding one output
protein(A, 132.0, TC[0], 24, EH, u'PLCε', C['other'], shape='bi')
protein(A, 158.5, TC[0], 23, EH, 'TIAM1', C['other'], shape='bi')
protein(A, 132.0, TC[1], 24, EH, 'DAG, PKC', C['other'], shape='tri',
        fs=FS['small'])
protein(A, 158.5, TC[1], 15, EH, 'RAC', C['other'], shape='round')
plate(A, 145.0, TC[2], 50, EH, 'actin remodelling, migration and invasion',
      C['other'], fs=FS['small'])
for cx in (132.0, 158.5):
    arrow(A, (cx, 49.6), (cx, TC[0] + EH / 2 + 0.2))
    arrow(A, (cx, TC[0] - EH / 2 - 0.2), (cx, TC[1] + EH / 2 + 0.2))
    arrow(A, (cx, TC[1] - EH / 2 - 0.2), (cx, TC[2] + EH / 2 + 0.2))
tag(A, 120, 12.2, 'no selective agent in the clinic', status='preclinical',
    fs=FS['tiny'])
tag(A, 120, 8.9, 'effector use differs by allele and by tissue', status='clinical',
    fs=FS['tiny'])

# --- ERK-mediated negative feedback -------------------------------------------
A.plot([6, 2.5, 2.5, 36.0, 36.0], [TC[2], TC[2], 81.8, 81.8, ABOT - 1.4],
       color=C['on'], linewidth=LW['arrow'], linestyle=DASH, zorder=4)
A.plot([36.0], [ABOT - 1.2], marker='_', markersize=4.0, color=C['on'], zorder=4)
A.text(4.4, 30, 'ERK-mediated negative feedback on SOS1, CRAF and the receptors',
       fontsize=FS['tiny'], color=C['on'], rotation=90, rotation_mode='anchor',
       ha='left', va='center')
A.text(6, 5.6, 'Blocking the pathway releases this feedback and the upstream layer '
               'reactivates: the mechanistic origin of adaptive resistance.',
       fontsize=FS['tiny'], color=C['grey'], ha='left', va='center')
A.text(6, 2.0, 'Markers:', fontsize=FS['tiny'], color=C['ink'], ha='left',
       va='center', fontweight='bold')
for xk, stk, lbk in ((20, 'approved', 'approved drug class'),
                     (58, 'clinical', 'in clinical trials (phase 1-3)'),
                     (104, 'preclinical', 'preclinical only, or tested and abandoned')):
    tag(A, xk, 2.0, lbk, status=stk, fs=FS['tiny'])
S.panel(fig, A, 'a')

# ====================================== panel b: cellular phenotype output ====
B.text(0, 34.5, 'Cellular output of sustained RAS signalling (review section 3.5)',
       fontsize=FS['small'], color=C['grey'], ha='left', va='top')


def icon_metabolic(ax, x, y):
    for k in range(3):
        cx, cy = x + k * 2.3, y + (0.5 if k == 1 else 0.0)
        ax.add_patch(Polygon([(cx + 1.15 * np.cos(a), cy + 1.15 * np.sin(a))
                              for a in np.linspace(0, 2 * np.pi, 7)[:-1]],
                             closed=True, facecolor='none', edgecolor=C['grey'],
                             linewidth=0.45, zorder=3))


def icon_macropino(ax, x, y):
    ax.add_patch(Wedge((x + 2.4, y), 2.4, 20, 160, width=0.6, facecolor=C['grey'],
                       edgecolor='none', zorder=3))
    for dx, dy in ((1.4, 0.9), (2.6, 1.6), (3.4, 0.7)):
        ax.add_patch(Circle((x + dx, y + dy), 0.4, facecolor=C['grey'],
                            edgecolor='none', zorder=3))


def icon_immune(ax, x, y):
    ax.add_patch(Circle((x + 1.4, y + 0.6), 1.5, facecolor='none',
                        edgecolor=C['grey'], linewidth=0.45, zorder=3))
    ax.plot([x + 3.4, x + 5.4], [y + 0.6, y + 0.6], color=C['grey'],
            linewidth=0.45, zorder=3)
    ax.plot([x + 5.4, x + 5.4], [y - 0.4, y + 1.6], color=C['grey'],
            linewidth=0.7, zorder=3)


def icon_senescence(ax, x, y):
    ax.add_patch(Ellipse((x + 2.6, y + 0.6), 5.2, 2.8, facecolor='none',
                         edgecolor=C['grey'], linewidth=0.45, zorder=3))
    ax.plot([x + 0.4, x + 4.8], [y + 2.2, y - 1.0], color=C['grey'],
            linewidth=0.6, zorder=3)


PH = [
    (0.5, 'Metabolic reprogramming', icon_metabolic,
     'Increased glucose uptake, rewired\nglutamine use, scavenging of\nextracellular nutrients',
     'metabolic co-targeting', 'preclinical'),
    (43.5, 'Macropinocytosis and autophagy', icon_macropino,
     'Protein and amino-acid recycling\nsustains growth and becomes a\nsurvival route under drug pressure',
     'autophagy inhibition', 'clinical'),
    (86.5, 'Immunosuppressive microenvironment', icon_immune,
     'Higher PD-L1, recruitment of myeloid\nsuppressor cells, reduced antigen\npresentation',
     'checkpoint blockade; mutant-RAS\nvaccines and TCR-T cells', 'clinical'),
    (129.5, 'Senescence and oncogenic stress', icon_senescence,
     'A barrier that must be bypassed:\ncarrying a mutation is not the same\nas depending on it',
     'no therapeutic use; constrains how\nmutation data are read', 'preclinical'),
]
for x, head, icon, body, tg, st in PH:
    # each card is a cell: outer leaflet, inner leaflet, cytoplasm
    B.add_patch(FancyBboxPatch((x + 1.2, 5.2), 39.0, 21.6,
                               boxstyle='round,pad=1.2,rounding_size=2.6',
                               facecolor=C['pheno'], edgecolor=HEAD,
                               linewidth=1.1, zorder=1))
    B.add_patch(FancyBboxPatch((x + 2.2, 6.0), 37.0, 20.0,
                               boxstyle='round,pad=1.0,rounding_size=2.2',
                               facecolor='none', edgecolor=HEAD,
                               linewidth=0.45, zorder=2))
    B.text(x + 2.9, 25.6, head, fontsize=FS['small'], fontweight='bold',
           ha='left', va='top', zorder=3)
    B.text(x + 2.9, 21.2, body, fontsize=FS['tiny'], ha='left', va='top',
           zorder=3, linespacing=1.4)
    icon(B, x + 33.0, 11.4)
    tag(B, x + 2.9, 7.2, tg, status=st, fs=FS['tiny'])
S.panel(fig, B, 'b')

S.save(fig, 'Fig7_RAS_signalling_network', FIG)
