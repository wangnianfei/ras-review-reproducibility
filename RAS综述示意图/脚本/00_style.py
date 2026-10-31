#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared style for the schematic figures of the RAS review (Fig7-Fig9, Fig11).

Identical style contract to RAS基因与蛋白结构/脚本/03_figures.py so that
all figures of the review look like one set:
  canvas      double column 180 mm wide, height per figure, never > 230 mm
  type        Arial; panel letter 8 pt bold; in-figure annotation 6 pt; min 5 pt
  rules       box 0.5 pt, connectors 0.6 pt, leader lines 0.4 pt
  panels      lowercase bold letters a, b, c outside the top-left of each axes
  no titles   figure titles live in Figure_legends.md, never in the artwork
  no Chinese  every piece of in-figure text is English
  genes       italic (GI helper); protein names roman
  coding      categories are told apart by SHAPE first, colour second, so the
              figures survive greyscale printing and colour-blind readers
Drawing coordinates are millimetres on the physical page: an axes created with
`mm_axes` has data units == mm, so every box below is positioned to the millimetre.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon

MM = 1 / 25.4
W2 = 180.0                                   # double-column width, mm

FS = {'panel': 8, 'head': 7, 'anno': 6, 'small': 5.5, 'tiny': 5}
LW = {'box': 0.5, 'arrow': 0.6, 'lead': 0.4, 'thin': 0.3}

plt.rcParams.update({
    'font.family': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
    'font.size': FS['anno'], 'axes.linewidth': LW['box'],
    'legend.frameon': False, 'legend.fontsize': FS['anno'],
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
    'mathtext.bfit': 'Arial:italic:bold',
})

# palette: one hue per functional layer, all mid-tone so white or black text reads
C = {
    'membrane': '#D8DEE4', 'receptor': '#8FB3CC', 'adaptor': '#5B8FB9',
    'gap': '#9AA4AB', 'off': '#BFCBD4', 'on': '#D7263D',
    'mapk': '#2E6F9E', 'pi3k': '#1C7C54', 'ral': '#6A4C93', 'other': '#8C3B12',
    'pheno': '#E8EDF1', 'drug': '#1A1A1A', 'ink': '#1A1A1A', 'grey': '#555555',
    'light': '#F2F5F7', 'edge': '#3A3A3A',
    'lane1': '#2E6F9E', 'lane2': '#1C7C54', 'lane3': '#D7263D',
    'lane4': '#6A4C93', 'lane5': '#8C3B12',
}


def GI(sym, extra=''):
    """Gene symbols italic, protein names roman (Nature convention)."""
    s = r'$\it{%s}$' % sym.replace(' ', r'\ ')
    return s + (' ' + extra if extra else '')


def figure(h_mm, w_mm=W2):
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM))
    fig._mm = (w_mm, h_mm)
    return fig


def mm_axes(fig, x, y, w, h):
    """Axes placed by mm rectangle whose data units are also mm."""
    W, H = fig._mm
    ax = fig.add_axes([x / W, y / H, w / W, h / H])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_axis_off()
    ax.set_aspect('auto')
    return ax


def panel(fig, ax, letter, dx=-4.5, dy=1.0):
    W, H = fig._mm
    bb = ax.get_position()
    fig.text((bb.x0 * W + dx) / W, (bb.y1 * H + dy) / H, letter,
             fontsize=FS['panel'], fontweight='bold', ha='left', va='bottom')


def box(ax, x, y, w, h, label, fc='white', ec=None, tc=None, fs=None,
        bold=False, r=0.8, lw=None, ls='-', va='center', pad=0.0, z=3):
    """Rounded box with centred label; (x, y) is the bottom-left corner in mm."""
    ec = ec if ec is not None else C['edge']
    tc = tc if tc is not None else C['ink']
    ax.add_patch(FancyBboxPatch((x + r, y + r), w - 2 * r, h - 2 * r,
                                boxstyle='round,pad=%.2f' % r, linewidth=lw or LW['box'],
                                linestyle=ls, facecolor=fc, edgecolor=ec, zorder=z))
    ax.text(x + w / 2, y + h / 2 + pad, label, ha='center', va=va, zorder=z + 1,
            fontsize=fs or FS['anno'], color=tc,
            fontweight='bold' if bold else 'normal', linespacing=1.25)
    return (x + w / 2, y, x + w / 2, y + h)          # centre bottom / centre top


def arrow(ax, p0, p1, style='-|>', ls='-', color=None, lw=None, rad=0.0,
          z=2, ms=2.2):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms * 3,
                                 linewidth=lw or LW['arrow'], linestyle=ls,
                                 color=color or C['edge'], zorder=z,
                                 connectionstyle='arc3,rad=%.2f' % rad,
                                 shrinkA=1.5, shrinkB=1.5, joinstyle='miter'))


def tee(ax, p0, p1, color=None, lw=None, ls='--', z=2):
    """Inhibition connector: line ending in a bar."""
    arrow(ax, p0, p1, style='|-|,widthA=0,widthB=1.6', ls=ls,
          color=color or C['grey'], lw=lw, z=z)


# ---- drug-class markers: SHAPE encodes how far the class has got clinically ---
# circle   = at least one regulatory approval
# square   = in clinical trials (phase 1-3), nothing approved yet
# triangle = preclinical only, or clinically tested and abandoned
MARK = {'approved': 'o', 'clinical': 's', 'preclinical': '^'}


def drug_tag(ax, x, y, text, status='clinical', w=None, fs=None, align='left',
             color=None, z=6):
    """Pill-shaped drug-class tag with a status marker, anchored at (x, y) mid-left."""
    fs = fs or FS['small']
    color = color or C['drug']
    ax.plot([x], [y], marker=MARK[status], markersize=2.6, markerfacecolor=color,
            markeredgecolor=color, linewidth=0, zorder=z + 1)
    ax.text(x + 1.4, y, text, ha=align, va='center', fontsize=fs, color=color,
            zorder=z + 1, linespacing=1.2)


def status_key(ax, x, y, items=('approved', 'clinical', 'preclinical'),
               labels=('approved drug class',
                       'in clinical trials (phase 1-3)',
                       'preclinical only, or tested and abandoned'),
               dy=3.0, fs=None):
    for i, (st, lb) in enumerate(zip(items, labels)):
        drug_tag(ax, x, y - i * dy, lb, status=st, fs=fs or FS['small'])


def save(fig, name, outdir):
    import os
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(os.path.join(outdir, '%s.%s' % (name, ext)), dpi=400,
                    facecolor='white')
    plt.close(fig)
    print('  ->', name)
