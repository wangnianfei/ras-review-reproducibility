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
# Manuscript Figure 2. Rebuilt 2026-11-02 (author: colour blocks too heavy,
# text and marks too small, use the full Word column width; new palette, no
# colour-blind constraint; the transcript-ID footer moves into the legend).
#   · one text size (T = 7.5 pt, ~6 pt once placed at 14.66 cm) and one
#     panel-letter size, as in Figure 1 of the manuscript;
#   · the label gutter is measured, so both panels share one left edge and
#     the tracks use the remaining width;
#   · panel b is drawn in codon coordinates: coding exons 2-4 fall into
#     shared columns across the four transcripts, read out once underneath;
#   · palette: deep teal value ramp (CDS -> UTR) + one coral accent reserved
#     for hotspot codons; columns are a faint tint, not a block of colour.
P1 = {'cds': '#1F6F78', 'utr': '#CFE5E2', 'edge': '#7FB3AE',
      'intron': '#9AA7A9', 'band': '#F2F7F6', 'hot': '#E0533D',
      'ink': '#1A1A1A', 'grey': '#59656B'}
CLIP_BP = 330.0          # exons longer than this are drawn truncated (*)


def fig1():
    P, T, PN = P1, 7.5, 9
    LEFT, RIGHT, TOP = 4.0, 3.0, 3.0
    fig = figure(10.0)
    rend = fig.canvas.get_renderer()

    def tw(s, bold=False):
        o = fig.text(0, 0, s, fontsize=T, fontweight='bold' if bold else None)
        w = o.get_window_extent(rend).width / fig.dpi / MM
        o.remove()
        return w

    keysA = ['KRAS4B', 'HRAS', 'NRAS']
    keysB = ['KRAS4B', 'KRAS4A', 'HRAS', 'NRAS']
    NAME = {'KRAS4B': (GI('KRAS'), 'KRAS4B, 188 aa'),
            'KRAS4A': (GI('KRAS'), 'KRAS4A, 189 aa'),
            'HRAS': (GI('HRAS'), '189 aa'), 'NRAS': (GI('NRAS'), '189 aa')}
    labA = {k: '%s  %s' % (GI(exons(TXS[k])[0]['gene']), CYTO[k])
            for k in keysA}
    labB = {k: '%s  %s' % NAME[k] for k in keysB}
    GUT = LEFT + max(tw(s) for s in list(labA.values()) +
                     list(labB.values())) + 2.5
    PW = W2 - GUT - RIGHT

    # vertical budget (mm, from the top)
    TXT = 2.7                                   # cap-to-descender, 7.5 pt
    A_LEG, A_PITCH, A_AX = 6.5, 7.0, 10.0
    B_HOT, B_PITCH, B_READ = 8.0, 13.5, 12.5
    GAP = 4.0
    HA = 3 * A_PITCH
    HB = 4 * B_PITCH
    H = TOP + A_LEG + HA + A_AX + GAP + B_HOT + HB + B_READ + 1.0
    fig.set_size_inches(W2 * MM, H * MM)
    fig._mm = (W2, H)

    # ------------------------------------------- panel a: genomic extent --
    yA1 = H - TOP - A_LEG                       # top of track area
    axA = axes(fig, GUT, yA1 - HA, PW, HA)
    axA.set_ylim(0, HA)
    axA.set_xlim(-0.4, 51.0)
    hc, hu = 3.4, 2.0
    for i, key in enumerate(keysA):
        ex = exons(TXS[key])
        hi = max(I(e['exon_end']) for e in ex)
        lo = min(I(e['exon_start']) for e in ex)
        span = (hi - lo) / 1000.0
        y = HA - A_PITCH * (i + 0.5)

        def X(p, _hi=hi):
            return (_hi - p) / 1000.0
        axA.plot([0, span], [y, y], color=P['intron'], lw=0.8, zorder=1,
                 solid_capstyle='butt')
        for e in ex:
            if I(e['utr_len']):
                a0, b0 = X(I(e['exon_end'])), X(I(e['exon_start']))
                axA.add_patch(Rectangle((a0, y - hu / 2), max(b0 - a0, 0.12),
                                        hu, fc=P['utr'], ec=P['edge'],
                                        lw=0.35, zorder=2))
            if I(e['coding_len']):
                a0, b0 = X(I(e['coding_end'])), X(I(e['coding_start']))
                axA.add_patch(Rectangle((a0, y - hc / 2), max(b0 - a0, 0.16),
                                        hc, fc=P['cds'], ec='none', zorder=3))
        fig.text((GUT - 2.5) / W2, (yA1 - HA + y) / H, labA[key], ha='right',
                 va='center', fontsize=T, color=P['ink'])
        axA.text(span + 0.7, y, '%.1f kb' % span, ha='left', va='center',
                 fontsize=T, color=P['grey'])
    axA.set_yticks([])
    axA.set_xticks(range(0, 51, 10))
    axA.spines['bottom'].set_bounds(0, 50)
    axA.spines['bottom'].set_color(P['grey'])
    for s_ in ('top', 'right', 'left'):
        axA.spines[s_].set_visible(False)
    axA.tick_params(axis='x', colors=P['grey'], labelcolor=P['ink'],
                    length=2.0, pad=1.5, labelsize=T)
    axA.set_xlabel('Distance from gene 5′ end (kb, GRCh38)', labelpad=2,
                   color=P['ink'], fontsize=T)
    yleg = H - TOP - 1.6                        # legend / letter centre line
    leg = fig.legend(
        handles=[Rectangle((0, 0), 1, 1, fc=P['cds'], ec='none',
                           label='Coding sequence'),
                 Rectangle((0, 0), 1, 1, fc=P['utr'], ec=P['edge'], lw=0.35,
                           label='Untranslated region'),
                 plt.Line2D([], [], color=P['intron'], lw=0.8, label='Intron'),
                 plt.Line2D([], [], color=P['hot'], lw=1.6,
                        label='Hotspot codon')],
        loc='center right', bbox_to_anchor=((W2 - RIGHT) / W2, yleg / H),
        ncol=4, fontsize=T, handlelength=1.6, handleheight=0.9,
        columnspacing=1.6, borderpad=0, borderaxespad=0, labelcolor=P['ink'])
    fig.text(LEFT / W2, (H - TOP) / H, 'a', fontsize=PN, fontweight='bold',
             ha='left', va='top')

    # --------------------------------- panel b: exons in codon coordinates --
    yB1 = yA1 - HA - A_AX - GAP                 # top of panel b
    fig.text(LEFT / W2, yB1 / H, 'b', fontsize=PN, fontweight='bold',
             ha='left', va='top')
    yB0 = yB1 - B_HOT - HB                      # bottom of the track area
    axB = axes(fig, GUT, yB0, PW, HB)
    axB.set_ylim(0, HB)
    axB.axis('off')
    GAPU = 6.5                                  # fixed intron gap, codons
    hc, hu = 4.2, 2.4

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
            labs.append((x + w / 2, 'E%s · %d bp%s' % (
                e['exon_rank'], I(e['exon_len']), '*' if clip else '')))
        left = x
        x = cds[-1][0] + cds[-1][1]
        if I(cod[-1]['utr_len']):
            w, clip = clipw(I(cod[-1]['utr_len']))
            utr.append((x, w, clip))
            if w > 6:
                labs.append((x + w / 2, '3′UTR · %d bp%s' % (
                    I(cod[-1]['utr_len']), '*' if clip else '')))
            x += w
        for e in sorted([e for e in ex if I(e['exon_rank']) > rN],
                        key=lambda e: I(e['exon_rank'])):
            w, clip = clipw(I(e['exon_len']))
            x += GAPU
            utr.append((x, w, clip))
            labs.append((x + w / 2, 'E%s · %d bp%s' % (
                e['exon_rank'], I(e['exon_len']), '*' if clip else '')))
            x += w
        return cds, utr, labs, left, x

    G = {k: geom(k) for k in keysB}
    x0 = min(G[k][3] for k in keysB)
    x1 = max(G[k][4] for k in keysB)
    axB.set_xlim(x0 - 1, x1 + 1)
    mmx = (x1 - x0 + 2) / PW                    # codons per mm

    shared = [c for c in G['KRAS4B'][0] if c[2] in (2, 3, 4)]
    rowy = [HB - B_PITCH * (i + 0.5) for i in range(len(keysB))]
    ytop, ybot = rowy[0] + hc / 2 + 1.2, rowy[-1] - hc / 2 - 1.2
    for xs, w, rank, e in shared:
        axB.add_patch(Rectangle((xs - 1.2, ybot), w + 2.4, ytop - ybot,
                                fc=P['band'], ec='none', zorder=0))

    for key, y in zip(keysB, rowy):
        cds, utr, labs, lft, rgt = G[key]
        aa_len = 188 if key == 'KRAS4B' else 189
        axB.plot([lft, rgt], [y, y], color=P['intron'], lw=0.8, zorder=1,
                 solid_capstyle='butt')
        for xs, w, clip in utr:
            axB.add_patch(Rectangle((xs, y - hu / 2), w, hu, fc=P['utr'],
                                    ec=P['edge'], lw=0.35, zorder=3))
            if clip:                             # double-slash break mark
                for off in (1.8, 4.6):
                    for col, lwd, z in (('white', 2.2, 4), (P['cds'], 0.6, 5)):
                        axB.plot([xs + w - off - 1.4, xs + w - off + 1.4],
                                 [y - hu * 0.9, y + hu * 0.9], color=col,
                                 lw=lwd, zorder=z, solid_capstyle='butt')
        for xs, w, rank, e in cds:
            axB.add_patch(Rectangle((xs, y - hc / 2), w, hc, fc=P['cds'],
                                    ec='none', zorder=3))
            if rank == cds[-1][2]:              # last coding exon: varies
                axB.text(xs, y - hc / 2 - 0.7,      # left-aligned: clear of E4
                         'E%d · %d bp · aa %s–%d' % (
                             rank, I(e['coding_len']), e['codon_first'],
                             min(I(e['codon_last']), aa_len)),
                         ha='left', va='top', fontsize=T, color=P['grey'],
                         zorder=6)
        for lx, tx in labs:                     # non-coding exons: above
            axB.text(lx, y + hu / 2 + 0.7, tx, ha='center', va='bottom',
                     fontsize=T, color=P['grey'], zorder=6)
        fig.text((GUT - 2.5) / W2, (yB0 + y) / H, labB[key], ha='right',
                 va='center', fontsize=T, color=P['ink'])

    # ---- hotspot codons: one label per codon, ticks only where registered --
    def hx(codon, rank):
        k = [c[2] for c in G['KRAS4B'][0]].index(rank)
        return codon - 0.5 + GAPU * k

    HOTG = [('G12/G13', (12, 13), 2), ('Q61', (61,), 3),
            ('K117', (117,), 4), ('A146', (146,), 4)]
    yl = HB + B_HOT - 2.2
    for lab, codons, rank in HOTG:
        rws = [i for i, k in enumerate(keysB)
               if any(h for h in HOT if h['gene'] == exons(TXS[k])[0]['gene']
                      and int(h['codon']) in codons)]
        if not rws:
            continue
        px = sum(hx(c, rank) for c in codons) / len(codons)
        axB.plot([px, px], [rowy[max(rws)], yl - 0.8], color=P['hot'],
                 lw=0.5, alpha=0.45, zorder=2, solid_capstyle='butt',
                 clip_on=False)
        for i in rws:
            for c in codons:
                axB.plot([hx(c, rank)] * 2, [rowy[i] - hc / 2,
                                             rowy[i] + hc / 2],
                         color=P['hot'], lw=1.6, zorder=5,
                         solid_capstyle='butt')
        axB.text(px, yl, lab, ha='center', va='bottom', fontsize=T,
                 color=P['hot'], fontweight='bold', clip_on=False)

    # ---- shared column read-out, printed once ----------------------------
    yh = ybot - 1.0
    for xs, w, rank, e in shared:
        axB.text(xs + w / 2, yh, 'E%d' % rank, ha='center', va='top',
                 fontsize=T, color=P['ink'], fontweight='bold', clip_on=False)
        axB.text(xs + w / 2, yh - 3.3, '%d bp\naa %s–%s' % (
            I(e['coding_len']), e['codon_first'], e['codon_last']),
            ha='center', va='top', fontsize=T, color=P['grey'],
            linespacing=1.25, clip_on=False)
    # read-out labels must not collide with each other
    cen = [(xs + w / 2, max(tw('%d bp' % I(e['coding_len'])),
                            tw('aa %s–%s' % (e['codon_first'],
                                             e['codon_last']))) * mmx)
           for xs, w, rank, e in shared]
    for (ca_, wa), (cb, wb) in zip(cen, cen[1:]):
        assert ca_ + wa / 2 < cb - wb / 2, 'Fig1 exon read-out labels overlap'

    save(fig, 'Fig1_RAS_gene_structure')
    CHECK['Fig1 coding exon lengths (KRAS/HRAS/NRAS, E2-E4)'] = [
        [I(e['coding_len']) for e in exons(TXS[k]) if I(e['coding_len'])][:3]
        for k in ('KRAS4B', 'HRAS', 'NRAS')]


