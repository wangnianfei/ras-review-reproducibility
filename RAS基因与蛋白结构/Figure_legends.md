# Figure legends

Prepared 20 October 2026. All panels were generated from primary database records retrieved on that date (NCBI Gene, Ensembl GRCh38, UniProt, RCSB PDB, AlphaFold DB v6, cBioPortal); no values were taken from secondary literature. Source files: `figures/Fig*.pdf` (vector, editable text), `figures/Fig*.svg` (vector, for Illustrator/Inkscape), `figures/Fig*.png` (400 dpi, preview only). Underlying numbers are in `数据/表1–表7`.

---

## Figure 1 | Tumour-type distribution of *RAS* mutations.

**a**, Fraction of samples with a *KRAS* mutation in each tumour type of the MSK-IMPACT cohort, bars segmented by allele (G12D, G12V, G12C, G12R, G13D, any codon 61 change, other). **b**,**c**, The ten tumour types with the highest *NRAS* (**b**) and *HRAS* (**c**) mutation frequency. Tumour types with ≥40 sequenced samples; in parentheses, mutated/total samples. MSK-IMPACT is a single-centre US cohort enriched for advanced disease; its G12C share should not be extrapolated to East Asian populations (East Asian data in section 1.2).

## Figure 2 | Genomic organization of the three classical human *RAS* genes.

**a**, Genomic extent of *KRAS* (12p12.1), *HRAS* (11p15.5) and *NRAS* (1p13.2) on GRCh38, to scale and oriented 5′→3′; dark boxes, coding sequence; light boxes, untranslated regions; lines, introns. **b**, Exon–intron structure of each MANE Select transcript (for *KRAS*, also the MANE Plus Clinical transcript encoding KRAS4A); introns at fixed width, exons proportional to length; asterisks, truncated terminal exons; red marks, hotspot codons; transcripts (Ensembl/NCBI): KRAS4B, ENST00000311936.8/NM_004985.5; KRAS4A, ENST00000256078.10/NM_033360.4; *HRAS*, ENST00000311189.8/NM_005343.4; *NRAS*, ENST00000369535.5/NM_002524.5. Coding exons 2, 3 and 4 have identical lengths in all three genes (111, 179 and 160 bp), the basis for exon 2/3/4 reporting in clinical *RAS* testing.

## Figure 3 | Nucleotide-binding elements of KRAS and sequence divergence among the four RAS proteins.

**a**, Ray-traced cartoon of KRAS–GDP (inactive state; PDB 4OBE, chain B, 1.24 Å); green, P-loop (10–17); orange, switch I (30–38); brick red, switch II (60–76); purple, G4/NKxD (116–119) and G5/SAK (145–147); sticks, GDP; green sphere, Mg²⁺; red sticks, Gly12 (substitution blocks GAP-catalysed hydrolysis). **b**, KRAS4A, HRAS and NRAS compared with KRAS4B position by position; dark, residues differing from KRAS4B; top row, structural elements (colours as in **a**) and the HVR; relative to KRAS4B, 4–12 residues differ in the G domain (1–166) and 15–19 in the HVR (167–189). **c**, alignment of the C-terminal residues 161–189; light blue, lysine/arginine; teal, S-palmitoyl cysteine; coral, S-farnesyl cysteine; grey letters, C-terminal tripeptide removed after prenylation; dashed line, G domain–HVR boundary; numbering follows the 189-residue proteins, and KRAS4B, one residue shorter, carries a gap at position 167, so that its farnesylated cysteine is C185. Sequences from UniProt (P01116-2, P01116, P01112, P01111); lipidation sites from UniProt annotations (KRAS4B marked at its CAAX cysteine).

## Figure 4 | Correspondence between *KRAS* gene structure and KRAS4B protein architecture.

Top, the 567-bp coding sequence (stop codon included) of the *KRAS* MANE Select transcript (ENST00000311936.8 / NM_004985.5); each box gives the exon number, its coding length and the residues it encodes; pale columns, the residue span of each exon. Middle, experimentally determined secondary structure (arrows, β-strands; rounded bars, α-helices) up to residue 166. Bottom, the 188-residue KRAS4B protein (UniProt P01116-2): G-box motifs, switch regions and the hypervariable region (HVR, 167–188), named with their residue ranges beneath the bar; red arrows, oncogenic hotspot residues; bottom ruler, residue number. Residues 1–150 are shared by KRAS4A and KRAS4B, the HVR differs (sequence and lipidation sites in Figure 3c); all residue numbers refer to the 4B isoform.

## Figure 5 | Complementarity of experimental and predicted structures across the RAS polypeptide.

