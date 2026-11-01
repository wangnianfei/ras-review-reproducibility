#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 8 - the RAS signalling network, drawn as a cell schematic.

Redrawn 2026-11-01 (author: the plain box-and-arrow form was not acceptable for a
top journal). The content is unchanged - same nodes, same labels, same arrows, same
drug tags and the same negative-feedback line as the box version it replaces; only
the depiction changed: the plasma membrane is a lipid bilayer, the four input
classes are receptor glyphs set in it, every signalling node is a protein body
(globule or capsule), and the switch carries its bound nucleotide in a pocket.

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
                                Polygon, Wedge)

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '..')
FIG = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)
C, FS, LW, GI = S.C, S.FS, S.LW, S.GI
arrow, tee, tag = S.arrow, S.tee, S.drug_tag
DASH = (0, (3, 2))

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


def capsule(ax, x, y, w, h, label, fc, tc='white', fs=None, bold=True,
            ec=None, lw=None, z=4, ls='-'):
    """Stadium-shaped protein body; (x, y) is the bottom-left corner in mm."""
    r = h / 2
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2 * r, 1e-6,
                                boxstyle='round,pad=%.3f' % r,
                                facecolor=fc, edgecolor=ec or C['edge'],
                                linewidth=lw or LW['box'], linestyle=ls, zorder=z))
    ax.text(x + w / 2, y + h / 2, label, ha='center', va='center',
            fontsize=fs or FS['anno'], color=tc, zorder=z + 1,
            fontweight='bold' if bold else 'normal', linespacing=1.25)
    return (x + w / 2, y, x + w / 2, y + h)


def globule(ax, cx, cy, w, h, label, fc, tc='white', fs=None, bold=True, z=4):
    """Globular protein body."""
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor=fc, edgecolor=C['edge'],
                         linewidth=LW['box'], zorder=z))
    ax.text(cx, cy, label, ha='center', va='center', fontsize=fs or FS['anno'],
            color=tc, zorder=z + 1, fontweight='bold' if bold else 'normal',
            linespacing=1.25)


def lipid_tail(ax, x, y, up=6.0, color=None):
    """Zigzag standing for the C-terminal prenyl anchor of RAS."""
    n, amp = 5, 0.85
    ys = np.linspace(y, y + up, n + 1)
    xs = [x + (amp if i % 2 else -amp) * (i > 0) for i in range(n + 1)]
    ax.plot(xs, ys, color=color or C['grey'], linewidth=0.55, zorder=3,
            solid_joinstyle='round')


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
    globule(ax, cx, cy, 32, 18, '', fc)
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
AY, AH = 88.0, 10.0
capsule(A, 3, AY, 17, AH, 'GRB2', C['adaptor'])
capsule(A, 23, AY, 22, AH, 'SOS1\nGEF', C['adaptor'], fs=FS['small'])
capsule(A, 48, AY, 17, AH, 'SHP2', C['adaptor'])
capsule(A, 68, AY, 28, AH, 'Tissue-restricted\nGEFs', C['adaptor'],
        fs=FS['tiny'], bold=False)

arrow(A, (13.5, 98.6), (11.5, AY + AH))                  # RTK -> GRB2
arrow(A, (19.5, 99.0), (53.0, AY + AH), rad=-0.22)        # RTK -> SHP2
arrow(A, (45.5, 100.0), (57.5, AY + AH))                 # integrins -> SHP2
arrow(A, (68.5, 100.0), (78.0, AY + AH))                 # GPCRs -> GEFs
arrow(A, (88.0, 99.5), (86.0, AY + AH))                  # immune -> RasGRP
arrow(A, (20, AY + AH / 2), (23, AY + AH / 2))           # GRB2 -> SOS1
arrow(A, (48, AY + 2.2), (45, AY + 2.8), color=C['grey'])  # SHP2 -> GRB2-SOS1
tag(A, 8, 82.5, 'SHP2 and SOS1 inhibitors act on this layer', status='clinical',
    fs=FS['tiny'])