# =========================================================== Figure 2 ======
# Manuscript Figure 4. Annotation layout rebuilt 2026-11-01 (author: the
# explanatory text was neither tidy nor sensibly placed). What changed:
#   · the six motif labels no longer dangle on leader lines of six different
#     lengths and angles; they sit in a 3 x 2 grid of swatch + name + range,
#     left-aligned to the protein bar, in N-to-C reading order;
#   · 'G domain (aa 1-166)' moved inside the bar, into the empty stretch
#     between switch II and G4, so it no longer collides with the Q61 arrow;
#   · the two long diagonal arrows to the HVR and C185 notes are gone: both
#     notes are now one left-aligned footnote under the residue axis;
#   · legend trimmed to the two secondary-structure marks (the bar labels
#     'G domain' and 'HVR' in place) and set on one baseline with the
#     transcript identifier;
#   · the floating axis title is dropped — the row label already reads
#     'KRAS4B protein, 188 aa'.
def fig2():
    # Manuscript Figure 4. Rebuilt 2026-11-02 (author: text too small, column
    # width not used, labels pushed to the right, wide gap between the row
    # labels and the tracks). One text size, a measured label gutter, tracks
    # to the right margin; exon length/aa range sit inside the exon boxes;
    # motifs are labelled directly under the protein bar; the transcript ID
    # and the HVR footnote move to the legend (HVR detail is Figure 3c).
    AA, NCOD = 188, 189                       # residues; codons incl. stop
    T = 7.5
    INK, GREY = P1['ink'], P1['grey']
    HEL, STR = '#3E7CB1', '#33434C'
    EXC = ['#CFE5E2', '#8CC2BC', '#3F8F95', '#1F6F78']
    EXT = [INK, INK, 'white', 'white']
    ex = [e for e in exons(TXS['KRAS4B']) if I(e['coding_len'])]
    assert sum(I(e['coding_len']) for e in ex) == 3 * NCOD

    # vertical layout, mm from the top
    EXH, G1, SSH, G2, PH, G3, LAB, G4 = 8.5, 3.2, 5.0, 8.0, 6.0, 1.4, 7.0, 0.6
    y_ex = 1.5
    y_ss = y_ex + EXH + G1
    y_pr = y_ss + SSH + G2
    y_lb = y_pr + PH + G3
    y_ax = y_lb + LAB + G4
    H = y_ax + 5.0
    W = W2
    fig = figure(H)
    ax = axes(fig, 0, 0, W, H)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)                          # y measured from the top
    ax.axis('off')
    rend = fig.canvas.get_renderer()

    def tw(s, bold=False):
        o = fig.text(0, 0, s, fontsize=T, fontweight='bold' if bold else None)
        w = o.get_window_extent(rend).width / fig.dpi / MM
        o.remove()
        return w

    ROWL = [('CDS', '567 bp'), ('Secondary', 'structure'),
            ('KRAS4B', '188 aa')]
    GUT = max(tw(s) for p in ROWL for s in p) + 4.5
    R = 2.0
    s = (W - GUT - R) / NCOD

    def X(r):                                  # residue boundary -> mm
        return GUT + r * s

    def rowlab(y, pair):
        ax.text(GUT - 2.5, y, '\n'.join(pair), ha='right', va='center',
                fontsize=T, color=INK, linespacing=1.3)

    # 1) CDS, drawn in nucleotide/3 so the split codon 97 falls where it does
    for k, e in enumerate(ex):
        x0 = X((I(e['cds_offset_start']) - 1) / 3)
        x1 = X(I(e['cds_offset_end']) / 3)
        ax.add_patch(Rectangle((x0, y_ex), x1 - x0, EXH, fc=EXC[k],
                               ec='white', lw=0.8))
        last = min(I(e['codon_last']), AA)
        cx = (x0 + x1) / 2
        ax.text(cx, y_ex + EXH * 0.32, 'Exon %s' % e['exon_rank'],
                ha='center', va='center', fontsize=T, color=EXT[k],
                fontweight='bold')
        ax.text(cx, y_ex + EXH * 0.71, '%s bp · aa %d–%d' %
                (e['coding_len'], I(e['codon_first']), last), ha='center',
                va='center', fontsize=T, color=EXT[k])
        # faint column linking the exon to the residues it encodes
        ax.add_patch(Rectangle((x0, y_ex + EXH), x1 - x0, y_pr - y_ex - EXH,
                               fc=EXC[k], alpha=0.16, ec='none', zorder=0))
    rowlab(y_ex + EXH / 2, ROWL[0])

    # 2) secondary structure (resolved part only, to residue 166)
    yc = y_ss + SSH / 2
    for f in FEAT:
        if f['gene'] != 'KRAS' or f['type'] not in ('Helix', 'Beta strand'):
            continue
        a, b = I(f['start']), min(I(f['end']), 166)
        if a > 166:
            continue
        if f['type'] == 'Helix':
            ax.add_patch(FancyBboxPatch((X(a - 1), yc - 1.35), X(b) - X(a - 1),
                                        2.7, boxstyle='round,pad=0,rounding_size=0.6',
                                        fc=HEL, ec='none'))
        else:
            L = X(b) - X(a - 1)
            ax.add_patch(FancyArrow(X(a - 1), yc, L, 0, width=1.3,
                                    head_width=2.9, head_length=min(1.8, L),
                                    length_includes_head=True, fc=STR,
                                    ec='none'))
    rowlab(yc, ROWL[1])
    # legend in the empty 167-188 stretch of this row
    lx = X(169)
    for i, (lab, col, kind) in enumerate([('α-helix', HEL, 'h'),
                                          ('β-strand', STR, 's')]):
        yy = yc - 1.7 + i * 3.4
        if kind == 'h':
            ax.add_patch(FancyBboxPatch((lx, yy - 0.8), 3.6, 1.6,
                                        boxstyle='round,pad=0,rounding_size=0.4',
                                        fc=col, ec='none'))
        else:
            ax.add_patch(FancyArrow(lx, yy, 3.6, 0, width=0.8, head_width=1.8,
                                    head_length=1.3, length_includes_head=True,
                                    fc=col, ec='none'))
        ax.text(lx + 4.8, yy, lab, ha='left', va='center', fontsize=T,
                color=INK)

    # 3) protein bar
    yt, yb = y_pr, y_pr + PH
    ax.add_patch(Rectangle((X(0), yt), X(166) - X(0), PH, fc='#E3E8EA',
                           ec=INK, lw=0.5))
    ax.add_patch(Rectangle((X(166), yt), X(AA) - X(166), PH, fc='#8C989C',
                           ec=INK, lw=0.5))
    ax.text((X(166) + X(AA)) / 2, yt + PH / 2, 'HVR', ha='center',
            va='center', fontsize=T, color='white', fontweight='bold')
    ax.text((X(77) + X(115)) / 2, yt + PH / 2, 'G domain 1–166',
            ha='center', va='center', fontsize=T, color=GREY)
    MOT = [('G1 / P-loop', 10, 17, C['ploop'], 'center'),
           ('switch I', 30, 38, C['sw1'], 'center'),
           ('G3 DxxG', 57, 60, C['g3'], 'right'),
           ('switch II', 60, 76, C['sw2'], 'left'),
           ('G4 NKxD', 116, 119, C['g4'], 'center'),
           ('G5 SAK', 145, 147, C['g5'], 'center')]
    for n, a, b, col, ha in MOT:
        ax.add_patch(Rectangle((X(a - 1), yt), X(b) - X(a - 1), PH, fc=col,
                               ec=INK, lw=LW['edge']))
    rowlab(yt + PH / 2, ROWL[2])

    # motif labels straight under the bar, short leaders, no legend grid
    def mlab(xm, xt, ha, name, rng, col):
        ax.plot([xm, xm], [yb, yb + G3 * 0.8], color=col, lw=0.6)
        ax.text(xt, y_lb, name, ha=ha, va='top', fontsize=T, color=col,
                fontweight='bold')
        ax.text(xt, y_lb + 3.4, rng, ha=ha, va='top', fontsize=T, color=GREY)
    for n, a, b, col, ha in MOT:
        xm = (X(a - 1) + X(b)) / 2
        # G3 and switch II share residue 60: split their labels at it
        xt = {'center': xm, 'right': X(58.6), 'left': X(60.4)}[ha]
        mlab(xm, xt, ha, n, '%d–%d' % (a, b), col)
    mlab((X(166) + X(AA)) / 2, (X(166) + X(AA)) / 2, 'center', 'HVR',
         '167–188', '#5E6A70')

    # 4) hotspots: labels in the gap between the SS row and the bar
    yh = y_ss + SSH + 1.6
    for cd, lb in [(12.5, 'G12/G13'), (61, 'Q61'), (117, 'K117'),
                   (146, 'A146')]:
        xx = X(cd - 0.5)
        ax.annotate(lb, xy=(xx, yt), xytext=(xx, yh), ha='center', va='top',
                    fontsize=T, color=P1['hot'], fontweight='bold',
                    arrowprops=dict(arrowstyle='-|>', lw=0.7, color=P1['hot'],
                                    shrinkA=0, shrinkB=0, mutation_scale=6,
                                    relpos=(0.5, 0.0)))

    # 5) residue ruler along the bottom
    ax.plot([X(0), X(AA)], [y_ax, y_ax], color=GREY, lw=LW['axis'])
    for t in (1, 25, 50, 75, 100, 125, 150, 188):
        xx = X(t - 0.5)
        ax.plot([xx, xx], [y_ax, y_ax + 0.9], color=GREY, lw=LW['axis'])
        ax.text(xx, y_ax + 1.3, str(t), ha='center', va='top', fontsize=T,
                color=GREY)
    ax.text(GUT - 2.5, y_ax + 1.3, 'Residue', ha='right', va='top',
            fontsize=T, color=GREY)
    CHECK['Fig4 (file Fig2) label gutter, mm'] = round(GUT, 1)
    CHECK['Fig4 (file Fig2) height, mm'] = round(H, 1)
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

    # 版式（2026-11-02 作者「整齐、用足 Word 版心宽、字不能偏小」）：
    # a 通栏在上，b、c 并排在下；三块共用一套字号、条粗与行距，
    # 类目标签栏宽按实测文字宽度定，面板字母贴同一条左边线与同一条顶线。
    T, PN = 7.5, 9                     # 全图唯一正文字号；面板字母
    NA, NB, PITCH, BAR = 16, 10, 4.1, 2.8
    BOT, XAX, GAP, TOP, LEGH = 1.0, 9.5, 9.0, 4.0, 6.0
    HA, HB = NA * PITCH, NB * PITCH
    H = BOT + XAX + HB + GAP + XAX + HA + LEGH + TOP
    fig = figure(H)
    rend = fig.canvas.get_renderer()

    def text_mm(labels):
        w = 0
        for t in labels:
            o = fig.text(0, 0, t, fontsize=T)
            w = max(w, o.get_window_extent(rend).width / fig.dpi / MM)
            o.remove()
        return w

    def style(ax, n, labels, xlab):
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels, fontsize=T)
        ax.set_ylim(-0.5, n - 0.5)
        ax.set_xlabel(xlab, fontsize=T, labelpad=2)
        ax.tick_params(axis='y', length=0, pad=2)
        ax.tick_params(axis='x', labelsize=T, pad=1.5)
        for s_ in ('top', 'right', 'left'):
            ax.spines[s_].set_visible(False)

    def value(ax, x, y, r):
        ax.text(x, y, '%.0f%% (%s/%s)' % (float(r['freq_pct']),
                                         r['n_mut_samples'], r['n_samples']),
                va='center', fontsize=T, color='#333333')

    LEFT, PADL = 4.0, 1.5              # 面板字母所在左边线；标签与轴的间隙
    ks = sorted([r for r in BYCT if r['gene'] == 'KRAS'],
                key=lambda r: -float(r['freq_pct']))[:NA][::-1]
    labA = [r['cancer_type'] for r in ks]
    xa = LEFT + text_mm(labA) + PADL
    ya = BOT + XAX + HB + GAP + XAX
    wa = W2 - xa - 24                  # 右侧留给最长的数值标注
    axA = axes(fig, xa, ya, wa, HA)
    XMAX = 80
    for i, r in enumerate(ks):
        f = float(r['freq_pct'])
        cc = comp[r['cancer_type']]
        tot = sum(cc.values()) or 1
        left = 0.0
        for k, col in zip(KEYS, PAL):
            w = f * cc[k] / tot
            if w > 0:
                axA.barh(i, w, left=left, color=col, height=BAR / PITCH,
                         ec='white', lw=0.3)
            left += w
        value(axA, f + 1.0, i, r)
    axA.set_xlim(0, XMAX)
    axA.set_xticks(range(0, XMAX + 1, 20))
    style(axA, NA, labA, GI('KRAS') + '-mutant samples (%)')
    fig.legend(handles=[Rectangle((0, 0), 1, 1, fc=c, label=k)
                        for k, c in zip(KEYS, PAL)],
               loc='lower left', ncol=len(KEYS), fontsize=T, borderpad=0,
               handlelength=1.4, handleheight=0.9, columnspacing=1.3,
               title='Allele', title_fontsize=T, alignment='left',
               bbox_to_anchor=(xa / W2, (ya + HA + 0.8) / H))
    # 图例题与条目同排：legend title 只能排在上方，故去掉，另按图例实测中线排「Allele」
    lg = fig.legends[-1]
    lg.set_title(None)
    bb = lg.get_window_extent(rend).transformed(fig.transFigure.inverted())
    fig.text(xa / W2 - 0.004, (bb.y0 + bb.y1) / 2, 'Allele',
             fontsize=T, ha='right', va='center', fontweight='bold')
    fig.text(LEFT / W2, (ya + HA + LEGH) / H, 'a', fontsize=PN,
             fontweight='bold', ha='left', va='bottom')

    half = W2 / 2
    labw = text_mm([r['cancer_type'] for r in BYCT if r['gene'] in ('NRAS', 'HRAS')
                    and r in sorted([x for x in BYCT if x['gene'] == r['gene']],
                                    key=lambda x: -float(x['freq_pct']))[:NB]])
    for idx, (g, col, pn) in enumerate((('NRAS', C['n'], 'b'),
                                        ('HRAS', C['h'], 'c'))):
        rs = sorted([r for r in BYCT if r['gene'] == g],
                    key=lambda r: -float(r['freq_pct']))[:NB][::-1]
        labs = [r['cancer_type'] for r in rs]
        x0 = LEFT + idx * half
        xb = x0 + labw + PADL          # b、c 共用同一标签栏宽，两块几何完全对称
        wb = half * (idx + 1) - xb - 22
        a_ = axes(fig, xb, BOT + XAX, wb, HB)
        mx = max(float(r['freq_pct']) for r in rs)
        a_.barh(range(NB), [float(r['freq_pct']) for r in rs], color=col,
                height=BAR / PITCH, ec='none')
        for i, r in enumerate(rs):
            value(a_, float(r['freq_pct']) + mx * 0.03, i, r)
        lim = 25 if g == 'NRAS' else 6
        a_.set_xlim(0, lim)
        a_.set_xticks(range(0, lim + 1, 5 if g == 'NRAS' else 2))
        style(a_, NB, labs, GI(g) + '-mutant samples (%)')
        fig.text(x0 / W2, (BOT + XAX + HB + 2.0) / H, pn, fontsize=PN,
                 fontweight='bold', ha='left', va='bottom')
    save(fig, 'Fig4_cancer_type_distribution')
    CHECK['Fig4 KRAS top3'] = [(r['cancer_type'], r['freq_pct'],
                                '%s/%s' % (r['n_mut_samples'], r['n_samples']))
                               for r in ks[::-1][:3]]


