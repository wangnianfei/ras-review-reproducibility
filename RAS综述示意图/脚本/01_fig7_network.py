#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 7 - the RAS signalling network: inputs, the switch, effectors, phenotypes.

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
from matplotlib.patches import Rectangle

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '..')
FIG = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)
C, FS, LW, GI = S.C, S.FS, S.LW, S.GI
box, arrow, tee, tag = S.box, S.arrow, S.tee, S.drug_tag
DASH = (0, (3, 2))

fig = S.figure(180.0)
A = S.mm_axes(fig, 4, 52, 172, 122)
B = S.mm_axes(fig, 4, 6, 172, 36)

# ===================================================== panel a: the network ====
# --- plasma membrane and cell-surface inputs ----------------------------------
A.add_patch(Rectangle((2, 109.5), 168, 4.5, facecolor=C['membrane'],
                      edgecolor=C['grey'], linewidth=LW['thin'], zorder=1))
A.text(2, 119.5, 'Extracellular inputs', fontsize=FS['small'], color=C['grey'],
       ha='left', va='top')
A.text(170, 111.7, 'plasma membrane', fontsize=FS['tiny'], color=C['grey'],
       ha='right', va='center', zorder=2)
for lbl, x, w in [('Receptor tyrosine\nkinases', 6, 30), ('Integrins', 40, 22),
                  ('G-protein-coupled\nreceptors', 66, 28),
                  ('Antigen and\nimmune receptors', 98, 30)]:
    box(A, x, 106, w, 11.5, lbl, fc=C['receptor'], tc='white', fs=FS['small'],
        bold=True)

# --- adaptor / exchange-factor layer ------------------------------------------
box(A, 6, 92, 18, 9, 'GRB2', fc=C['adaptor'], tc='white', bold=True)
box(A, 27, 92, 24, 9, 'SOS1\n(GEF)', fc=C['adaptor'], tc='white', fs=FS['small'],
    bold=True)
box(A, 54, 92, 20, 9, 'SHP2', fc=C['adaptor'], tc='white', bold=True)
box(A, 77, 92, 30, 9, 'Tissue-restricted\nGEFs',
    fc=C['adaptor'], tc='white', fs=FS['tiny'])
box(A, 118, 92, 30, 9, 'NF1, RASA1\n(GAPs)', fc=C['gap'], tc='white',
    fs=FS['small'], bold=True)
A.text(149, 96.5, 'lost in ' + GI('NF1') + '-mutant\ntumours; germline loss\ncauses RASopathies',
       fontsize=FS['tiny'], color=C['grey'], ha='left', va='center')

arrow(A, (18, 106), (15, 101))                       # RTK -> GRB2
arrow(A, (24, 96.5), (27, 96.5))                     # GRB2 -> SOS1
# SHP2 receives two inputs: it is recruited to phosphorylated RTK / GAB scaffolds, and it
# also transduces signals downstream of integrin receptors -- Ruess 2018
# (4.5_RuessDA_2018_29808009): "SHP2, encoded by PTPN11, is involved in signal
# transduction downstream of multiple growth factor, cytokine and integrin receptors".
# The two connectors start at different x and never cross.
arrow(A, (32, 106), (57, 101))                       # RTK -> SHP2
arrow(A, (49, 106), (71, 101))                       # integrins -> SHP2
arrow(A, (62, 101), (52, 98), color=C['grey'])       # SHP2 -> GRB2-SOS1 complex
arrow(A, (80, 106), (86, 101))                       # GPCRs -> tissue-restricted GEFs
arrow(A, (113, 106), (100, 101))                     # immune receptors -> RasGRP
# two lines, kept left of the feedback line at x = 33
tag(A, 6, 88.5, 'SHP2 and SOS1 inhibitors\nact on this layer', status='clinical',
    fs=FS['tiny'])

# --- the switch ---------------------------------------------------------------
box(A, 20, 67, 38, 14, 'RAS' + u'–' + 'GDP\nOFF state', fc=C['off'],
    tc=C['ink'], fs=FS['head'], bold=True)
box(A, 78, 67, 38, 14, 'RAS' + u'–' + 'GTP\nON state', fc=C['on'],
    tc='white', fs=FS['head'], bold=True)
arrow(A, (58, 77), (78, 77), rad=-0.42, lw=0.9)
A.text(68, 86.5, 'nucleotide exchange (GEF: SOS1)', fontsize=FS['small'],
       ha='center', va='bottom')
arrow(A, (78, 71), (58, 71), rad=-0.42, lw=0.9)
A.text(68, 59.0, 'GTP hydrolysis (GAP: NF1)', fontsize=FS['small'],
       ha='center', va='top')
arrow(A, (39, 92), (65, 81.3), color=C['adaptor'])            # SOS1 -> exchange
# the label sits above the arrow: the tip stops on the exchange arc, clear of the text
A.plot([120, 120, 76], [92, 62, 62], color=C['gap'], linewidth=LW['arrow'],
       zorder=2, solid_joinstyle='miter')                     # GAP -> hydrolysis
arrow(A, (78, 62), (70, 63.8), color=C['gap'])

A.add_patch(Rectangle((124, 67), 46, 19, facecolor=C['light'],
                      edgecolor=C['grey'], linewidth=LW['thin'], zorder=1))
A.text(125.5, 84.3, 'Substitutions at codons 12, 13 and 61 impair\n'
                    'GAP-stimulated hydrolysis, so the switch accumulates\n'
                    'in the GTP-bound state; the residual nucleotide cycling\n'
                    'left to each allele decides which drug class can work.',
       fontsize=FS['tiny'], ha='left', va='top', linespacing=1.35, zorder=2)

tag(A, 21, 55.0, 'OFF-state covalent inhibitors (' + GI('KRAS') + ' G12C)',
    status='approved')