# --- the nucleotide switch ----------------------------------------------------
SY = 72.0
switch(A, 48, SY, 'OFF state', C['off'], C['ink'], 'GDP', '#4A5560')
switch(A, 104, SY, 'ON state', C['on'], 'white', 'GTP', C['on'])

arrow(A, (63, 77.0), (89, 77.0), rad=-0.38, lw=0.9)      # exchange
arrow(A, (89, 67.0), (63, 67.0), rad=-0.38, lw=0.9)      # hydrolysis
A.text(76, 84.0, 'nucleotide exchange (GEF: SOS1)', ha='center', va='bottom',
       fontsize=FS['small'], color=C['adaptor'])
A.text(76, 59.8, 'GTP hydrolysis (GAP: NF1)', ha='center', va='top',
       fontsize=FS['small'], color=C['grey'])
arrow(A, (34, AY), (69, 81.5), color=C['adaptor'])       # SOS1 -> exchange

capsule(A, 126, 61, 32, 10, 'NF1, RASA1\nGAPs', C['gap'], fs=FS['small'])
A.text(126, 59.0, 'lost in ' + GI('NF1') + '-mutant tumours; germline\n'
       'loss causes RASopathies', fontsize=FS['tiny'], color=C['grey'],
       ha='left', va='top', linespacing=1.3)
arrow(A, (126, 66.0), (88, 64.5), color=C['gap'])        # GAP -> hydrolysis

A.add_patch(Rectangle((124, 88), 47, 14, facecolor=C['light'],
                      edgecolor=C['grey'], linewidth=LW['thin'], zorder=1))
A.text(125.5, 100.6, 'Substitutions at codons 12, 13 and 61 impair\n'
                     'GAP-stimulated hydrolysis, so the switch accumulates\n'
                     'in the GTP-bound state; the residual nucleotide cycling\n'
                     'left to each allele decides which drug class can work.',
       fontsize=FS['tiny'], ha='left', va='top', linespacing=1.35, zorder=2)

tag(A, 14, 59.0, 'OFF-state covalent inhibitors (' + GI('KRAS') + ' G12C)',
    status='approved')
tag(A, 14, 55.0, 'OFF-state inhibitors of non-cysteine alleles', status='clinical')
tag(A, 124, 79.0, 'RAS(ON) tri-complex inhibitors: allele-selective\n'
                  'and multi-selective (pan-RAS)', status='approved')
tag(A, 124, 74.0, 'RAS degraders; effector-interface binders', status='clinical')

# --- effector fan -------------------------------------------------------------
arrow(A, (104, 63.0), (104, 51.0), lw=0.9)
A.plot([13, 161], [50.0, 50.0], color=C['edge'], linewidth=LW['arrow'], zorder=2)
A.text(101, 51.8, 'effector binding (switch I and the interswitch surface)',
       fontsize=FS['tiny'], color=C['grey'], ha='right', va='bottom')

TIERS = [40.0, 29.0, 18.0]
CHAIN = [(C['mapk'], 6, 34, ['RAF (BRAF, CRAF)', 'MEK1/2', 'ERK1/2'],
          [('RAF and MEK inhibitors', 'approved'),
           ('ERK inhibitors', 'clinical')]),
         (C['pi3k'], 46, 32, ['PI3K (p110)', 'AKT', 'mTORC1'],
          [('PI3K, AKT and mTOR inhibitors', 'approved'),
           ('blocking one trunk de-represses the other', 'clinical')]),
         (C['ral'], 84, 30, ['RALGDS', 'RAL', 'vesicle traffic,\nsecretion'],
          [('no selective agent in the clinic', 'preclinical')])]