# =========================================================== Figure 5 ======
def fig5():
    # Manuscript Figure 5. Rebuilt 2026-11-02 (author: same problems as
    # Figure 4 — panel letters far from the artwork, small text, thin lines,
    # heavy blue bars, colours not coordinated). Layout as Figures 2 and 4:
    #   · one text size (T = 7.5 pt) and one panel-letter size; the row-label
    #     gutter of b is measured, a and b share that left edge and run to the
    #     right margin; letters sit on one left line next to the artwork;
    #   · a: y axis starts at 30 (no data below 38.9), four confidence bands
    #     become three dashed thresholds labelled at the right edge; switch I/II
    #     and the HVR are named directly; data lines 1.4 pt;
    #   · b: a three-column table (PDB, protein, resolution) replaces the
    #     packed tick string; observed residues as a teal bar on a thin grey
    #     1-189 track, and unmodelled internal residues are drawn at their true
    #     length (read from the coordinate files, not a fixed 1-residue notch).
    T, PN = 7.5, 9
    INK, GREY = P1['ink'], P1['grey']
    GCOL = {'KRAS': '#E0533D', 'NRAS': '#1F6F78', 'HRAS': '#E9A23B'}
    PDBS = ('3CON', '4LDJ', '4OBE', '4Q21', '5P21', '5VQ2', '6GJ8', '6OIM',
            '7RPZ')
    PROT = {'3CON': 'NRAS', '4LDJ': 'KRAS G12C', '4OBE': 'KRAS',
            '4Q21': 'HRAS', '5P21': 'HRAS', '5VQ2': 'KRAS', '6GJ8': 'KRAS G12D',
            '6OIM': 'KRAS G12C', '7RPZ': 'KRAS G12D'}
    LIG = {'GDP': 'GDP', 'GNP': 'GppNHp', 'GTP': 'GTP', 'GCP': 'GppCH$_2$p'}
    cov = sorted([c for c in COV if c['pdb'] in PDBS],
                 key=lambda c: c['pdb'], reverse=True)

    def observed(c):
        s = set()
        for l in open(os.path.join(STRU, '%s.pdb' % c['pdb'])):
            if l.startswith('ATOM') and l[21] == c['chain']:
                s.add(int(l[22:26]))
        return sorted(r for r in s if 0 < r < 400)

    LEFT, AA = 0.5, 189
    HA, PITCH, BAR = 46.0, 4.6, 2.6
    HB = len(cov) * PITCH
    TOP, HEAD, XAX, GAP = 5.0, 5.0, 10.0, 7.0
    H = TOP + HA + GAP + HEAD + HB + XAX
    fig = figure(H)
    rend = fig.canvas.get_renderer()

    def tw(s, bold=False):
        o = fig.text(0, 0, s, fontsize=T, fontweight='bold' if bold else None)
        w = o.get_window_extent(rend).width / fig.dpi / MM
        o.remove()
        return w

    # table columns of b: PDB | protein | resolution ; widths measured
    c1 = max(tw(c['pdb'], True) for c in cov + [{'pdb': 'PDB'}])
    c2 = max(tw(s) for s in list(PROT.values()) + ['Protein'])
    c3 = max(tw('%.2f Å' % PDBM[c['pdb']]['resolution']) for c in cov)
    CG = 3.0
    x1 = LEFT + 3.5
    x2 = x1 + c1 + CG
    x3 = x2 + c2 + CG
    XL = x3 + c3 + 3.5                     # left edge of both data axes
    RT = 21.0                              # right margin: threshold labels
    WD = W2 - XL - RT

    # ---- a: pLDDT ----
    ya = H - TOP - HA
    ax = axes(fig, XL, ya, WD, HA)
    ax.axvspan(167, AA + 0.5, color='#ECEFF0', zorder=0, lw=0)
    for nm, lo, hi, _ in REG[1:3]:             # switch I 30-38, switch II 60-76
        ax.axvspan(lo - 0.5, hi + 0.5, color='#F6F1E6', zorder=0, lw=0)
    for g in ('HRAS', 'NRAS', 'KRAS'):
        y = PLD[g]
        ax.plot(range(1, len(y) + 1), y, color=GCOL[g], lw=1.4, zorder=3,
                solid_joinstyle='round', solid_capstyle='round')
    for v, nm in ((90, 'Very high'), (70, 'Confident'), (50, 'Low')):
        ax.axhline(v, color='#8A9497', lw=0.6, ls=(0, (3, 2)), zorder=1)
    for y0, nm in ((95, 'Very high'), (80, 'Confident'), (60, 'Low'),
                   (40, 'Very low')):
        ax.text(AA + 3, y0, nm, fontsize=T, color=GREY, va='center',
                ha='left', clip_on=False)
    for x0, nm in ((34, 'switch I'), (68, 'switch II'), (178, 'HVR')):
        ax.text(x0, 101.5, nm, fontsize=T, color=GREY, ha='center',
                va='bottom', clip_on=False)
    ax.set_ylim(30, 101)
    ax.set_yticks(range(30, 101, 10))
    ax.set_xlim(0.5, AA + 0.5)
    ax.set_xticks(range(25, AA, 25))
    ax.set_xticklabels([])
    ax.set_ylabel('pLDDT', fontsize=T, labelpad=2)
    ax.tick_params(labelsize=T, pad=1.5, width=0.6, length=2.2)
    for s_ in ('top', 'right'):
        ax.spines[s_].set_visible(False)
    for s_ in ('left', 'bottom'):
        ax.spines[s_].set_linewidth(0.6)
    ax.legend(handles=[plt.Line2D([], [], color=GCOL[g], lw=1.8,
                                  label='%s (%s)' % (g, GCORE[g]['alphafold']['entryId']))
                       for g in ('KRAS', 'NRAS', 'HRAS')],
              loc='lower left', bbox_to_anchor=(0.01, 0.03), ncol=3,
              fontsize=T, borderpad=0, handlelength=1.8, columnspacing=1.6,
              frameon=False)
    fig.text(LEFT / W2, (ya + HA + 4.5) / H, 'a', fontsize=PN,
             fontweight='bold', ha='left', va='top')

    # ---- b: crystal-structure coverage ----
    yb = XAX
    ax2 = axes(fig, XL, yb, WD, HB)
    ax2.axvspan(167, AA + 0.5, color='#ECEFF0', zorder=0, lw=0)
    bh = BAR / PITCH
    toY = lambda i: (yb + (i + 0.5) * PITCH) / H
    for i, c in enumerate(cov):
        rs = observed(c)
        assert rs[0] == int(c['first_obs']) and rs[-1] == int(c['last_obs'])
        assert len(set(range(rs[0], rs[-1] + 1)) - set(rs)) == \
            int(c['missing_internal'])
        ax2.plot([0.5, AA + 0.5], [i, i], color='#B9C3C5', lw=0.8, zorder=1,
                 solid_capstyle='butt')
        # contiguous observed runs
        run0 = rs[0]
        for a_, b_ in zip(rs, rs[1:] + [None]):
            if b_ is None or b_ != a_ + 1:
                ax2.add_patch(FancyBboxPatch(
                    (run0 - 0.5, i - bh / 2), a_ - run0 + 1, bh,
                    boxstyle='square,pad=0', fc=P1['cds'], ec='none',
                    zorder=2))
                run0 = b_
        y = toY(i)
        fig.text(x1 / W2, y, c['pdb'], fontsize=T, fontweight='bold',
                 va='center', color=INK)
        fig.text(x2 / W2, y, PROT[c['pdb']], fontsize=T, va='center',
                 color=INK)
        fig.text((x3 + c3) / W2, y, '%.2f Å' % PDBM[c['pdb']]['resolution'],
                 fontsize=T, va='center', ha='right', color=INK)
        nuc = [LIG[l] for l in PDBM[c['pdb']]['ligands'] if l in LIG]
        ax2.text(AA + 3, i, nuc[0], fontsize=T, color=GREY, va='center',
                 ha='left', clip_on=False)
    hy = (yb + HB + 1.2) / H
    for x_, s, ha in ((x1, 'PDB', 'left'), (x2, 'Protein', 'left'),
                      (x3 + c3, 'Resolution', 'right')):
        fig.text(x_ / W2, hy, s, fontsize=T, color=GREY, ha=ha, va='bottom')
    ax2.text(AA + 3, len(cov) - 0.5 + 1.2 / PITCH, 'Nucleotide', fontsize=T,
             color=GREY, ha='left', va='bottom', clip_on=False)
    ax2.set_xlim(0.5, AA + 0.5)
    ax2.set_ylim(-0.5, len(cov) - 0.5)
    ax2.set_yticks([])
    ax2.set_xticks([1] + list(range(25, AA, 25)) + [189])
    ax2.set_xlabel('Residue number', fontsize=T, labelpad=2)
    ax2.tick_params(labelsize=T, pad=1.5, width=0.6, length=2.2)
    for s_ in ('top', 'right', 'left'):
        ax2.spines[s_].set_visible(False)
    ax2.spines['bottom'].set_linewidth(0.6)
    fig.text(LEFT / W2, (yb + HB + HEAD) / H, 'b', fontsize=PN,
             fontweight='bold', ha='left', va='top')
    save(fig, 'Fig5_AlphaFold_confidence_and_coverage')
    CHECK['Fig5 last observed residue'] = {c['pdb']: int(c['last_obs'])
                                           for c in cov}
    CHECK['Fig5 height, mm'] = round(H, 1)


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


