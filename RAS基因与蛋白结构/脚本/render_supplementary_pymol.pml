# Supplementary molecular figures S1–S3, rendered with PyMOL.
# Run headless:  pymol -cq 脚本/render_supplementary_pymol.pml
# Outputs (transparent background, assembled by 04_supplementary.py):
#   figures/_S1_KRAS_GDP_4OBE.png        switch regions on the GDP-bound state
#   figures/_S2_GDP_vs_GTP_overlay.png   4OBE / 5VQ2 superposition
#   figures/_S3_AlphaFold_pLDDT.png      full-length model coloured by pLDDT

# ---- shared palette (identical to the main figure set) -------------------
set_color c_core,  [0.909, 0.929, 0.945]
set_color c_ploop, [0.110, 0.486, 0.329]
set_color c_sw1,   [0.878, 0.624, 0.243]
set_color c_sw2,   [0.749, 0.192, 0.000]
set_color c_g4,    [0.416, 0.298, 0.576]
set_color c_g5,    [0.616, 0.427, 0.749]
set_color c_hot,   [0.843, 0.149, 0.239]
set_color c_gdp,   [0.208, 0.314, 0.439]
set_color c_gtp,   [0.180, 0.525, 0.671]
set_color c_mg,    [0.110, 0.486, 0.329]
set_color c_warm,  [0.816, 0.549, 0.376]
set_color c_cool,  [0.624, 0.706, 0.780]
# AlphaFold official confidence palette
set_color af_vh,   [0.000, 0.325, 0.839]
set_color af_c,    [0.396, 0.796, 0.953]
set_color af_l,    [1.000, 0.859, 0.075]
set_color af_vl,   [1.000, 0.490, 0.271]

set cartoon_fancy_helices, 1
set cartoon_smooth_loops, 1
set ray_trace_mode, 1
set ray_trace_color, black
set ray_trace_gain, 0.18
set antialias, 2
set ambient, 0.30
set direct, 0.55
set reflect, 0.25
set specular, 0.15
set depth_cue, 0
set ray_shadows, 0
set orthoscopic, 1
set ray_opaque_background, 0
set stick_radius, 0.16
bg_color white

# ========================= S1: KRAS–GDP (4OBE) ===========================
load 结构文件/4OBE.pdb, s1
remove solvent
remove not chain B
remove hydrogens
hide everything
show cartoon, polymer
color c_core, polymer
color c_ploop, resi 10-17
color c_sw1,   resi 30-38
color c_sw2,   resi 60-76
color c_g4,    resi 116-119
color c_g5,    resi 145-147
show sticks, resn GDP
show spheres, resn MG
set sphere_scale, 0.42, resn MG
util.cnc("resn GDP")
color c_gdp, resn GDP and elem C
color c_mg, resn MG
show sticks, resi 12 and not name N+C+O
color c_hot, resi 12 and elem C
orient polymer
turn y, 90
turn x, -10
zoom polymer, 4
ray 2400, 2400
png figures/_S1_KRAS_GDP_4OBE.png, dpi=600
delete s1

# ============== S2: GDP state vs GTP state, superposed ===================
load 结构文件/4OBE.pdb, gdp
load 结构文件/5VQ2.pdb, gtp
remove solvent
remove hydrogens
remove gdp and not chain B
remove gtp and not chain A
super gtp, gdp
hide everything
show cartoon, polymer
color c_cool, gdp
color c_warm, gtp
color c_gtp, gdp and resi 30-38+60-76
color c_sw2, gtp and resi 30-38+60-76
set cartoon_transparency, 0.45, gdp and not resi 30-38+60-76
set cartoon_transparency, 0.45, gtp and not resi 30-38+60-76
show sticks, resn GDP+GTP
util.cnc("resn GDP+GTP")
color c_gdp, resn GDP and elem C
color c_sw2, resn GTP and elem C
show spheres, resn MG
set sphere_scale, 0.38, resn MG
color c_mg, resn MG
orient gdp and polymer
turn y, 90
turn x, -10
zoom polymer, 4
ray 2400, 2400
png figures/_S2_GDP_vs_GTP_overlay.png, dpi=600
delete gdp
delete gtp

# ============ S3: full-length AlphaFold model coloured by pLDDT ==========
load 结构文件/AF-P01116-F1-model.pdb, af
hide everything
show cartoon, af
spectrum b, af_vl af_l af_c af_vh, af, 30, 100
color af_vl, af and b < 50
color af_l,  af and b > 50 and b < 70
color af_c,  af and b > 70 and b < 90
color af_vh, af and b > 90
orient af
zoom af, 4
ray 2400, 2400
png figures/_S3_AlphaFold_pLDDT.png, dpi=600