for col, x, w, labels, tags in CHAIN:
    for i, lbl in enumerate(labels):
        y = TIERS[i]
        capsule(A, x, y, w, 8.5, lbl, col,
                fs=FS['small'] if '\n' in lbl else FS['anno'], bold=(i < 2))
        if i:
            arrow(A, (x + w / 2, TIERS[i - 1]), (x + w / 2, y + 8.5))
    arrow(A, (x + w / 2, 50.0), (x + w / 2, TIERS[0] + 8.5))
    for j, (tg, st) in enumerate(tags):
        tag(A, x, 13.0 - 3.4 * j, tg, status=st, fs=FS['tiny'])

# fourth branch: two parallel effectors feeding one output
capsule(A, 120, TIERS[0], 24, 8.5, u'PLCε', C['other'])
capsule(A, 147, TIERS[0], 23, 8.5, 'TIAM1', C['other'])
capsule(A, 120, TIERS[1], 24, 8.5, 'DAG, PKC', C['other'], fs=FS['small'])
capsule(A, 147, TIERS[1], 23, 8.5, 'RAC', C['other'])
capsule(A, 120, TIERS[2], 50, 8.5, 'actin remodelling, migration and invasion',
        C['other'], fs=FS['small'], bold=False)
for x, w in ((120, 24), (147, 23)):
    arrow(A, (x + w / 2, 50.0), (x + w / 2, TIERS[0] + 8.5))
    arrow(A, (x + w / 2, TIERS[0]), (x + w / 2, TIERS[1] + 8.5))
    arrow(A, (x + w / 2, TIERS[1]), (x + w / 2, TIERS[2] + 8.5))
tag(A, 120, 13.0, 'no selective agent in the clinic', status='preclinical',
    fs=FS['tiny'])
tag(A, 120, 9.6, 'effector use differs by allele and by tissue', status='clinical',
    fs=FS['tiny'])

# --- ERK-mediated negative feedback -------------------------------------------
A.plot([6, 2.5, 2.5, 28.0, 28.0], [22.2, 22.2, 85.5, 85.5, 86.9],
       color=C['on'], linewidth=LW['arrow'], linestyle=DASH, zorder=4)
A.plot([28.0], [87.1], marker='_', markersize=4.0, color=C['on'], zorder=4)
A.text(4.4, 29, 'ERK-mediated negative feedback on SOS1, CRAF and the receptors',
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
    (2, 'Metabolic reprogramming', icon_metabolic,
     'Increased glucose uptake, rewired\nglutamine use, scavenging of\nextracellular nutrients',
     'metabolic co-targeting', 'preclinical'),
    (45, 'Macropinocytosis and autophagy', icon_macropino,
     'Protein and amino-acid recycling\nsustains growth and becomes a\nsurvival route under drug pressure',
     'autophagy inhibition', 'clinical'),
    (88, 'Immunosuppressive microenvironment', icon_immune,
     'Higher PD-L1, recruitment of myeloid\nsuppressor cells, reduced antigen\npresentation',
     'checkpoint blockade; mutant-RAS\nvaccines and TCR-T cells', 'clinical'),
    (131, 'Senescence and oncogenic stress', icon_senescence,
     'A barrier that must be bypassed:\ncarrying a mutation is not the same\nas depending on it',
     'no therapeutic use; constrains how\nmutation data are read', 'preclinical'),
]
for x, head, icon, body, tg, st in PH:
    B.add_patch(FancyBboxPatch((x + 1.2, 5.2), 36.6, 21.6,
                               boxstyle='round,pad=1.2,rounding_size=1.4',
                               facecolor=C['pheno'], edgecolor=C['edge'],
                               linewidth=LW['box'], zorder=1))
    B.text(x + 2.4, 26.0, head, fontsize=FS['small'], fontweight='bold',
           ha='left', va='top', zorder=2)
    B.text(x + 2.4, 21.4, body, fontsize=FS['tiny'], ha='left', va='top',
           zorder=2, linespacing=1.4)
    icon(B, x + 31.0, 11.5)
    tag(B, x + 2.4, 7.0, tg, status=st, fs=FS['tiny'])
S.panel(fig, B, 'b')

S.save(fig, 'Fig7_RAS_signalling_network', FIG)