# ------------------------------------------------- manuscript Figure 3 ----
# File name kept as FigS1_KRAS_GDP_structure (it started life as a
# supplementary figure).  Three panels on the full 180 mm width:
#   a  the PyMOL render of 4OBE (figures/_S1_KRAS_GDP_4OBE.png), colour key
#      shared with the region bar of panel b;
#   b  KRAS4A / HRAS / NRAS compared with KRAS4B position by position:
#      every residue that differs from KRAS4B (or faces its gap) is dark;
#   c  the C-terminal end (161-189) written out, basic residues and the
#      lipidated cysteines marked.
# Sequences: UniProt P01116-2 (prepared_meta.json), P01116 / P01112 /
# P01111 canonical (genes_core.json).  Lipidation sites: UniProt
# S-palmitoyl / S-farnesyl cysteine features; KRAS4B carries none in that
# entry, so its farnesyl cysteine is the CAAX cysteine (length - 3) and the
# same rule is asserted against UniProt for the other three.
SEQ_KEYS = ['KRAS4B', 'KRAS4A', 'HRAS', 'NRAS']
CMP_KEYS = SEQ_KEYS[1:]


def nw(a, b):
    """Global alignment, match +1 / mismatch 0 / gap -1; returns gapped pair."""
    n, m = len(a), len(b)
    S = np.zeros((n + 1, m + 1))
    S[:, 0], S[0, :] = -np.arange(n + 1), -np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            S[i, j] = max(S[i - 1, j - 1] + (a[i - 1] == b[j - 1]),
                          S[i - 1, j] - 1, S[i, j - 1] - 1)
    i, j, x, y = n, m, [], []
    while i or j:
        if i and j and S[i, j] == S[i - 1, j - 1] + (a[i - 1] == b[j - 1]):
            x.append(a[i - 1]); y.append(b[j - 1]); i -= 1; j -= 1
        elif i and S[i, j] == S[i - 1, j] - 1:
            x.append(a[i - 1]); y.append('-'); i -= 1
        else:
            x.append('-'); y.append(b[j - 1]); j -= 1
    return ''.join(x[::-1]), ''.join(y[::-1])