**a**, Per-residue confidence (pLDDT) of the full-length AlphaFold DB v6 models of KRAS, NRAS and HRAS; dashed lines, official confidence thresholds (90, 70, 50), with the tier names at right; beige bands, switch I (30–38) and switch II (60–76). **b**, Residues with interpretable electron density in nine representative crystal structures (left, PDB code, protein and resolution; right, bound nucleotide); teal bars, modelled residues; thin grey line, unmodelled residues, drawn at their true length. Grey shading, hypervariable region (HVR, 167–189): no crystal structure is modelled beyond residue 169, and the prediction confidence is low, indicating intrinsic flexibility.

## Figure 6 | Nucleotide state and covalent inhibitor binding remodel the switch regions without altering the core fold.

**a**,**b**, Per-residue Cα deviation after superposition on G-domain core residues (switch regions excluded from the fit): **a**, KRAS–GDP (PDB 4OBE) vs KRAS–GTP (5VQ2); **b**, KRAS(G12C)–GDP (4LDJ) vs the covalent KRAS(G12C)–sotorasib complex (6OIM); shaded bands, P-loop, switch I and switch II. Displacement is confined to the switch regions (GDP→GTP: switch I ≈4.0 Å, switch II ≈4.6 Å; covalent binding: switch II ≈8.9 Å); core r.m.s.d. 0.71 and 0.88 Å. **c**, Ray-traced cartoon of the 6OIM complex, colours as in **a**,**b**; sticks, GDP and sotorasib; green sphere, Mg²⁺; red, covalent attachment site Cys12.

---

## Figure 7 | Position-resolved somatic mutation spectra of *KRAS*, *NRAS* and *HRAS* in a pan-cancer cohort.

**a–c**, Lollipop plots for *KRAS* (**a**), *NRAS* (**b**) and *HRAS* (**c**) in the MSK-IMPACT cohort (10,945 tumours; cBioPortal; Zehir et al., *Nat. Med.* 2017). Stem height and dot area, samples mutated at that residue; each panel in its gene colour (as Fig. 5); diamonds, canonical hotspot codons (12, 13, 61, 117, 146); pale circles, other codons; labels, the three commonest changes at each hotspot with sample count and share; bottom bars, protein segments as in Fig. 4. Percentages count mutation records and describe the sequenced cohort, not population incidence.

## Notes on attribution and methods

1. Cite both the database and the primary publication of every PDB entry shown: 4OBE and 4LDJ (Hunter et al., *PNAS* 2014), 5VQ2 (*Acta Crystallogr. D* 2017), 6OIM (Canon et al., *Nature* 2019), 6GJ8 (Kessler et al., *PNAS* 2019), 7RPZ (Wang et al., *J. Med. Chem.* 2022), 5P21 (Pai et al., *EMBO J.* 1990), 4Q21 (Milburn et al., *Science* 1990), 1WQ1 (Scheffzek et al., *Science* 1997), 3CON (unpublished).
2. AlphaFold models must be cited as Jumper et al., *Nature* 2021 together with the AlphaFold DB publication, and the model version (v6) stated.
3. Mutation data must be attributed to cBioPortal and to the MSK-IMPACT cohort publication (Zehir et al., *Nat. Med.* 2017), with the access date.
4. The deviation values in Fig. 6a,b were computed for this work from deposited coordinates; state the superposition protocol (core-region Kabsch fit, switch regions excluded) in the Methods, and cite PyMOL for the rendering in Fig. 6c.

---

---

# Supplementary figure legends

Single-column (88 mm) molecular figures rendered with PyMOL from the deposited coordinates in `结构文件/`; colour keys are inside each panel, titles are given here. Script: `脚本/render_supplementary_pymol.pml` → `脚本/04_supplementary.py`.

## Supplementary Figure S1 | The AlphaFold model of full-length KRAS, coloured by per-residue confidence.

AlphaFold DB model AF-P01116-F1 (v6) for full-length KRAS, coloured by pLDDT using the official four-tier palette. The G domain is predicted with very high confidence (pLDDT ≥ 90, dark blue), whereas confidence falls progressively along the C-terminal hypervariable region (residues 167–188), which is modelled as an extended tail at low to very low confidence (yellow to orange). Because this segment is also absent from every deposited crystal structure (Fig. 5b), the two lines of evidence together indicate intrinsic flexibility rather than missing data; the extended conformation shown here should therefore not be interpreted as a defined structure.

## Supplementary Figure S2 | Superposition of the GDP- and GTP-bound states shows that the conformational change is confined to the switch regions.

KRAS–GDP (PDB 4OBE, chain B; cool grey) and KRAS–GTP (PDB 5VQ2, chain A; warm grey) superposed on their G-domain cores. Switch I and switch II are highlighted in teal for the GDP state and in red for the GTP state; all other regions are rendered semi-transparent. The bound nucleotides are shown as sticks and Mg²⁺ as spheres. Outside the two switch regions the two structures are indistinguishable at this scale (core-region Cα r.m.s.d. 0.71 Å, Fig. 6a), whereas switch I and switch II move by up to ~4.0 Å and ~4.6 Å respectively — the structural basis of the binary molecular switch and of conformation-selective drug design.

