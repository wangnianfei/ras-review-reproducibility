# Figure legends

Prepared 20 October 2026. All panels were generated from primary database records retrieved on that date (NCBI Gene, Ensembl GRCh38, UniProt, RCSB PDB, AlphaFold DB v6, cBioPortal); no values were taken from secondary literature. Source files: `figures/Fig*.pdf` (vector, editable text), `figures/Fig*.svg` (vector, for Illustrator/Inkscape), `figures/Fig*.png` (400 dpi, preview only). Underlying numbers are in `数据/表1–表7`.

---

## Figure 1 | Tumour-type distribution of *RAS* mutations.

**a**, Fraction of samples carrying a *KRAS* mutation in each tumour type of the MSK-IMPACT cohort, with each bar partitioned by allele (G12D, G12V, G12C, G12R, G13D, any codon-61 change, and all others). **b**,**c**, The ten tumour types with the highest *NRAS* (**b**) and *HRAS* (**c**) mutation frequencies. Only tumour types with ≥40 sequenced samples are shown; numbers in parentheses are mutated samples/total samples. *KRAS* mutation frequency ranges from 74% in pancreatic cancer — the MSK category as a whole, all histologies including neuroendocrine tumours, within which 348 of 384 pancreatic ductal adenocarcinomas are mutant (90.6%) — to 2% in melanoma, and the allele spectrum is tumour-type specific — G12D and G12V predominate in pancreatic cancer, G12C is enriched in non-small-cell lung cancer, and in colorectal cancer G12D predominates, with G12V and G13D next (MSK counts 122, 87 and 76). *NRAS* mutations concentrate in melanoma and thyroid cancer and *HRAS* mutations in non-melanoma skin, bladder and salivary gland cancers, indicating that the three paralogues are not interchangeable across tissues. **Read the cohort for what it is**: MSK-IMPACT is a single-centre US cohort enriched for
advanced disease, so its share of *KRAS* G12C cannot be extrapolated to East Asian populations;
the G12C share and its denominators in East Asian and Chinese cohorts are given in section 1.2
(the LANDSCAPE and OrigiMed cohorts), and the two **cannot be compared directly** — the
denominators, the sequencing platforms and the enrolled populations all differ.

## Figure 2 | Genomic organization of the three classical human *RAS* genes.

**a**, Genomic extent of *KRAS* (12p12.1), *HRAS* (11p15.5) and *NRAS* (1p13.2) drawn to scale on GRCh38 and oriented 5′→3′ (all three genes lie on the minus strand). Dark boxes, coding sequence; light boxes, untranslated regions; horizontal lines, introns. Despite encoding proteins of near-identical length (188–189 amino acids), the loci differ ~14-fold in size (45.7, 3.3 and 12.3 kb, respectively), a difference contributed entirely by introns and untranslated exons. **b**, Exon–intron architecture of the MANE Select transcript of each gene and, for *KRAS*, of the MANE Plus Clinical transcript that encodes the KRAS4A isoform. Introns are drawn at fixed width and exons to scale in base pairs; asterisks denote terminal exons truncated for display. Exon lengths are printed beside each exon; for coding exons 2, 3 and 4, which are identical in all three genes, the length and the codons contributed are printed once beneath the shared columns. Red marks on the coding blocks give the hotspot codons, drawn only in the transcripts in which they are registered. Coding exons 2, 3 and 4 are identical in length across all three genes (111, 179 and 160 bp, encoding residues 1–37, 38–97 and 97–150), so that codons 12 and 13 always fall in exon 2, codon 61 in exon 3, and codons 117 and 146 in exon 4 — the basis of the exon 2/3/4 scheme used in clinical *RAS* testing. Divergence is confined to the last coding exon, where alternative splicing of *KRAS* exon 4 generates the 4A and 4B C termini. Transcript and RefSeq identifiers are MANE v1 matched pairs (Ensembl/NCBI). Throughout all figures, gene symbols are set in italics and protein names in roman type.

## Figure 3 | The GDP-bound state of KRAS, with the nucleotide-binding elements highlighted.

Ray-traced cartoon of KRAS in the GDP-bound (inactive) state (PDB 4OBE, chain B, 1.24 Å; waters removed). The G domain is shown in light grey with the G-box elements and switch regions coloured: P-loop (10–17) green, switch I (30–38) orange, switch II (60–76) brick red, G4/NKxD (116–119) and G5/SAK (145–147) purple. Bound GDP is drawn as sticks with heteroatoms by element, the catalytic Mg²⁺ as a green sphere, and Gly12 — the residue mutated in the majority of RAS-driven tumours — as red sticks at the mouth of the nucleotide pocket. Note that Gly12 lies at the junction of the P-loop and the nucleotide, which is the structural reason why its substitution blocks GAP-stimulated hydrolysis.

## Figure 4 | Correspondence between *KRAS* gene structure and KRAS4B protein architecture.