def isoform_alignment():
    G = json.load(open(os.path.join(DATA, 'genes_core.json')))
    raw = {'KRAS4B': META['kras4b_seq'],
           'KRAS4A': G['KRAS']['uniprot_data']['sequence'],
           'HRAS': G['HRAS']['uniprot_data']['sequence'],
           'NRAS': G['NRAS']['uniprot_data']['sequence']}
    L = 189
    for k in ('KRAS4A', 'HRAS', 'NRAS'):
        assert len(raw[k]) == L, k
    assert len(raw['KRAS4B']) == 188
    # residues 1-166 carry no indel; place the single KRAS4B gap in the tail
    t4a, t4b = nw(raw['KRAS4A'][166:], raw['KRAS4B'][166:])
    assert t4a == raw['KRAS4A'][166:] and t4b.count('-') == 1, (t4a, t4b)
    aln = dict(raw)
    aln['KRAS4B'] = raw['KRAS4B'][:166] + t4b
    # lipidated cysteines, in alignment-column numbering (1-based)
    lip = {}
    for k, g in (('KRAS4A', 'KRAS'), ('HRAS', 'HRAS'), ('NRAS', 'NRAS')):
        f = G[g]['uniprot_data']['features']
        palm = sorted(int(x['start']) for x in f if x['type'] == 'Lipidation'
                      and x['desc'].startswith('S-palmitoyl cysteine'))
        farn = [int(x['start']) for x in f if x['type'] == 'Lipidation'
                and x['desc'].startswith('S-farnesyl cysteine')]
        assert farn == [L - 3] and raw[k][L - 4] == 'C', (k, farn)
        lip[k] = {'palm': palm, 'farn': farn}
    col4b = [i + 1 for i, c in enumerate(aln['KRAS4B']) if c != '-']
    assert raw['KRAS4B'][185 - 1] == 'C'            # CAAX cysteine, C185
    lip['KRAS4B'] = {'palm': [], 'farn': [col4b[185 - 1]]}
    for k in lip:
        for c in lip[k]['palm'] + lip[k]['farn']:
            assert aln[k][c - 1] == 'C', (k, c)
    var = []                                        # columns not all identical
    for i in range(L):
        if len({aln[k][i] for k in SEQ_KEYS}) > 1:   # gap counts as a state
            var.append(i + 1)
    return raw, aln, lip, var


