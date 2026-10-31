# Figure 6, panel c — KRAS(G12C)–sotorasib covalent complex (PDB 6OIM)
# Publication-grade molecular rendering with PyMOL's ray tracer.
# Run headless from the RAS基因与蛋白结构 directory:  pymol -cq 脚本/render_panelC_pymol.pml
# Output:        figures/_panelC_6OIM.png  (transparent background, embedded by 03_figures.py)

load 结构文件/6OIM.pdb, kras

remove solvent
remove not chain A
remove hydrogens

hide everything
show cartoon, polymer
set cartoon_fancy_helices, 1
set cartoon_smooth_loops, 1
set cartoon_highlight_color, grey70

# --- colour palette identical to the rest of the figure set --------------
set_color c_core,   [0.909, 0.929, 0.945]   # #E8EDF1 G domain
set_color c_ploop,  [0.110, 0.486, 0.329]   # #1C7C54
set_color c_sw1,    [0.878, 0.624, 0.243]   # #E09F3E
set_color c_sw2,    [0.749, 0.192, 0.000]   # #BF3100
set_color c_g4,     [0.416, 0.298, 0.576]   # #6A4C93
set_color c_g5,     [0.616, 0.427, 0.749]   # #9D6DBF
set_color c_hot,    [0.843, 0.149, 0.239]   # #D7263D
set_color c_gdp,    [0.208, 0.314, 0.439]   # #355070
set_color c_mg,     [0.110, 0.486, 0.329]   # #1C7C54

color c_core, polymer
color c_ploop, resi 10-17
color c_sw1,   resi 30-38
color c_sw2,   resi 60-76
color c_g4,    resi 116-119
color c_g5,    resi 145-147

# --- ligands -------------------------------------------------------------
show sticks, resn GDP+MOV
show spheres, resn MG
set sphere_scale, 0.42, resn MG
color c_gdp, resn GDP
color c_sw2, resn MOV
color c_mg,  resn MG
util.cnc("resn GDP+MOV")          # heteroatoms by element, carbons keep the colour above
color c_gdp, resn GDP and elem C
color c_sw2, resn MOV and elem C

# --- covalent attachment site -------------------------------------------
show sticks, resi 12 and not name N+C+O
color c_hot, resi 12 and elem C
set stick_radius, 0.16
set stick_radius, 0.20, resn MOV

# --- lighting and outlines (ChimeraX-like silhouettes) -------------------
bg_color white
set ray_opaque_background, 0
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
set cartoon_discrete_colors, 1
set orthoscopic, 1

# --- reproducible camera: orient on the protein, then fixed rotations ----
orient polymer
turn y, 90
turn x, -10
zoom polymer, 4

ray 3000, 3400
png figures/_panelC_6OIM.png, dpi=400