Top, the 567-bp coding sequence of the MANE Select transcript ENST00000311936.8/NM_004985.5, coloured by exon and annotated with the residue interval each exon encodes. Middle, experimentally determined secondary structure (arrows, β-strands; rounded bars, α-helices) taken from UniProt/PDB annotation and shown only to the end of the G domain (residue 166). Bottom, the 188-residue KRAS4B protein (UniProt P01116-2) with the G-box motifs and switch regions — G1/P-loop (10–17), switch I (30–38), G3/DxxG (57–60), switch II (60–76), G4/NKxD (116–119) and G5/SAK (145–147) — and the hypervariable region (HVR, 167–188). Red arrows indicate the oncogenic hotspot residues; the motifs are keyed by colour beneath the residue axis, and the C-terminal membrane-anchoring modifications are given in the note below. The gene and the protein are two distinct coordinate systems that can only be aligned through the exon-to-codon map shown here; note also that residues 1–150 are shared by KRAS4A and KRAS4B, whereas the HVR differs between them (KRAS4B carries the K175–K180 polybasic stretch and is farnesylated at C185, whereas KRAS4A is additionally palmitoylated at C180/C181). Because the UniProt canonical sequence for P01116 is KRAS4A (189 aa), all residue numbers here refer explicitly to isoform 4B (P01116-2).

## Figure 5 | Complementarity of experimental and predicted structures across the RAS polypeptide.

**a**, Per-residue model confidence (pLDDT) of the full-length AlphaFold DB v6 models of KRAS (AF-P01116-F1), NRAS (AF-P01111-F1) and HRAS (AF-P01112-F1); background bands indicate the official confidence categories. **b**, Residue ranges with interpretable electron density in nine representative crystal structures (PDB code, resolution and bound ligands given at left); white gaps denote internal residues not modelled. Grey shading in both panels marks the hypervariable region. The G domain (residues 1–166) is covered by high-resolution experimental structures and is predicted with very high confidence, whereas the hypervariable region is absent from every crystal structure and is predicted with low to very low confidence. The concordance of the two independent lines of evidence indicates intrinsic flexibility rather than missing data, and defines the limits within which a predicted model may legitimately be used.

## Figure 6 | Nucleotide state and covalent inhibitor binding remodel the switch regions without altering the core fold.

**a**,**b**, Per-residue Cα deviation after least-squares superposition on G-domain core residues (switch I and switch II excluded from the fit) for KRAS–GDP (PDB 4OBE) versus KRAS–GTP (5VQ2) (**a**) and for KRAS(G12C)–GDP (4LDJ) versus the KRAS(G12C)–sotorasib covalent complex (6OIM) (**b**). Shaded bands mark the P-loop, switch I and switch II. Displacement is confined almost entirely to the switch regions — peaks of ~4.0 Å (switch I) and ~4.6 Å (switch II) on GDP→GTP exchange, and ~8.9 Å in switch II upon covalent inhibitor binding — while the core region superimposes to 0.71 Å and 0.88 Å r.m.s.d., respectively. **c**, Ray-traced cartoon of the KRAS(G12C)–sotorasib complex (6OIM, chain A; waters removed), coloured as in **a**,**b**: G domain in light grey, P-loop green, switch I orange, switch II brick red, G4 and G5 purple. Bound GDP and sotorasib are drawn as sticks with heteroatoms by element, Mg²⁺ as a green sphere, and the covalent attachment site Cys12 in red. Rendered with PyMOL (orthographic projection, outline shading, shadows and depth cue off) from a scripted, reproducible camera; the sotorasib molecule occupies the switch-II pocket immediately beneath the switch II helix whose displacement is quantified in **b**.

---

## Figure 7 | Position-resolved somatic mutation spectra of *KRAS*, *NRAS* and *HRAS* in a pan-cancer cohort.

**a–c**, Lollipop plots for *KRAS* (**a**), *NRAS* (**b**) and *HRAS* (**c**) in the MSK-IMPACT clinical sequencing cohort (10,945 tumours; Zehir et al., *Nat. Med.* 2017). Each stem marks a residue; its height and marker area give the number of samples carrying a mutation at that residue; red diamonds denote the canonical hotspot codons (12, 13, 61, 117, 146) and blue circles all other codons, so that hotspots are distinguished by marker shape as well as by colour. Labels give the three most frequent amino-acid changes at a hotspot, the number of samples and the percentage of all mutations in that gene. The bar beneath each plot maps the protein regions defined in Fig. 4. Mutational pressure is extremely focal in all three genes but falls on different residues: 77% of *KRAS* mutations affect codon 12, whereas *NRAS* and *HRAS* are dominated by codon 61 (66% and 38%, respectively; all counted per mutation record — de-duplicated per patient, *HRAS* is 39%; see `脚本/05_codon_share.py`). Note that this is a targeted-panel cohort enriched for advanced disease; percentages describe the sequenced cohort and are not population incidence estimates.

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