def fig_s1():
    raw, aln, lip, var = isoform_alignment()
    L = len(aln['HRAS'])
    T, PN = 7.5, 9
    INK, GREY = P1['ink'], P1['grey']
    DIFF, SAME = '#33434C', '#E3E8EA'
    BASIC, PALM, FARN = '#D5E6F1', P1['cds'], P1['hot']
    CAAX = '#8C989C'
    W, H = W2, 74.0
    fig = figure(H)
    rend = fig.canvas.get_renderer()

    def tw(s, bold=False, fs=T):
        o = fig.text(0, 0, s, fontsize=fs, fontweight='bold' if bold else None)
        w = o.get_window_extent(rend).width / fig.dpi / MM
        o.remove()
        return w

    # ---------------------------------------------------- a: structure --
    img = plt.imread(os.path.join(FIG, '_S1_KRAS_GDP_4OBE.png'))
    a_ = img[:, :, 3] > 0.02
    rs, cs = np.where(a_.any(1))[0], np.where(a_.any(0))[0]
    pad = 12
    img = img[rs[0] - pad:rs[-1] + pad, cs[0] - pad:cs[-1] + pad]
    TOP, KEY = 4.0, 7.0
    AW = 66.0
    AH = AW * img.shape[0] / img.shape[1]
    if AH > H - TOP - KEY:
        AH = H - TOP - KEY
        AW = AH * img.shape[1] / img.shape[0]
    axA = axes(fig, 3.0, H - TOP - AH, AW, AH)
    axA.imshow(img, interpolation='antialiased')
    axA.set_axis_off()
    fig.text(1.0 / W, (H - 1.2) / H, 'a', fontsize=PN, fontweight='bold',
             va='top')
    fig.legend(handles=[
        plt.Line2D([], [], ls='', marker='o', ms=4, color=C['strand'],
                   label='GDP'),
        plt.Line2D([], [], ls='', marker='o', ms=4, color=C['ploop'],
                   label='Mg$^{2+}$'),
        plt.Line2D([], [], ls='', marker='o', ms=4, color=C['hot'], mec='k',
                   mew=0.3, label='Gly12')],
        loc='center', bbox_to_anchor=((3.0 + AW / 2) / W, (H - TOP - AH - 3.5) / H),
        ncol=3, fontsize=T, handletextpad=0.3, columnspacing=1.4,
        borderpad=0, borderaxespad=0)

    # ---------------------------------------------- b: four-way comparison --
    X0 = 3.0 + AW + 6.0                        # right column left edge
    labs = {'KRAS4B': 'KRAS4B', 'KRAS4A': 'KRAS4A', 'HRAS': 'HRAS',
            'NRAS': 'NRAS'}
    GUT = X0 + max(tw(s) for s in labs.values()) + 2.0
    PW = W - GUT - 3.0
    RH, RG = 3.0, 0.9                           # row height / gap, mm
    yb_top = H - TOP - 7.5                     # top of the region bar
    BAR = 1.8
    rows_top = yb_top - BAR - 1.6
    HB = 3 * RH + 2 * RG
    axB = axes(fig, GUT, rows_top - HB, PW, yb_top - (rows_top - HB))
    axB.set_xlim(0.5, L + 0.5)
    axB.set_ylim(-HB, yb_top - rows_top)
    axB.set_axis_off()
    # region bar (colours = panel a)
    regs = [r for r in REG if r[0] != 'HVR']
    yb = yb_top - rows_top - BAR
    axB.add_patch(Rectangle((0.5, yb + BAR / 2 - 0.15), L, 0.3, fc=SAME,
                            ec='none'))
    for nm, lo, hi, col in regs:
        axB.add_patch(Rectangle((lo - 0.5, yb), hi - lo + 1, BAR, fc=col,
                                ec='none'))
    axB.add_patch(Rectangle((166.5, yb), L - 166, BAR, fc='#9AA7A9',
                            ec='none'))
    # labels above the bar: one tier, assert no collision
    upp = PW / L                                # mm per residue
    lab_items = [(nm, (lo + hi) / 2, col) for nm, lo, hi, col in regs] + \
        [('HVR', (167 + L) / 2, GREY)]
    spans = []
    for nm, cx, col in lab_items:
        w = tw(nm)
        spans.append(((cx - 0.5) * upp - w / 2, (cx - 0.5) * upp + w / 2, nm))
        axB.text(cx, yb + BAR + 0.7, nm, ha='center', va='bottom',
                 fontsize=T, color=col)
    spans.sort()
    for (a0, a1, n0), (b0, b1, n1) in zip(spans, spans[1:]):
        assert a1 + 0.8 < b0, 'FigS1 region labels overlap: %s / %s' % (n0, n1)
    # sequence rows: KRAS4B is the reference (it is the protein drawn in
    # Figures 4-6); each other row darkens the residues that differ from it
    cnt = {}
    REF = aln['KRAS4B']
    fig.text((GUT - 2.0) / W, (rows_top + yb + BAR / 2) / H, 'KRAS4B',
             ha='right', va='center', fontsize=T, color=INK)
    for r, k in enumerate(CMP_KEYS):
        y = -(r * (RH + RG)) - RH
        axB.add_patch(Rectangle((0.5, y), L, RH, fc=SAME, ec='none'))
        d = [i + 1 for i in range(L) if aln[k][i] != REF[i]]
        for i in d:
            axB.add_patch(Rectangle((i - 0.5, y), 1, RH, fc=DIFF, ec='none'))
        cnt[k] = (sum(i <= 166 for i in d), sum(i > 166 for i in d))
        fig.text((GUT - 2.0) / W, (rows_top + y + RH / 2) / H, labs[k],
                 ha='right', va='center', fontsize=T, color=INK)
    # axis
    yax = rows_top - HB
    axX = axes(fig, GUT, yax - 0.01, PW, 0.01)
    axX.set_xlim(0.5, L + 0.5)
    axX.set_yticks([])
    for s_ in ('top', 'right', 'left'):
        axX.spines[s_].set_visible(False)
    axX.spines['bottom'].set_color(GREY)
    axX.set_xticks([1, 50, 100, 150, 189])
    axX.tick_params(axis='x', colors=GREY, labelcolor=INK, length=1.8,
                    pad=1.2, labelsize=T)
    nG = sum(1 for i in var if i <= 166)
    nH = sum(1 for i in var if i > 166)
    fig.text((X0 - 3.0) / W, (H - 1.2) / H, 'b', fontsize=PN,
             fontweight='bold', va='top')
    CHECK['FigS1 variable positions (G domain / HVR)'] = (nG, nH)
    CHECK['FigS1 differences from KRAS4B (1-166, 167-189)'] = cnt

    # ------------------------------------------------ c: C-terminal zoom --
    C0, C1 = 161, L
    ncol = C1 - C0 + 1
    CH, CG = 5.0, 1.0
    HC = 4 * CH + 3 * CG
    yc_top = yax - 9.5                         # top of the number row
    yc = yc_top - 3.6 - HC
    axC = axes(fig, GUT, yc, PW, HC)
    axC.set_xlim(C0 - 0.5, C1 + 0.5)
    axC.set_ylim(-HC, 0)
    axC.set_axis_off()
    cw = PW / ncol
    for r, k in enumerate(SEQ_KEYS):
        y = -(r * (CH + CG)) - CH
        pos = 0
        n_before = sum(1 for c in aln[k][:C0 - 1] if c != '-')
        for i in range(C0, C1 + 1):
            c = aln[k][i - 1]
            if c == '-':
                axC.text(i, y + CH / 2, '–', ha='center', va='center',
                         fontsize=T, color=CAAX)
                continue
            pos += 1
            fc, tc, fw = None, INK, None
            if i in lip[k]['farn']:
                fc, tc, fw = FARN, 'white', 'bold'
            elif i in lip[k]['palm']:
                fc, tc, fw = PALM, 'white', 'bold'
            elif c in 'KR':
                fc = BASIC
            if i > lip[k]['farn'][0]:
                tc = CAAX
            if fc:
                axC.add_patch(Rectangle((i - 0.46, y), 0.92, CH, fc=fc,
                                        ec='none'))
            axC.text(i, y + CH / 2, c, ha='center', va='center', fontsize=T,
                     color=tc, fontweight=fw)
        fig.text((GUT - 2.0) / W, (yc + HC + y + CH / 2) / H, labs[k],
                 ha='right', va='center', fontsize=T, color=INK)
    # G domain | HVR divider and column numbers
    xd = GUT + (166.5 - C0 + 0.5) * cw
    fig.add_artist(plt.Line2D([xd / W] * 2, [(yc - 0.6) / H,
                                             (yc + HC + 0.6) / H],
                              color=GREY, lw=0.5, ls=(0, (2, 1.5))))
    for n in (161, 166, 170, 175, 180, 185, 189):
        fig.text((GUT + (n - C0 + 0.5) * cw) / W, (yc + HC + 1.0) / H, str(n),
                 ha='center', va='bottom', fontsize=T, color=GREY)
    # zoom guides from b's 161-189 span to c
    for xb, xc_ in ((GUT + (C0 - 1) * upp, GUT), (GUT + L * upp, GUT + PW)):
        fig.add_artist(plt.Line2D([xb / W, xc_ / W],
                                  [(yax - 3.6) / H, (yc_top + 0.4) / H],
                                  color=GREY, lw=0.4, alpha=0.6))
    fig.text((X0 - 3.0) / W, (yc_top + 2.0) / H, 'c', fontsize=PN,
             fontweight='bold', va='top')
    fig.legend(handles=[
        Rectangle((0, 0), 1, 1, fc=BASIC, label='Lys/Arg'),
        Rectangle((0, 0), 1, 1, fc=PALM, label='S-palmitoyl Cys'),
        Rectangle((0, 0), 1, 1, fc=FARN, label='S-farnesyl Cys')],
        loc='center', bbox_to_anchor=((GUT + PW / 2) / W,
                                      (H - TOP - AH - 3.5) / H),
        ncol=3, fontsize=T, handlelength=1.1, handleheight=0.9,
        handletextpad=0.4, columnspacing=1.2, borderpad=0, borderaxespad=0)
    CHECK['FigS1 lipidated Cys (alignment columns)'] = lip
    save(fig, 'FigS1_KRAS_GDP_structure')


for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig_s1):
    print('==', f.__name__)
    f()

print('\n--- self-check -------------------------------------------------')
for k, v in CHECK.items():
    print('%-46s %s' % (k, v))
print('figures ->', FIG)
