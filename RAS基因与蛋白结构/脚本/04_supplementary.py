#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the PyMOL renders into single-column supplementary figures.

Usage: python3 04_supplementary.py <root>
Input : figures/_S1_*.png, _S2_*.png, _S3_*.png  (from render_supplementary_pymol.pml)
Output: figures/FigS1..FigS3  .pdf / .svg / .png
Same style contract as 03_figures.py: 88 mm single column, Arial, no titles,
no Chinese, colour keys inside the panel, titles live in Figure_legends.md.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = sys.argv[1]
FIG = os.path.join(ROOT, 'figures')
MM = 1 / 25.4
W1 = 88.0                                   # single-column width, mm

plt.rcParams.update({
    'font.family': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
    'legend.frameon': False, 'font.size': 6,
})

C = {'ploop': '#1C7C54', 'sw1': '#E09F3E', 'sw2': '#BF3100', 'g4': '#6A4C93',
     'g5': '#9D6DBF', 'hot': '#D7263D', 'gdp': '#355070', 'gtp': '#2E86AB',
     'cool': '#9FB4C7', 'warm': '#D08C60', 'mg': '#1C7C54'}
AF = [('≥90 very high', '#0053D6'), ('70–90 confident', '#65CBF3'),
      ('50–70 low', '#FFDB13'), ('<50 very low', '#FF7D45')]


def line(c, label, lw=2.6):
    return plt.Line2D([], [], color=c, lw=lw, label=label)


def dot(c, label, ms=3.4, mec='none', mew=0):
    return plt.Line2D([], [], ls='', marker='o', color=c, ms=ms, label=label,
                      mec=mec, mew=mew)


def crop(path):
    img = plt.imread(path)
    if img.ndim == 3 and img.shape[2] == 4:
        a = img[:, :, 3] > 0.02
        rs, cs = np.where(a.any(1))[0], np.where(a.any(0))[0]
        pad = int(0.012 * max(img.shape[:2]))
        img = img[max(rs[0] - pad, 0):rs[-1] + pad,
                  max(cs[0] - pad, 0):cs[-1] + pad]
    return img


def build(src, out, handles, ncol, key_mm=11.0):
    img = crop(os.path.join(FIG, src))
    h_img = W1 * img.shape[0] / img.shape[1]          # keep aspect, mm
    H = h_img + key_mm
    fig = plt.figure(figsize=(W1 * MM, H * MM))
    ax = fig.add_axes([0, key_mm / H, 1, h_img / H])
    ax.imshow(img, interpolation='antialiased')
    ax.set_axis_off()
    lg = fig.add_axes([0, 0, 1, key_mm / H])
    lg.set_axis_off()
    lg.legend(handles=handles, loc='center', ncol=ncol, fontsize=5.8,
              handlelength=1.3, columnspacing=0.9, handletextpad=0.45,
              borderpad=0.1, labelspacing=0.35)
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(os.path.join(FIG, '%s.%s' % (out, ext)), dpi=400,
                    facecolor='white')
    plt.close(fig)
    print('  -> %s   %.0f x %.0f mm' % (out, W1, H))


build('_S1_KRAS_GDP_4OBE.png', 'FigS1_KRAS_GDP_structure',
      [line(C['ploop'], 'P-loop'), line(C['sw1'], 'switch I'),
       line(C['sw2'], 'switch II'), line(C['g4'], 'G4'), line(C['g5'], 'G5'),
       dot(C['gdp'], 'GDP'), dot(C['mg'], 'Mg2+'),
       dot(C['hot'], 'Gly12', mec='k', mew=0.3)], ncol=4)

build('_S2_GDP_vs_GTP_overlay.png', 'FigS2_GDP_vs_GTP_superposition',
      [line(C['cool'], 'KRAS–GDP (4OBE)'), line(C['gtp'], 'switch I/II, GDP state'),
       line(C['warm'], 'KRAS–GTP (5VQ2)'), line(C['sw2'], 'switch I/II, GTP state'),
       dot(C['gdp'], 'GDP'), dot(C['sw2'], 'GTP'), dot(C['mg'], 'Mg2+')],
      ncol=3, key_mm=13.0)

build('_S3_AlphaFold_pLDDT.png', 'FigS3_AlphaFold_pLDDT_model',
      [line(c, n) for n, c in AF], ncol=4)

print('supplementary figures ->', FIG)