tag(A, 21, 51.0, 'OFF-state inhibitors of non-cysteine alleles',
    status='clinical')
tag(A, 124, 58.5, 'RAS(ON) tri-complex inhibitors: allele-selective\n'
                  'and multi-selective (pan-RAS)', status='approved')
tag(A, 124, 53.0, 'RAS degraders; effector-interface binders',
    status='clinical')

# --- effector fan ------------------------------------------------------------
arrow(A, (97, 67), (97, 49.5), lw=0.9)
A.plot([13, 161], [48.5, 48.5], color=C['edge'], linewidth=LW['arrow'], zorder=2)
A.text(99, 50.4, 'effector binding (switch I and the interswitch surface)',
       fontsize=FS['tiny'], color=C['grey'], ha='left', va='bottom')

TIERS = [38.5, 27.5, 16.5]
CHAIN = [(C['mapk'], 6, 34, ['RAF (BRAF, CRAF)', 'MEK1/2', 'ERK1/2'],
          [('RAF and MEK inhibitors', 'approved'),
           ('ERK inhibitors', 'clinical')]),
         (C['pi3k'], 46, 32, ['PI3K (p110)', 'AKT', 'mTORC1'],
          [('PI3K, AKT and mTOR inhibitors', 'approved'),
           ('blocking one trunk de-represses the other', 'clinical')]),
         (C['ral'], 84, 30, ['RALGDS', 'RAL',
                             'vesicle traffic,\nsecretion'],
          [('no selective agent in the clinic', 'preclinical')])]
for col, x, w, labels, tags in CHAIN:
    for i, lbl in enumerate(labels):
        y = TIERS[i]
        box(A, x, y, w, 8, lbl, fc=col, tc='white',
            fs=FS['small'] if '\n' in lbl else FS['anno'], bold=(i < 2))
        if i:
            arrow(A, (x + w / 2, TIERS[i - 1]), (x + w / 2, y + 8))
    arrow(A, (x + w / 2, 48.5), (x + w / 2, TIERS[0] + 8))
    for j, (tg, st) in enumerate(tags):
        tag(A, x, 13.0 - 3.4 * j, tg, status=st, fs=FS['tiny'])

# fourth branch: two parallel effectors feeding one output
box(A, 120, 38.5, 24, 8, u'PLCε', fc=C['other'], tc='white', bold=True)
box(A, 147, 38.5, 23, 8, 'TIAM1', fc=C['other'], tc='white', bold=True)
# PLCe acts mainly through DAG -> PKC/PKD rather than calcium release, so the node names DAG
box(A, 120, 27.5, 24, 8, 'DAG, PKC', fc=C['other'], tc='white', fs=FS['small'])
box(A, 147, 27.5, 23, 8, 'RAC', fc=C['other'], tc='white', bold=True)
box(A, 120, 16.5, 50, 8, 'actin remodelling, migration and invasion',
    fc=C['other'], tc='white', fs=FS['small'])
for x, w in ((120, 24), (147, 23)):
    arrow(A, (x + w / 2, 48.5), (x + w / 2, 46.5))
    arrow(A, (x + w / 2, 38.5), (x + w / 2, 35.5))
    arrow(A, (x + w / 2, 27.5), (x + w / 2, 24.5))
tag(A, 120, 13.0, 'no selective agent in the clinic', status='preclinical',
    fs=FS['tiny'])
tag(A, 120, 9.6, 'effector use differs by allele and by tissue', status='clinical',
    fs=FS['tiny'])

# --- ERK-mediated negative feedback ------------------------------------------
A.plot([6, 2.5, 2.5, 33, 33], [20.5, 20.5, 84.5, 84.5, 91.0], color=C['on'],
       linewidth=LW['arrow'], linestyle=DASH, zorder=4)
A.plot([33], [91.0], marker='_', markersize=3.6, color=C['on'], zorder=4)
# the label runs the whole length of the vertical feedback segment and must stay below
# the horizontal run at y = 84.5 (54.6 mm of text at 5 pt, so the anchor sits at y = 28)
A.text(4.4, 28, 'ERK-mediated negative feedback on SOS1, CRAF and the receptors',
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
PH = [
    (2, 'Metabolic reprogramming',
     'Increased glucose uptake, rewired\nglutamine use, scavenging of\nextracellular nutrients',
     'metabolic co-targeting', 'preclinical'),
    (45, 'Macropinocytosis and autophagy',
     'Protein and amino-acid recycling\nsustains growth and becomes a\nsurvival route under drug pressure',
     'autophagy inhibition', 'clinical'),
    (88, 'Immunosuppressive microenvironment',
     'Higher PD-L1, recruitment of myeloid\nsuppressor cells, reduced antigen\npresentation',
     'checkpoint blockade; mutant-RAS\nvaccines and TCR-T cells', 'clinical'),
    (131, 'Senescence and oncogenic stress',
     'A barrier that must be bypassed:\ncarrying a mutation is not the same\nas depending on it',
     'no therapeutic use; constrains how\nmutation data are read', 'preclinical'),
]
for x, head, body, tg, st in PH:
    B.add_patch(Rectangle((x, 4), 39, 24, facecolor=C['pheno'],
                          edgecolor=C['edge'], linewidth=LW['box'], zorder=1))
    B.text(x + 1.6, 26.2, head, fontsize=FS['small'], fontweight='bold',
           ha='left', va='top', zorder=2)
    B.text(x + 1.6, 21.6, body, fontsize=FS['tiny'], ha='left', va='top',
           zorder=2, linespacing=1.4)
    tag(B, x + 1.6, 7.0, tg, status=st, fs=FS['tiny'])
S.panel(fig, B, 'b')

S.save(fig, 'Fig7_RAS_signalling_network', FIG)
