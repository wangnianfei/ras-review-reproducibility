#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication-grade figures for the RAS review (v2, mm-exact layout).

Usage: python3 03_figures.py <root>
Output: <root>/figures/Fig*.pdf  (vector, text kept editable)
                       Fig*.svg  (vector, text not converted to paths)
                       Fig*.png  (400 dpi, preview only)

Style contract (applies to every figure):
  canvas      double column 180 mm wide, heights set per figure, never > 230 mm
  type        Arial; panel letter 8 pt bold; axis title 7 pt; ticks 6.5 pt;
              in-figure annotation 6 pt; nothing below 5 pt
  rules       axis/box 0.5 pt; data lines 1.0-1.2 pt; leader lines 0.4 pt
  panels      lowercase bold letters a, b, c at the top-left outside each panel
  no titles   figure titles live in Figure_legends.md, never in the artwork
  no Chinese  all in-figure text is English
  colours     fixed palette below (colour-blind checked)
All numbers come from 数据/表1-表7; nothing is estimated or rounded for looks.
A self-check block at the end re-prints the key values for verification.
"""
import collections, csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Polygon, FancyBboxPatch

ROOT = sys.argv[1]
DATA = os.path.join(ROOT, '数据')
FIG = os.path.join(ROOT, 'figures')
STRU = os.path.join(ROOT, '结构文件')
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------- style ----
MM = 1 / 25.4                     # mm -> inch
PT = 72 * MM                      # mm -> points  (2.8346)
W2 = 180.0                        # double-column width, mm

FS = {'panel': 8, 'axis': 7, 'tick': 6.5, 'anno': 6, 'small': 5.5}
LW = {'axis': 0.5, 'data': 1.1, 'lead': 0.4, 'edge': 0.3}

plt.rcParams.update({
    'font.family': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
    'axes.linewidth': LW['axis'],
    'xtick.major.width': LW['axis'], 'ytick.major.width': LW['axis'],
    'xtick.major.size': 2.0, 'ytick.major.size': 2.0,
    'xtick.labelsize': FS['tick'], 'ytick.labelsize': FS['tick'],
    'axes.labelsize': FS['axis'], 'font.size': FS['anno'],
    'legend.frameon': False, 'legend.fontsize': FS['anno'],
    'legend.handlelength': 1.5, 'legend.handletextpad': 0.5,
    'legend.labelspacing': 0.35, 'legend.columnspacing': 1.2,
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
    'mathtext.bfit': 'Arial:italic:bold',
})


def GI(sym, bold=False):
    """Gene symbols are italic; protein names stay roman (Nature convention)."""
    return (r'$\mathbfit{%s}$' if bold else r'$\it{%s}$') % sym

C = {'cds': '#2E6F9E', 'utr': '#BFCBD4', 'intron': '#8A939B', 'hot': '#D7263D',
     'ploop': '#1C7C54', 'sw1': '#E09F3E', 'g3': '#8C3B12', 'sw2': '#BF3100',
     'g4': '#6A4C93', 'g5': '#9D6DBF', 'hvr': '#6F7378',
     'helix': '#C44536', 'strand': '#355070',
     'k': '#D7263D', 'h': '#2E86AB', 'n': '#E07A5F', 'grey': '#555555'}

# region definitions used across figures (switch II per Vetter & Wittinghofer)
REG = [('P-loop', 10, 17, C['ploop']), ('switch I', 30, 38, C['sw1']),
       ('switch II', 60, 76, C['sw2']), ('G4', 116, 119, C['g4']),
       ('G5', 145, 147, C['g5']), ('HVR', 167, 189, C['hvr'])]

CHECK = {}


# ------------------------------------------------------------- plumbing ----
def figure(h_mm, w_mm=W2):
    """Create a figure of exact physical size; return (fig, w_mm, h_mm)."""
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM))
    fig._mm = (w_mm, h_mm)
    return fig


def axes(fig, x, y, w, h, **kw):
    """Place an axes by millimetre rectangle measured from the bottom-left."""
    W, H = fig._mm
    return fig.add_axes([x / W, y / H, w / W, h / H], **kw)


def panel(fig, ax, letter, dx=-5.0, dy=1.2):
    """Put a lowercase bold panel letter outside the top-left of an axes."""
    W, H = fig._mm
    bb = ax.get_position()
    fig.text((bb.x0 * W + dx) / W, (bb.y1 * H + dy) / H, letter,
             fontsize=FS['panel'], fontweight='bold', ha='left', va='bottom')


def dot_area(d_mm):
    """matplotlib scatter 's' (pt^2) for a marker of diameter d_mm."""
    return np.pi / 4 * (d_mm * 72 * MM) ** 2


def save(fig, name):
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(os.path.join(FIG, '%s.%s' % (name, ext)), dpi=400,
                    facecolor='white')          # no bbox_inches: keep exact mm
    plt.close(fig)
    print('  ->', name)


def rows(fn):
    with open(os.path.join(DATA, fn)) as f:
        return list(csv.DictReader(f))


def I(v):
    return int(v) if v not in ('', None) else 0


def fmt(n):
    return format(int(n), ',')


EX = rows('表1_外显子结构.csv')
HOT = rows('表2_热点密码子定位.csv')
FEAT = rows('表3_蛋白结构特征.csv')
MUT = rows('表4_突变谱_MSK-IMPACT.csv')
BYCT = rows('表5_各癌种突变频率_MSK-IMPACT.csv')
COV = rows('表7_实验结构可见残基.csv')
PLD = json.load(open(os.path.join(DATA, 'alphafold_plddt.json')))
META = json.load(open(os.path.join(DATA, 'prepared_meta.json')))
PDBM = json.load(open(os.path.join(DATA, 'pdb_entries.json')))
GCORE = json.load(open(os.path.join(DATA, 'genes_core.json')))
NTOT = META['cohort']['n_samples']

TXS = {'KRAS4B': 'ENST00000311936', 'KRAS4A': 'ENST00000256078',
       'HRAS': 'ENST00000311189', 'NRAS': 'ENST00000369535'}
LAB = {'KRAS4B': (GI('KRAS') + '  ENST00000311936.8 / NM_004985.5',
                  'MANE Select (KRAS4B protein, 188 aa)'),
       'KRAS4A': (GI('KRAS') + '  ENST00000256078.10 / NM_033360.4',
                  'MANE Plus Clinical (KRAS4A protein, 189 aa)'),
       'HRAS': (GI('HRAS') + '  ENST00000311189.8 / NM_005343.4',
                'MANE Select (189 aa)'),
       'NRAS': (GI('NRAS') + '  ENST00000369535.5 / NM_002524.5',
                'MANE Select (189 aa)')}
CYTO = {'KRAS4B': '12p12.1', 'HRAS': '11p15.5', 'NRAS': '1p13.2'}
HOTLAB = {12: 'G12', 13: 'G13', 61: 'Q61', 117: 'K117', 146: 'A146'}


def exons(tx):
    return sorted([e for e in EX if e['transcript'] == tx],
                  key=lambda e: int(e['exon_rank']))


# =========================================================== Figure 1 ======
# Manuscript Figure 2. Layout rebuilt 2026-11-01 (author: the old one was not
# publication-grade). Two changes carry the redesign:
#   panel a  three loci on one tight baseline grid, axis directly under the
#            tracks, legend on the panel's top line — no floating blocks;
#   panel b  drawn in CODON coordinates, so coding exons 2-4 fall into shared
#            columns across all four transcripts. The point of the figure —
#            the coding exons are identical in all three genes, divergence is
#            confined to the last one — is now carried by the layout instead
#            of by the reader comparing printed numbers. Per-exon numbers that
#            are the same in every row are printed once, under the columns.
# Palette: one ink-blue value ramp (CDS -> UTR) plus a single vermilion accent
# reserved for hotspot codons; nothing else is coloured.
P1 = {'cds': '#1B3A5C', 'utr': '#C7D3DE', 'intron': '#93A1AE',
      'band': '#EDF2F7', 'hot': '#CC3311', 'ink': '#1A1A1A', 'grey': '#5B6770'}
CLIP_BP = 330.0          # exons longer than this are drawn truncated (*)


def fig1():
    from matplotlib.transforms import blended_transform_factory as blend
    P, H, GUT = P1, 114.0, 31.0
    fig = figure(H)

    # ------------------------------------------- panel a: genomic extent --
    AH = 22.0
    axA = axes(fig, GUT, H - 12.5 - AH, W2 - GUT - 6, AH)
    order = ['KRAS4B', 'HRAS', 'NRAS']
    axA.set_xlim(-0.6, 53.5)
    axA.set_ylim(-0.8, 2.7)
    uA = AH / 3.5                                   # mm per data unit
    hc, hu = 2.0 / uA, 1.25 / uA
    tA = blend(axA.transAxes, axA.transData)
    for i, key in enumerate(order):
        ex = exons(TXS[key])
        g = ex[0]['gene']
        hi = max(I(e['exon_end']) for e in ex)
        lo = min(I(e['exon_start']) for e in ex)
        span = (hi - lo) / 1000.0
        y = len(order) - 1 - i

        def X(p, _hi=hi):
            return (_hi - p) / 1000.0
        axA.plot([0, span], [y, y], color=P['intron'], lw=0.6, zorder=1,
                 solid_capstyle='butt')
        for e in ex:
            if I(e['utr_len']):
                a0, b0 = X(I(e['exon_end'])), X(I(e['exon_start']))
                axA.add_patch(Rectangle((a0, y - hu / 2), max(b0 - a0, 0.10),
                                        hu, fc=P['utr'], ec=P['cds'], lw=0.2,
                                        zorder=2))
            if I(e['coding_len']):
                a0, b0 = X(I(e['coding_end'])), X(I(e['coding_start']))
                axA.add_patch(Rectangle((a0, y - hc / 2), max(b0 - a0, 0.10),
                                        hc, fc=P['cds'], ec='none', zorder=3))
        axA.text(-0.012, y, '%s  %s' % (GI(g), CYTO[key]), transform=tA,
                 ha='right', va='center', fontsize=FS['anno'], color=P['ink'])
        axA.text(span + 0.8, y, '%.1f kb' % span, ha='left', va='center',
                 fontsize=FS['small'], color=P['grey'])
    axA.set_yticks([])
    axA.set_xticks(range(0, 51, 10))
    axA.spines['bottom'].set_bounds(0, 50)
    axA.spines['bottom'].set_color(P['grey'])
    for s_ in ('top', 'right', 'left'):
        axA.spines[s_].set_visible(False)
    axA.tick_params(axis='x', colors=P['grey'], length=1.8, pad=1.2)
    for t in axA.get_xticklabels():
        t.set_fontsize(FS['small'])
    axA.set_xlabel('Distance from gene 5′ end (kb, GRCh38)', labelpad=1.5,
                   color=P['ink'], fontsize=FS['anno'])
    axA.legend(handles=[Rectangle((0, 0), 1, 1, fc=P['cds'], ec='none',
                                  label='Coding sequence'),
                        Rectangle((0, 0), 1, 1, fc=P['utr'], ec=P['cds'],
                                  lw=0.2, label='Untranslated region')],
               loc='lower right', bbox_to_anchor=(1.0, 1.0), ncol=2,
               borderpad=0.0, handlelength=1.2, fontsize=FS['small'],
               labelcolor=P['grey'])
    panel(fig, axA, 'a', dx=-GUT + 1.0, dy=2.0)

    # --------------------------------- panel b: exons in codon coordinates --
    BH = 62.0
    axB = axes(fig, GUT, 10.0, W2 - GUT - 6, BH)
    keys = ['KRAS4B', 'KRAS4A', 'HRAS', 'NRAS']
    NAME = {'KRAS4B': (GI('KRAS'), 'KRAS4B, 188 aa'),
            'KRAS4A': (GI('KRAS'), 'KRAS4A, 189 aa'),
            'HRAS': (GI('HRAS'), '189 aa'),
            'NRAS': (GI('NRAS'), '189 aa')}
    GAPU = 6.5                                      # fixed intron gap, codons
    nrow = len(keys)
    axB.set_ylim(-1.50, nrow - 1 + 1.35)
    uB = BH / (nrow - 1 + 2.85)                     # mm per data unit
    hc, hu = 2.5 / uB, 1.5 / uB
    axB.axis('off')
    tB = blend(axB.transAxes, axB.transData)

    def clipw(bp):
        return min(bp, CLIP_BP) / 3.0, bp > CLIP_BP

    def geom(key):
        """Blocks in codon units. Coding exons share coordinates across rows."""
        ex = exons(TXS[key])
        cod = [e for e in ex if I(e['coding_len'])]
        r0, rN = I(cod[0]['exon_rank']), I(cod[-1]['exon_rank'])
        cds, utr, labs, cum = [], [], [], 0.0
        for k, e in enumerate(cod):
            w = I(e['coding_len']) / 3.0
            cds.append((cum + GAPU * k, w, I(e['exon_rank']), e))
            cum += w
        u = I(cod[0]['utr_len']) / 3.0              # 5′ stub on first CDS exon
        if u:
            utr.append((cds[0][0] - u, u, False))
        x = cds[0][0] - u
        for e in sorted([e for e in ex if I(e['exon_rank']) < r0],
                        key=lambda e: -I(e['exon_rank'])):
            w, clip = clipw(I(e['exon_len']))
            x -= GAPU + w
            utr.append((x, w, clip))
            labs.append((x + w / 2, 'E%s · %d bp%s' % (e['exon_rank'],
                                                       I(e['exon_len']),
                                                       '*' if clip else '')))
        left = x
        x = cds[-1][0] + cds[-1][1]
        if I(cod[-1]['utr_len']):
            w, clip = clipw(I(cod[-1]['utr_len']))
            utr.append((x, w, clip))
            if w > 6:
                labs.append((x + w / 2, '3′UTR · %d bp%s' %
                             (I(cod[-1]['utr_len']), '*' if clip else '')))
            x += w
        for e in sorted([e for e in ex if I(e['exon_rank']) > rN],
                        key=lambda e: I(e['exon_rank'])):
            w, clip = clipw(I(e['exon_len']))
            x += GAPU
            utr.append((x, w, clip))
            labs.append((x + w / 2, 'E%s · %d bp%s' % (e['exon_rank'],
                                                       I(e['exon_len']),
                                                       '*' if clip else '')))
            x += w
        return cds, utr, labs, left, x

    G = {k: geom(k) for k in keys}
    x0 = min(G[k][3] for k in keys)
    x1 = max(G[k][4] for k in keys)
    axB.set_xlim(x0 - 4, x1 + 4)

    # shared columns behind everything
    ytop, ybot = nrow - 1 + 0.42, -0.34
    shared = [c for c in G['KRAS4B'][0] if c[2] in (2, 3, 4)]
    for xs, w, rank, e in shared:
        axB.add_patch(Rectangle((xs - 1.4, ybot), w + 2.8, ytop - ybot,
                                fc=P['band'], ec='none', zorder=0))

    for i, key in enumerate(keys):
        cds, utr, labs, _, _ = G[key]
        ex = exons(TXS[key])
        g = ex[0]['gene']
        aa_len = 188 if key == 'KRAS4B' else 189
        y = nrow - 1 - i
        # intron baseline, from the first to the last drawn block
        axB.plot([G[key][3], G[key][4]], [y, y], color=P['intron'], lw=0.55,
                 zorder=1, solid_capstyle='butt')
        for xs, w, clip in utr:
            axB.add_patch(Rectangle((xs, y - hu / 2), w, hu, fc=P['utr'],
                                    ec=P['cds'], lw=0.2, zorder=3))
            if clip:
                for off in (1.6, 4.4):
                    for col, lwd, z in (('white', 1.8, 4), (P['cds'], 0.45, 5)):
                        axB.plot([xs + w - off - 1.3, xs + w - off + 1.3],
                                 [y - hu * 0.95, y + hu * 0.95], color=col,
                                 lw=lwd, zorder=z, solid_capstyle='butt')
        for xs, w, rank, e in cds:
            axB.add_patch(Rectangle((xs, y - hc / 2), w, hc, fc=P['cds'],
                                    ec='none', zorder=3))
            if rank == cds[-1][2]:                  # last coding exon: varies
                axB.text(xs + w / 2, y - hc / 2 - 0.16,
                         'E%d · %d bp · aa %s–%d' % (rank, I(e['coding_len']),
                                                     e['codon_first'],
                                                     min(I(e['codon_last']),
                                                         aa_len)),
                         ha='center', va='top', fontsize=FS['small'],
                         color=P['grey'], zorder=6)
        for lx, tx in labs:                 # non-coding exons: label above
            axB.text(lx, y + hu / 2 + 0.11, tx, ha='center', va='bottom',
                     fontsize=FS['small'], color=P['grey'], zorder=6)
        gene, iso = NAME[key]
        axB.text(-0.015, y, '%s  %s' % (gene, iso), transform=tB, ha='right',
                 va='center', fontsize=FS['anno'], color=P['ink'])

    # ---- hotspot codons: one label per codon, ticks only where registered --
    def hx(codon, rank):
        k = [c[2] for c in G['KRAS4B'][0]].index(rank)
        return codon - 0.5 + GAPU * k

    HOTG = [('G12/G13', (12, 13), 2), ('Q61', (61,), 3),
            ('K117', (117,), 4), ('A146', (146,), 4)]
    yl = nrow - 1 + 0.95
    for lab, codons, rank in HOTG:
        rows = [i for i, k in enumerate(keys)
                if any(h for h in HOT if h['gene'] == exons(TXS[k])[0]['gene']
                       and int(h['codon']) in codons)]
        if not rows:
            continue
        px = sum(hx(c, rank) for c in codons) / len(codons)
        ylow = nrow - 1 - max(rows)
        axB.plot([px, px], [ylow, yl - 0.16], color=P['hot'], lw=0.4,
                 alpha=0.30, zorder=2, solid_capstyle='butt')
        for i in rows:
            yy = nrow - 1 - i
            for c in codons:
                axB.plot([hx(c, rank)] * 2, [yy - hc / 2, yy + hc / 2],
                         color=P['hot'], lw=1.0, zorder=5,
                         solid_capstyle='butt')
        axB.text(px, yl, lab, ha='center', va='bottom', fontsize=FS['anno'],
                 color=P['hot'], fontweight='bold')

    # ---- shared column read-out, printed once ----------------------------
    yh = ybot - 0.10
    for xs, w, rank, e in shared:
        axB.text(xs + w / 2, yh, 'E%d' % rank, ha='center', va='top',
                 fontsize=FS['small'], color=P['ink'], fontweight='bold')
        axB.text(xs + w / 2, yh - 0.30, '%d bp\naa %s–%s' %
                 (I(e['coding_len']), e['codon_first'], e['codon_last']),
                 ha='center', va='top', fontsize=FS['small'], color=P['grey'],
                 linespacing=1.3)
    bx0, bx1 = shared[0][0] - 1.4, shared[-1][0] + shared[-1][1] + 1.4
    byy = yh - 1.02
    axB.plot([bx0, bx0, bx1, bx1], [byy + 0.09, byy, byy, byy + 0.09],
             color=P['grey'], lw=0.4, zorder=2)
    axB.text((bx0 + bx1) / 2, byy - 0.08,
             'identical in all three genes — the basis of the exon 2/3/4 '
             'scheme used in clinical testing', ha='center', va='top',
             fontsize=FS['small'], color=P['grey'])
    panel(fig, axB, 'b', dx=-GUT + 1.0, dy=2.6)
    fig.text(6.0 / W2, 5.4 / H, 'MANE v1 matched pairs (Ensembl / NCBI) — '
             'KRAS4B, MANE Select, ENST00000311936.8 / NM_004985.5;   '
             'KRAS4A, MANE Plus Clinical, ENST00000256078.10 / NM_033360.4;',
             ha='left', va='bottom', fontsize=FS['small'], color=P['grey'])
    fig.text(6.0 / W2, 2.2 / H, 'HRAS, MANE Select, ENST00000311189.8 / '
             'NM_005343.4;   NRAS, MANE Select, ENST00000369535.5 / '
             'NM_002524.5.   Asterisks, terminal exons truncated for display.',
             ha='left', va='bottom', fontsize=FS['small'], color=P['grey'])

    save(fig, 'Fig1_RAS_gene_structure')
    CHECK['Fig1 coding exon lengths (KRAS/HRAS/NRAS, E2-E4)'] = [
        [I(e['coding_len']) for e in exons(TXS[k]) if I(e['coding_len'])][:3]
        for k in ('KRAS4B', 'HRAS', 'NRAS')]


# =========================================================== Figure 2 ======
def fig2():
    AA = 188
    H = 104.0
    fig = figure(H)
    ax = axes(fig, 29, 2, W2 - 29 - 3, H - 4)
    ax.set_xlim(-16, AA + 28)
    ax.set_ylim(-3.45, 4.35)
    ax.axis('off')
    ex = [e for e in exons(TXS['KRAS4B']) if I(e['coding_len'])]

    # 1) CDS track
    ytop, hh = 2.95, 0.52
    cols = ['#9FC3DE', '#5B93BD', '#2E6F9E', '#1B4F72']
    for k, e in enumerate(ex):
        a, b = I(e['codon_first']), min(I(e['codon_last']), AA)
        ax.add_patch(Rectangle((a - 1, ytop - hh / 2), b - a + 1, hh,
                               fc=cols[k], ec='#111111', lw=LW['edge']))
        ax.text((a + b) / 2, ytop, 'Exon %s' % e['exon_rank'], ha='center',
                va='center', fontsize=FS['anno'], color='white',
                fontweight='bold')
        ax.text((a + b) / 2, ytop + hh / 2 + 0.13, '%s bp  (aa %d–%d)' %
                (e['coding_len'], a, b), ha='center', va='bottom',
                fontsize=FS['anno'], color='#333333')
        if k < len(ex) - 1:
            ax.plot([b + 0.5, b + 0.5], [ytop - hh / 2, ytop + hh / 2],
                    color='white', lw=0.7)
    ax.text(-14, ytop, 'CDS\n567 bp', ha='right', va='center',
            fontsize=FS['axis'], linespacing=1.35)
    ax.text(AA + 26, ytop + 0.82,
            GI('KRAS') + ', MANE Select ENST00000311936.8 / NM_004985.5',
            ha='right', va='bottom', fontsize=FS['anno'], color='#1B4F72')

    # 2) straight-edged correspondence band
    ybot = 1.05
    for k, e in enumerate(ex):
        a, b = I(e['codon_first']) - 1, min(I(e['codon_last']), AA)
        ax.add_patch(Polygon([[a, ytop - hh / 2], [b, ytop - hh / 2],
                              [b, ybot + 0.40], [a, ybot + 0.40]],
                             closed=True, fc=cols[k], alpha=0.10, ec='none'))

    # 3) secondary structure (to residue 166 only)
    for f in FEAT:
        if f['gene'] != 'KRAS' or f['type'] not in ('Helix', 'Beta strand'):
            continue
        a, b = I(f['start']), I(f['end'])
        if a > 166:
            continue
        b = min(b, 166)
        if f['type'] == 'Helix':
            ax.add_patch(FancyBboxPatch((a - 1, ybot + 0.10), b - a + 1, 0.30,
                                        boxstyle='round,pad=0,rounding_size=0.12',
                                        fc=C['helix'], ec='none'))
        else:
            ax.add_patch(FancyArrow(a - 1, ybot + 0.25, b - a + 1, 0, width=0.13,
                                    head_width=0.26, head_length=min(4, b - a + 1),
                                    length_includes_head=True, fc=C['strand'],
                                    ec='none'))
    ax.text(-14, ybot + 0.25, 'Secondary\nstructure', ha='right', va='center',
            fontsize=FS['axis'], linespacing=1.35)

    # 4) protein track
    yp, ph = 0.02, 0.60
    ax.add_patch(Rectangle((0, yp - ph / 2), 166, ph, fc='#E8EDF1',
                           ec='#111111', lw=0.45))
    ax.add_patch(Rectangle((166, yp - ph / 2), AA - 166, ph, fc=C['hvr'],
                           ec='#111111', lw=0.45, alpha=0.78))
    ax.text(83, yp + ph / 2 + 0.11, 'G domain (aa 1–166)', ha='center',
            va='bottom', fontsize=FS['anno'], color='#333333')
    ax.text(177, yp, 'HVR', ha='center', va='center', fontsize=FS['small'],
            color='white', fontweight='bold')
    MOT = [('G1 / P-loop\n10–17', 10, 17, C['ploop'], 13, -1.30),
           ('switch I\n30–38', 30, 38, C['sw1'], 34, -1.30),
           ('G3 DxxG\n57–60', 57, 60, C['g3'], 46, -2.12),
           ('switch II\n60–76', 60, 76, C['sw2'], 76, -1.30),
           ('G4 NKxD\n116–119', 116, 119, C['g4'], 117, -1.30),
           ('G5 SAK\n145–147', 145, 147, C['g5'], 146, -1.30)]
    for n, a, b, col, lx, ly in MOT:
        ax.add_patch(Rectangle((a - 1, yp - ph / 2), b - a + 1, ph, fc=col,
                               ec='#111111', lw=LW['edge']))
        ax.annotate(n, xy=((a + b) / 2, yp - ph / 2), xytext=(lx, ly),
                    ha='center', va='top', fontsize=FS['anno'], color=col,
                    linespacing=1.35,
                    arrowprops=dict(arrowstyle='-', lw=LW['lead'], color=col))
    ax.text(-14, yp, 'KRAS4B protein\n188 aa (UniProt P01116-2)', ha='right',
            va='center', fontsize=FS['axis'], linespacing=1.35)

    for cd, lb in [(12.5, 'G12 / G13'), (61, 'Q61'), (117, 'K117'),
                   (146, 'A146')]:
        ax.annotate(lb, xy=(cd, yp + ph / 2), xytext=(cd, 0.93), ha='center',
                    fontsize=FS['anno'], color=C['hot'], fontweight='bold',
                    arrowprops=dict(arrowstyle='-|>', lw=0.6, color=C['hot'],
                                    shrinkA=0, shrinkB=0, mutation_scale=6))
    ax.annotate('C185 farnesylation and\ncarboxymethylation (membrane anchor)',
                xy=(185, yp - ph / 2), xytext=(AA + 24, -2.42), ha='right',
                va='top', fontsize=FS['anno'], color='#333333', linespacing=1.4,
                arrowprops=dict(arrowstyle='-|>', lw=LW['lead'], color='#333333',
                                mutation_scale=6))
    ax.annotate('HVR (aa 167–188): K175–K180 polybasic stretch,\n'
                'specific to KRAS4B; KRAS4A is palmitoylated at C180/C181',
                xy=(176, yp + ph / 2), xytext=(AA + 24, 2.05), ha='right',
                va='bottom', fontsize=FS['anno'], color='#333333',
                linespacing=1.4,
                arrowprops=dict(arrowstyle='-|>', lw=LW['lead'], color='#333333',
                                mutation_scale=6))
    for t in range(0, AA + 1, 20):
        ax.plot([t, t], [yp - ph / 2 - 0.06, yp - ph / 2 - 0.15],
                color=C['grey'], lw=LW['axis'])
        ax.text(t, yp - ph / 2 - 0.19, str(t), ha='center', va='top',
                fontsize=FS['small'], color=C['grey'])
    ax.text(AA / 2, -3.3, 'Residue number (KRAS4B, 188 aa)', ha='center',
            fontsize=FS['axis'], color='#333333')
    h = [Rectangle((0, 0), 1, 1, fc=C['helix'], label='α-helix'),
         Rectangle((0, 0), 1, 1, fc=C['strand'], label='β-strand'),
         Rectangle((0, 0), 1, 1, fc='#E8EDF1', ec='#111111', lw=LW['edge'],
                   label='G domain'),
         Rectangle((0, 0), 1, 1, fc=C['hvr'], label='Hypervariable region')]
    ax.legend(handles=h, loc='upper left', bbox_to_anchor=(0.005, 1.0), ncol=4)
    save(fig, 'Fig2_gene_to_protein_map')


# =========================================================== Figure 3 ======
def fig3():
    AA = 189
    PH, GAPY, BOT, TOP = 40.0, 7.0, 13.0, 9.0
    H = BOT + 3 * PH + 2 * GAPY + TOP
    fig = figure(H)
    genes = ('KRAS', 'NRAS', 'HRAS')
    axs = []
    for i in range(3):
        y = H - TOP - (i + 1) * PH - i * GAPY
        axs.append(axes(fig, 15, y, W2 - 15 - 6, PH))
    for pi, (ax, g) in enumerate(zip(axs, genes)):
        rs = [r for r in MUT if r['gene'] == g]
        tot = sum(int(r['n']) for r in rs)
        pos = collections.defaultdict(list)
        for r in rs:
            if r['codon']:
                pos[int(r['codon'])].append((r['protein_change'], int(r['n'])))
        ymax = max(sum(n for _, n in v) for v in pos.values())
        labs = []
        for p, v in sorted(pos.items()):
            tt = sum(n for _, n in v)
            ax.plot([p, p], [0, tt], color='#999999', lw=0.5, zorder=2,
                    solid_capstyle='butt')
            hotspot = p in (12, 13, 61, 117, 146)
            d_mm = 1.2 + 2.0 * (tt / ymax) ** 0.5
            ax.scatter([p], [tt], s=dot_area(d_mm) * (1.35 if hotspot else 1.0),
                       marker='D' if hotspot else 'o',
                       fc=C['hot'] if hotspot else '#9FC3DE',
                       ec='#111111' if hotspot else '#2E6F9E',
                       lw=0.45 if hotspot else LW['edge'], zorder=3)
            if tt >= ymax * 0.08:
                labs.append((p, tt, '/'.join(x for x, _ in
                                             sorted(v, key=lambda a: -a[1])[:3])))
        clusters = []
        for it in labs:
            if clusters and it[0] - clusters[-1][-1][0] <= 14:
                clusters[-1].append(it)
            else:
                clusters.append([it])
        for cl in clusters:
            top = max(t for _, t, _ in cl)
            if len(cl) == 1 and cl[0][1] >= ymax * 0.5:
                p0, tt0, lb0 = cl[0]
                ax.annotate('%s\n%s (%.0f%%)' % (lb0, fmt(tt0),
                                                 100.0 * tt0 / tot),
                            xy=(p0, tt0), xytext=(0, 5),
                            textcoords='offset points', ha='center',
                            va='bottom', fontsize=FS['anno'], linespacing=1.3)
                continue
            tx = cl[-1][0] + 8
            ty = top * 1.04 + ymax * 0.07
            txt = '\n'.join('%s  %s (%.0f%%)' % (lb, fmt(tt), 100.0 * tt / tot)
                            for _, tt, lb in cl)
            ax.text(tx, ty, txt, ha='left', va='bottom', fontsize=FS['anno'],
                    linespacing=1.35)
            for p0, tt0, _ in cl:
                ax.plot([p0, tx - 1.5], [tt0, ty], color='#aaaaaa',
                        lw=LW['lead'], zorder=1)
        ax.add_patch(Rectangle((1, -ymax * 0.125), AA, ymax * 0.048,
                               fc='#DCE3E8', ec='#333333', lw=LW['edge'],
                               zorder=1, clip_on=False))
        for nm, a, b, cc in REG:
            ax.add_patch(Rectangle((a, -ymax * 0.145), b - a + 1, ymax * 0.088,
                                   fc=cc, ec='none', clip_on=False, zorder=4))
        ax.set_ylim(-ymax * 0.17, ymax * 1.44)
        ax.set_xlim(0, AA + 2)
        ax.set_ylabel('Mutated samples (n)')
        ax.text(0.995, 0.95, '%s, %s mutations in %s samples' %
                (GI(g, bold=True), fmt(tot), fmt(NTOT)),
                transform=ax.transAxes, ha='right',
                va='top', fontsize=FS['axis'], fontweight='bold')
        for s_ in ('top', 'right'):
            ax.spines[s_].set_visible(False)
        if pi < 2:
            ax.set_xticklabels([])
        panel(fig, ax, 'abc'[pi])
        CHECK['Fig3 %s hotspot counts' % g] = {
            c: sum(n for _, n in pos.get(c, [])) for c in (12, 13, 61)}
    axs[-1].set_xlabel('Residue number')
    hmark = [plt.Line2D([], [], ls='', marker='D', mfc=C['hot'], mec='#111111',
                        mew=0.45, ms=3.4, label='Hotspot codon'),
             plt.Line2D([], [], ls='', marker='o', mfc='#9FC3DE', mec='#2E6F9E',
                        mew=0.3, ms=3.4, label='Other codon')]
    axs[0].legend(handles=hmark + [Rectangle((0, 0), 1, 1, fc=cc, label=nm)
                                   for nm, _, _, cc in REG],
                  loc='lower left', bbox_to_anchor=(0.0, 1.02), ncol=8,
                  borderpad=0.1, handletextpad=0.4)
    save(fig, 'Fig3_mutation_distribution')


# =========================================================== Figure 4 ======
def fig4():
    KEYS = ['G12D', 'G12V', 'G12C', 'G12R', 'G13D', 'Q61X', 'Other']
    PAL = ['#1B4F72', '#2E86AB', '#48A9A6', '#E09F3E', '#BF3100', '#6A4C93',
           '#B6BEC6']
    muts = json.load(open(os.path.join(DATA, 'cbioportal_mutations.json')))
    ct = json.load(open(os.path.join(DATA, 'cbioportal_sample_cancertype.json')))
    comp = collections.defaultdict(collections.Counter)
    for m in muts['KRAS']:
        if m['sample'] in ct and m['protein']:
            k = m['protein'] if m['protein'] in KEYS[:5] else (
                'Q61X' if str(m['start']) == '61' else 'Other')
            comp[ct[m['sample']]][k] += 1

    NA, PITCH_A, BAR_A = 16, 4.6, 3.2
    NB, PITCH_B, BAR_B = 10, 3.0, 2.1
    HA, HB = NA * PITCH_A, NB * PITCH_B
    BOT, TOP, GAPB = 12.0, 7.0, 11.0
    H = max(BOT + HA + TOP, BOT + 2 * HB + GAPB + 11 + TOP)
    fig = figure(H)

    axA = axes(fig, 44, BOT, 72, HA)
    ks = sorted([r for r in BYCT if r['gene'] == 'KRAS'],
                key=lambda r: -float(r['freq_pct']))[:NA][::-1]
    bar_u = BAR_A / PITCH_A
    for i, r in enumerate(ks):
        f = float(r['freq_pct'])
        cc = comp[r['cancer_type']]
        tot = sum(cc.values()) or 1
        left = 0.0
        for k, col in zip(KEYS, PAL):
            w = f * cc[k] / tot
            if w > 0:
                axA.barh(i, w, left=left, color=col, height=bar_u, ec='white',
                         lw=0.3)
            left += w
        axA.text(f + 1.5, i, '%.0f%%  (%s/%s)' % (f, r['n_mut_samples'],
                                                  r['n_samples']),
                 va='center', fontsize=FS['anno'], color='#333333')
    axA.set_yticks(range(NA))
    axA.set_yticklabels([r['cancer_type'] for r in ks], fontsize=FS['tick'])
    axA.set_ylim(-0.5, NA - 0.5)
    axA.set_xlim(0, 100)
    axA.set_xticks(range(0, 101, 20))
    axA.set_xlabel(GI('KRAS') + '-mutant samples (%)')
    axA.tick_params(axis='y', length=0)
    for s_ in ('top', 'right', 'left'):
        axA.spines[s_].set_visible(False)
    axA.legend(handles=[Rectangle((0, 0), 1, 1, fc=c, label=k)
                        for k, c in zip(KEYS, PAL)], loc='lower left',
               ncol=2, title='Allele', title_fontsize=FS['anno'],
               borderpad=0.1, bbox_to_anchor=(0.58, 0.015))
    panel(fig, axA, 'a', dx=-40)

    for idx, (g, col, pn) in enumerate((('NRAS', C['n'], 'b'),
                                        ('HRAS', C['h'], 'c'))):
        ytop = H - TOP if idx == 0 else H - TOP - HB - GAPB
        a_ = axes(fig, 148, ytop - HB, 28, HB)
        rs = sorted([r for r in BYCT if r['gene'] == g],
                    key=lambda r: -float(r['freq_pct']))[:NB][::-1]
        a_.barh(range(NB), [float(r['freq_pct']) for r in rs], color=col,
                height=BAR_B / PITCH_B, ec='#333333', lw=LW['edge'])
        for i, r in enumerate(rs):
            a_.text(float(r['freq_pct']) + max(float(x['freq_pct'])
                                               for x in rs) * 0.04, i,
                    '%.0f%% (%s/%s)' % (float(r['freq_pct']),
                                        r['n_mut_samples'], r['n_samples']),
                    va='center', fontsize=FS['small'], color='#333333')
        a_.set_yticks(range(NB))
        a_.set_yticklabels([r['cancer_type'] for r in rs], fontsize=FS['small'])
        a_.set_ylim(-0.5, NB - 0.5)
        a_.set_xlim(0, max(float(r['freq_pct']) for r in rs) * 1.6)
        a_.set_xlabel(GI(g) + '-mutant samples (%)')
        a_.tick_params(axis='y', length=0)
        for s_ in ('top', 'right', 'left'):
            a_.spines[s_].set_visible(False)
        panel(fig, a_, pn, dx=-31)
    save(fig, 'Fig4_cancer_type_distribution')
    CHECK['Fig4 KRAS top3'] = [(r['cancer_type'], r['freq_pct'],
                                '%s/%s' % (r['n_mut_samples'], r['n_samples']))
                               for r in ks[::-1][:3]]


# =========================================================== Figure 5 ======
def fig5():
    PDBS = ('3CON', '4LDJ', '4OBE', '4Q21', '5P21', '5VQ2', '6GJ8', '6OIM',
            '7RPZ')
    cov = sorted([c for c in COV if c['pdb'] in PDBS],
                 key=lambda c: c['pdb'], reverse=True)
    HA, PITCH_B, BAR_B = 55.0, 3.6, 2.2
    HB = len(cov) * PITCH_B
    BOT, GAPY, TOP = 12.0, 5.0, 6.0
    H = BOT + HB + GAPY + HA + TOP
    fig = figure(H)
    L, WIDTH = 40.0, W2 - 40 - 6

    ax = axes(fig, L, H - TOP - HA, WIDTH, HA)
    for g, col in (('KRAS', C['k']), ('NRAS', C['n']), ('HRAS', C['h'])):
        y = PLD[g]
        ax.plot(range(1, len(y) + 1), y, color=col, lw=LW['data'],
                label='%s (%s)' % (g, GCORE[g]['alphafold']['entryId']))
    for lo, hi, cc, al in ((90, 100, '#0053D6', 0.07), (70, 90, '#65CBF3', 0.07),
                           (50, 70, '#FFDB13', 0.10), (0, 50, '#FF7D45', 0.10)):
        ax.axhspan(lo, hi, color=cc, alpha=al, zorder=0, lw=0)
    ax.axvspan(167, 189, color=C['hvr'], alpha=0.16, zorder=0, lw=0)
    ax.text(178, 18, 'Hypervariable region\n(flexible; absent from\n'
            'all crystal structures)', ha='center', fontsize=FS['anno'],
            color='#333333', linespacing=1.35)
    ax.set_ylim(0, 102)
    ax.set_xlim(0, 191)
    ax.set_ylabel('pLDDT')
    ax.set_xticklabels([])
    ax.legend(loc='lower left', bbox_to_anchor=(0.005, 0.02), borderpad=0.1)
    ax.text(0.995, 0.055, '≥90 very high  |  70–90 confident  |  50–70 low  |'
            '  <50 very low', transform=ax.transAxes, ha='right',
            fontsize=FS['small'], color='#444444')
    for s_ in ('top', 'right'):
        ax.spines[s_].set_visible(False)
    panel(fig, ax, 'a', dx=-36)

    ax2 = axes(fig, L, BOT, WIDTH, HB)
    ylab = []
    for i, c in enumerate(cov):
        a, b = int(c['first_obs']), int(c['last_obs'])
        bh = BAR_B / PITCH_B
        ax2.add_patch(Rectangle((a, i - bh / 2), b - a + 1, bh, fc='#2E6F9E',
                                ec='#111111', lw=LW['edge']))
        for gp in [x for x in c['gap_after'].split(';') if x]:
            ax2.add_patch(Rectangle((int(gp) + 0.5, i - bh / 2), 1.2, bh,
                                    fc='white', ec='none'))
        ylab.append('%s  %.2f Å  [%s]' % (c['pdb'],
                                          PDBM[c['pdb']]['resolution'] or 0,
                                          ','.join(PDBM[c['pdb']]['ligands'] or [])))
    ax2.axvspan(167, 189, color=C['hvr'], alpha=0.16, zorder=0, lw=0)
    ax2.set_yticks(range(len(cov)))
    ax2.set_yticklabels(ylab, fontsize=FS['small'])
    ax2.tick_params(axis='y', length=0)
    ax2.set_xlim(0, 191)
    ax2.set_ylim(-0.6, len(cov) - 0.4)
    ax2.set_xlabel('Residue number')
    for s_ in ('top', 'right', 'left'):
        ax2.spines[s_].set_visible(False)
    panel(fig, ax2, 'b', dx=-36)
    save(fig, 'Fig5_AlphaFold_confidence_and_coverage')
    CHECK['Fig5 last observed residue'] = {c['pdb']: int(c['last_obs'])
                                           for c in cov}


# =========================================================== Figure 6 ======
def ca(pdb, chain=None, want_het=None):
    xyz, het = {}, []
    for l in open(os.path.join(STRU, '%s.pdb' % pdb)):
        if l.startswith('ATOM') and l[12:16].strip() == 'CA':
            if chain and l[21] != chain:
                continue
            if l[16] not in (' ', 'A'):
                continue
            xyz[int(l[22:26])] = (float(l[30:38]), float(l[38:46]),
                                  float(l[46:54]))
        elif l.startswith('HETATM') and want_het and l[17:20].strip() in want_het:
            if chain and l[21] != chain:
                continue
            het.append((l[17:20].strip(), float(l[30:38]), float(l[38:46]),
                        float(l[46:54])))
    return xyz, het


def kabsch(P, Q):
    cp, cq = P.mean(0), Q.mean(0)
    U, S, Vt = np.linalg.svd((P - cp).T @ (Q - cq))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    return Vt.T @ np.diag([1, 1, d]) @ U.T, cp, cq


def devcurve(p1, c1, p2, c2, excl=((25, 45), (55, 76))):
    a, _ = ca(p1, c1)
    b, _ = ca(p2, c2)
    com = [r for r in sorted(set(a) & set(b)) if r <= 169]
    core = [r for r in com if not any(lo <= r <= hi for lo, hi in excl)]
    P, Q = np.array([a[r] for r in core]), np.array([b[r] for r in core])
    R, cp, cq = kabsch(P, Q)
    A, B = np.array([a[r] for r in com]), np.array([b[r] for r in com])
    d = np.linalg.norm((R @ (A - cp).T).T + cq - B, axis=1)
    rms = float(np.sqrt((np.linalg.norm((R @ (P - cp).T).T + cq - Q,
                                        axis=1) ** 2).mean()))
    return com, d, rms


def fig6():
    PH, GAPY, BOT, TOP = 44.0, 9.0, 13.0, 7.0
    H = BOT + 2 * PH + GAPY + TOP
    fig = figure(H)
    pairs = [(('4OBE', 'B'), ('5VQ2', 'A'),
              'KRAS–GDP (4OBE) vs KRAS–GTP (5VQ2)', C['h']),
             (('4LDJ', 'A'), ('6OIM', 'A'),
              'KRAS(G12C)–GDP (4LDJ) vs KRAS(G12C)–sotorasib (6OIM)', C['sw2'])]
    for i, (p1, p2, ttl, col) in enumerate(pairs):
        y = H - TOP - (i + 1) * PH - i * GAPY
        ax = axes(fig, 15, y, 85, PH)
        com, d, rms = devcurve(p1[0], p1[1], p2[0], p2[1])
        ax.fill_between(com, 0, d, color=col, alpha=0.30, lw=0)
        ax.plot(com, d, color=col, lw=LW['data'])
        for nm, lo, hi, cc in REG[:3]:
            ax.axvspan(lo, hi, color=cc, alpha=0.18, zorder=0, lw=0)
            ax.text((lo + hi) / 2, max(d) * 1.07, nm, ha='center',
                    fontsize=FS['small'], color=cc)
        ax.set_xlim(1, 170)
        ax.set_ylim(0, max(d) * 1.26)
        ax.set_ylabel('Cα deviation (Å)')
        ax.text(0.995, 1.02, ttl, transform=ax.transAxes, ha='right',
                va='bottom', fontsize=FS['anno'], color='#222222')
        ax.text(0.99, 0.90, 'Core-region RMSD = %.2f Å' % rms,
                transform=ax.transAxes, ha='right', va='top',
                fontsize=FS['anno'], color='#333333')
        if i == 1:
            ax.set_xlabel('Residue number')
        for s_ in ('top', 'right'):
            ax.spines[s_].set_visible(False)
        panel(fig, ax, 'ab'[i])
        CHECK['Fig6 %s' % ttl.split(' vs ')[0]] = {
            'core RMSD': round(rms, 2),
            'switch I peak': round(max(d[j] for j, r in enumerate(com)
                                       if 30 <= r <= 38), 1),
            'switch II peak': round(max(d[j] for j, r in enumerate(com)
                                        if 60 <= r <= 76), 1)}

    # ---- panel c: molecular rendering -----------------------------------
    SEGS = [('P-loop', C['ploop']), ('switch I', C['sw1']),
            ('switch II', C['sw2']), ('G4', C['g4']), ('G5', C['g5'])]
    hl = [plt.Line2D([], [], color=c, lw=2.6, label=n) for n, c in SEGS]
    hl += [plt.Line2D([], [], marker='o', ls='', color='#355070', ms=3,
                      label='GDP'),
           plt.Line2D([], [], marker='o', ls='', color=C['sw2'], ms=3,
                      label='Sotorasib (AMG 510)'),
           plt.Line2D([], [], marker='o', ls='', color=C['ploop'], ms=4,
                      label='Mg2+'),
           plt.Line2D([], [], marker='o', ls='', color=C['hot'], ms=4.5,
                      mec='k', mew=0.3, label='Cys12 (covalent site)')]
    render = os.path.join(FIG, '_panelC_6OIM.png')

    if os.path.exists(render):                     # PyMOL ray-traced render
        imax = axes(fig, 102, 24, 76, H - 24 - 8)
        img = plt.imread(render)
        if img.ndim == 3 and img.shape[2] == 4:      # crop transparent margins
            a = img[:, :, 3] > 0.02
            rs, cs = np.where(a.any(1))[0], np.where(a.any(0))[0]
            pad = int(0.015 * max(img.shape[:2]))
            img = img[max(rs[0] - pad, 0):rs[-1] + pad,
                      max(cs[0] - pad, 0):cs[-1] + pad]
        imax.imshow(img, interpolation='antialiased')
        imax.set_axis_off()
        lgax = axes(fig, 104, 6, 72, 18)
        lgax.set_axis_off()
        lgax.legend(handles=hl, loc='center', ncol=2, fontsize=FS['small'],
                    handlelength=1.3, columnspacing=0.8, borderpad=0.1)
        panel(fig, imax, 'c', dx=-2, dy=-2)
    else:                                          # fallback: Ca trace sketch
        ax3 = fig.add_axes([108 / W2, 24 / H, 68 / W2, (H - 32) / H],
                           projection='3d')
        xyz, het = ca('6OIM', 'A', want_het={'GDP', 'MOV', 'MG'})
        ks = sorted(xyz)
        P = np.array([xyz[r] for r in ks])
        ctr = P.mean(0)
        U, S, Vt = np.linalg.svd(P - ctr)
        P = (P - ctr) @ Vt.T
        hetp = {}
        for grp in ('GDP', 'MOV', 'MG'):
            q = np.array([[h[1], h[2], h[3]] for h in het if h[0] == grp])
            hetp[grp] = (q - ctr) @ Vt.T if len(q) else q

        def smooth(pts, n=6):
            out = []
            for i in range(len(pts) - 1):
                p0, p1 = pts[max(i - 1, 0)], pts[i]
                p2, p3 = pts[i + 1], pts[min(i + 2, len(pts) - 1)]
                for t in np.linspace(0, 1, n, endpoint=False):
                    t2, t3 = t * t, t * t * t
                    out.append(0.5 * ((2 * p1) + (-p0 + p2) * t +
                                      (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                                      (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            out.append(pts[-1])
            return np.array(out)

        segs = [(1, 9, '#C3CCD5', None), (10, 17, C['ploop'], 'P-loop'),
                (18, 29, '#C3CCD5', None), (30, 38, C['sw1'], 'switch I'),
                (39, 59, '#C3CCD5', None), (60, 76, C['sw2'], 'switch II'),
                (77, 115, '#C3CCD5', None), (116, 119, C['g4'], 'G4'),
                (120, 144, '#C3CCD5', None), (145, 147, C['g5'], 'G5'),
                (148, 170, '#C3CCD5', None)]
        idx = {r: i for i, r in enumerate(ks)}
        for lo, hi, col, nm in segs:
            sel = [idx[r] for r in ks if lo - 1 <= r <= hi + 1]
            if len(sel) > 1:
                sp = smooth(P[sel])
                ax3.plot(sp[:, 0], sp[:, 1], sp[:, 2], color=col,
                         lw=2.6 if nm else 1.4, solid_capstyle='round',
                         zorder=3 if nm else 2)
        for grp, col, dmm in (('GDP', '#355070', 0.9), ('MOV', C['sw2'], 1.0),
                              ('MG', C['ploop'], 1.5)):
            q = hetp[grp]
            if len(q):
                ax3.scatter(q[:, 0], q[:, 1], q[:, 2], s=dot_area(dmm),
                            color=col, ec='none', depthshade=False, zorder=5)
        c12 = P[idx[12]]
        ax3.scatter([c12[0]], [c12[1]], [c12[2]], s=dot_area(1.6),
                    color=C['hot'], ec='k', lw=0.3, depthshade=False, zorder=6)
        ax3.legend(handles=hl, loc='upper center', bbox_to_anchor=(0.5, 0.16),
                   ncol=2, fontsize=FS['small'], handlelength=1.3,
                   columnspacing=0.8, borderpad=0.1)
        ax3.set_axis_off()
        ax3.view_init(elev=16, azim=-72)
        try:
            ax3.set_box_aspect((1, 1, 0.9), zoom=1.5)
        except Exception:
            pass
        rad = np.abs(P).max() * 0.92
        ax3.set_xlim(-rad, rad)
        ax3.set_ylim(-rad, rad)
        ax3.set_zlim(-rad * 0.9, rad * 0.9)
        panel(fig, ax3, 'c', dx=-2, dy=-6)
    save(fig, 'Fig6_conformational_switch')


for f in (fig1, fig2, fig3, fig4, fig5, fig6):
    print('==', f.__name__)
    f()

print('\n--- self-check -------------------------------------------------')
for k, v in CHECK.items():
    print('%-46s %s' % (k, v))
print('figures ->', FIG)
