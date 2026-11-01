# Data and code for the figures and tables of *RAS in malignant tumours: from oncogene to druggable target*

*(Chinese original title: 《恶性肿瘤中的 RAS：从癌基因到可成药靶点》)*

[中文说明 → README_zh.md](README_zh.md)

This repository contains everything needed to rebuild the **12 figures, 2 supplementary
figures and 3 tables** of the review from their sources: the raw database downloads, the
scripts that downloaded them, the processed data, the plotting code, the software
environment, and the final images. It does not contain the manuscript text or the
full-text articles that the review cites (they are copyrighted).

Everything is listed **in the order in which it first appears in the text** (section 3).

---

## 1. Quick start

```bash
git clone <this repository>
cd ras-review-reproducibility
pip install -r environment/requirements.txt          # Python 3.9+
Rscript environment/install_R_packages.R             # R 4.6
brew install pymol                                   # optional, macOS; see section 2
bash reproduce.sh
```

`reproduce.sh` starts from the raw downloads in `*/数据/raw/`, rebuilds every processed
data file, re-renders every figure, regenerates Table 1, and finally runs `verify.py`,
which compares the results with the committed files. On the reference machine
(section 2) the last line reads:

```
All data files and figures reproduced exactly.
```

Data, text and PNG files must be byte-identical; PDF and SVG files carry creation dates and
random IDs, so they are checked through their PNG twins. With other software versions or
another Arial font file, expect visually equivalent but not pixel-identical images.

`bash reproduce.sh --refetch` first downloads the raw data again from the live databases.
Databases are updated continuously (new trials, new PDB entries), so counts will then
differ from the published snapshot; that is expected.

## 2. Software environment

| Component | Version used | Needed for |
|---|---|---|
| Python | 3.9.6 | all data preparation; Figures 1–8, S1–S2; Table 1 |
| matplotlib / numpy / pillow | 3.9.4 / 2.0.2 / 11.3.0 | `environment/requirements.txt` |
| R | 4.6.1 | Figures 9–12 |
| R packages | ggplot2 4.0.3, dplyr 1.2.1, tidyr 1.3.2, ggtext 0.1.2, gridtext 0.1.6, ggrepel 0.9.8, patchwork 1.3.2, cowplot 1.2.0, scales 1.4.0, maps 3.4.3, svglite 2.2.2, systemfonts 1.3.2 | `environment/install_R_packages.R` installs these exact versions |
| PyMOL (open-source) | 3.1.0 | molecular renders in Figures 3, 6c, S1, S2 (optional: the renders are committed) |
| Font | Arial | all figure text; must be installed for identical output |
| OS | macOS 26.7.2, arm64 | reference machine |

The retrieval scripts use only the Python standard library. Full version list:
`environment/versions.txt`.

## 3. Figures and tables in order of appearance

The tables were written in Chinese; each has an English version in `RAS综述表格/英文版/`.
`脚本/02_tables_en.py --check` verifies, row by row, that every number in each Chinese table
also appears in its English version.

| # | First cited | Content | Data source | Plotting code |
|---|---|---|---|---|
| Figure 1 | §1.2 | Tumour-type distribution of *RAS* mutations | cBioPortal, MSK-IMPACT 2017 | Python |
| Figure 2 | §2.1 | Genomic organization of *KRAS*, *NRAS*, *HRAS* | NCBI Gene, Ensembl | Python |
| Figure 3 | §2.2 | GDP-bound KRAS with nucleotide-binding elements | RCSB PDB 4OBE | PyMOL + Python |
| Figure 4 | §2.2 | *KRAS* gene structure ↔ KRAS4B protein architecture | Ensembl, UniProt | Python |
| Supplementary Figure S1 | §2.2 | AlphaFold model of full-length KRAS by confidence | AlphaFold DB | PyMOL + Python |
| Figure 5 | §2.2 | Experimental vs predicted structure coverage | RCSB PDB, AlphaFold DB | Python |
| Supplementary Figure S2 | §2.3 | GDP- vs GTP-state superposition | RCSB PDB 4OBE, 5VQ2 | PyMOL + Python |
| Figure 6 | §2.3 | Switch-region remodelling by nucleotide and inhibitor | RCSB PDB 4OBE, 5VQ2, 4LDJ, 6OIM | Python + PyMOL |
| Figure 7 | §2.4 | Position-resolved mutation spectra of the three genes | cBioPortal, MSK-IMPACT 2017 | Python |
| Figure 8 | §3.5 | RAS signalling network and drug-intervention points | Cited literature; ClinicalTrials.gov | Python |
| Table 3 | §3.5 | Key clinical studies | Cited trial publications | hand-compiled |
| Table 2 | §4.1 | Approved drugs, indications, regulatory routes | FDA, EMA, NMPA, PMDA documents | hand-compiled |
| Figure 9 | §4.7 | Swimlane map of RAS-directed drug classes | ClinicalTrials.gov; regulatory documents | Python count + R |
| Table 1 | §4.7 | Drug landscape | Figure 9 data + cited literature | Python |
| Figure 10 | §4.7 | Sixty-year timeline of RAS biology and drugs | Cited literature; regulatory documents | R |
| Figure 11 | §4.7 | Global distribution of RAS-related oncology trials | ClinicalTrials.gov API v2 | R |
| Figure 12 | §4.7 | Resistance mechanisms and combination logics | Cited literature | R |

The file names inside the project use an older numbering; the mapping is given in each
entry below.

### Figures 1–7 and S1–S2: genes, structures and mutations — `RAS基因与蛋白结构/`

**Retrieval** (`脚本/01_fetch.py`, run on 2026-10-20; raw responses in `数据/raw/`):

| Database | What was taken | Version / identifier |
|---|---|---|
| NCBI Gene (E-utilities) | gene summaries | KRAS 3845, HRAS 3265, NRAS 4893 |
| Ensembl REST (GRCh38) | genes, transcripts, exons, MANE Select / Plus Clinical | KRAS ENST00000311936.8 (4B) and ENST00000256078.10 (4A); HRAS ENST00000311189.8; NRAS ENST00000369535.5 |
| UniProt | sequences and features | P01116 (and isoform P01116-2 = KRAS4B), P01112, P01111 |
| RCSB PDB | 12 experimental structures | 5P21, 4Q21, 1WQ1, 1NVV, 4G0N, 4OBE, 4LDJ, 5VQ2, 6OIM, 6GJ8, 7RPZ, 3CON (`结构文件/`) |
| AlphaFold DB | predicted models and pLDDT | AF-P01116-F1, AF-P01112-F1, AF-P01111-F1, model v6 |
| cBioPortal | somatic mutations in the three genes | study `msk_impact_2017`, 10 945 samples (Zehir et al., *Nat Med* 2017, PMID 28481359) |

**Processing** (`脚本/02_prepare.py`, `脚本/05_codon_share.py`) writes the tables in `数据/`:
`表1_外显子结构.csv` (exons), `表2_热点密码子定位.csv` (hotspot codons → exons),
`表3_蛋白结构特征.csv` (protein features), `表4_突变谱_MSK-IMPACT.csv` (mutations by
position), `表5_各癌种突变频率_MSK-IMPACT.csv` (mutation frequency by tumour type),
`表6_AlphaFold_pLDDT.csv`, `表6_密码子占比.csv` (hotspot share, counted per mutation record),
`表7_实验结构可见残基.csv` (residues resolved in each crystal structure), plus
`alphafold_plddt.json`, `pdb_entries.json`, `prepared_meta.json`.

**Plotting**: `脚本/03_figures.py` (main figures), `脚本/04_supplementary.py` (S1, S2),
molecular renders by `脚本/render_panelC_pymol.pml` and `脚本/render_supplementary_pymol.pml`
(written to `figures/_*.png`, then assembled). Each figure is saved as PDF (editable Arial
text), SVG and PNG in `figures/`.

| Figure | File in `figures/` | Input data |
|---|---|---|
| Figure 1 | `Fig4_cancer_type_distribution` | `表5`, `cbioportal_mutations.json`, `cbioportal_sample_cancertype.json` |
| Figure 2 | `Fig1_RAS_gene_structure` | `表1`, `表2` |
| Figure 3 | `FigS1_KRAS_GDP_structure` | PDB 4OBE → `_S1_KRAS_GDP_4OBE.png` |
| Figure 4 | `Fig2_gene_to_protein_map` | `表1`, `表3` |
| Figure 5 | `Fig5_AlphaFold_confidence_and_coverage` | `alphafold_plddt.json`, `表7`, `pdb_entries.json`, `genes_core.json` |
| Figure 6 | `Fig6_conformational_switch` | PDB 4OBE, 5VQ2, 4LDJ, 6OIM (Cα superposition computed in the script); `_panelC_6OIM.png` |
| Figure 7 | `Fig3_mutation_distribution` | `表4` |
| Supplementary Figure S1 | `FigS3_AlphaFold_pLDDT_model` | AF-P01116-F1 → `_S3_AlphaFold_pLDDT.png` |
| Supplementary Figure S2 | `FigS2_GDP_vs_GTP_superposition` | PDB 4OBE + 5VQ2 → `_S2_GDP_vs_GTP_overlay.png` |

Notes. MSK-IMPACT is a targeted-panel cohort of mostly advanced tumours, so its percentages
are frequencies *in that cohort*, not population incidence. Residue numbering follows KRAS4B
(188 aa, the MANE Select isoform); UniProt's canonical P01116 sequence is KRAS4A (189 aa).

### Figure 8: RAS signalling network — `RAS综述示意图/`

A schematic: node and arrow positions are defined in `脚本/01_fig7_network.py` (shared style
in `脚本/00_style.py`); there is no numerical input. Every node, arrow and label is backed by a
verbatim sentence from a paper cited in the review, listed in
`evidence/图8_节点与边证据.tsv` (70 rows: element, type, supporting sentence, source
document ID `<section>_<FirstAuthor>_<year>_<PMID>`, section of the text). Five rows are
marked as textbook scaffolding; three drug-status labels were counted from the
ClinicalTrials.gov corpus of Figure 11.
Output: `figures/Fig7_RAS_signalling_network.{pdf,svg,png}`.

### Table 3: key clinical studies — `RAS综述表格/表三_关键临床研究汇总表.md`

Compiled by hand from the trial publications cited in Chapter 5 of the review. Every
result cell names the section of the text where the number and its citation appear; the
notes at the end of the table record the checks made on denominators and assessment
methods. English version: `RAS综述表格/英文版/Table3_key_clinical_studies.md`.

### Table 2: approved drugs and regulatory routes — `RAS综述表格/表二_获批药物与适应证、监管路径.md`

Compiled by hand from primary regulatory documents, archived in `evidence/regulatory/`:
FDA approval letters (PDF) and approval histories, EMA EPAR overviews and the CHMP
October 2026 meeting highlights, the NMPA English-site announcement for garsorasib, the
PMDA list of approved drugs, plus plain-text extracts (`*_正文摘录.txt`) quoting the
approval date, route (accelerated or regular) and indication from each. For sosimerasib
(NMPA, 2026-02-25) only the extract is included: the archived copy came from a reprint on a
third-party news site, and the NMPA page itself could not be retrieved by script. Status as
of 2026-10-31. English version:
`RAS综述表格/英文版/Table2_approved_drugs_indications_regulatory_routes.md`.

### Figure 9: drug-class swimlanes — `RAS综述示意图/`

| File in `数据/` | Content | Origin |
|---|---|---|
| `图八_药物泳道.csv` | 59 agents: lane, code, stage, number of trials, target, regulatory status | `n_trials` and every stage below Approved **computed** from the Figure 11 corpus (highest `phase` among matched trials); approval status from `evidence/regulatory/` |
| `图八_试验命中.tsv` | the NCT IDs counted for each agent | written by `脚本/00_count_swimlane_trials.py` |
| `图八_直接RAS候选.tsv` | ledger of 61 candidate direct-RAS codes: target identity, evidence, decision | compiled from the literature and the corpus |
| `图八_等位基因覆盖.csv` | allele coverage per lane | text of the review |

`脚本/00_count_swimlane_trials.py` matches each agent's name and aliases against
`RAS临床试验注册分析/数据/表1_临床试验总表.csv` and reports any mismatch with the CSV
(`--write` writes the counts back; `--stage` checks that each stage equals the highest
`phase` among the matched trials). Plot: `脚本/02_fig8_drug_lanes.R` →
`figures/Fig8_drug_class_swimlanes.*`.

### Table 1: drug landscape — `RAS综述表格/`

Generated by `脚本/01_build_table1.py` from `图八_药物泳道.csv` (same drug set as
Figure 9) and `数据/表一_补充列.tsv` (mechanism, binding mode, representative results; each
result names the section of the text that reports it). Output: `表一_药物全景表.md`. The English
version, `英文版/Table1_RAS-directed_drug_landscape.md`, is generated by `脚本/02_tables_en.py`
from the same Figure 9 data and the English text in `数据/表一_补充列_en.tsv`. The
script imports the gene/protein typography rules from
`RAS综述原始文献/RAG/脚本/辅助/geneprotein.py`, shipped at the same relative path.

### Figure 10: sixty-year timeline — `RAS综述示意图/`

`数据/图九_大事记.csv`: 34 events (year, lane, label, detail, section of the text, source);
the 12 with `milestone = Y` are drawn on the axis, the rest are kept as documented
candidates. `数据/图九_分期.csv`: the six eras. Plot: `脚本/11_fig9_timeline.R` →
`figures/Fig9_RAS_milestones_timeline.*`.

### Figure 11: global trial landscape — `RAS临床试验注册分析/`

**Retrieval** (`脚本/01_fetch_ctgov.py`; ClinicalTrials.gov REST API v2, fetched
2026-10-20 12:26 Beijing time). Two sweeps, merged by NCT ID: (A) gene/biomarker terms
(KRAS, NRAS, HRAS, hotspot alleles, "RAS mutation", "RAS wild-type", "pan-RAS", "RAS
pathway", …) and (B) 59 RAS-directed and RAS-regulator drug names, restricted to
interventional studies. Eligibility criteria, keywords and outcome measures are searched
too. Query terms: `数据/检索词表.csv`. Raw response with per-record provenance:
`数据/raw/studies_raw.json.gz` (unpacked by `reproduce.sh`).

**Curation** (`脚本/02_curate.py`): of 3 149 interventional records, **1 133 are
included** (RAS gene or RAS-directed agent; malignant indication; Early Phase 1 to Phase
3) and 2 016 excluded, each with its reason in `表2_排除记录与原因.csv`. A bare "RAS" is
accepted only in an oncogene context, because in cardiology and nephrology it means the
renin–angiotensin system. Each trial is assigned a tier (RAS-targeted 321,
RAS-regulator-targeted 132, RAS-biomarker-selected 634, RAS-mentioned 46). Outputs:
`表1_临床试验总表.csv` (master table), `表3_国家分布.csv`, `表4`–`表12` (cross-tabulations),
`summary.json` (all headline numbers).

**Plotting**: `脚本/03_figures_country.R` → `figures/Figure_RAS_trials_global_distribution.*`
and single panels `FigurePanel_a`–`d`. `表13_国家名_地图多边形对照.csv` maps registry
country names to map polygons (Hong Kong is merged into China only on the map).

Limits: ClinicalTrials.gov only; the unit is the trial–country pair; 2026 is a partial year.

### Figure 12: resistance and combination logic — `RAS综述示意图/`

`数据/图十一_耐药机制.csv` (resistance mechanisms), `图十一_联合逻辑.csv` (combination
logics with best readouts), `图十一_矩阵.csv` and `图十一_对应.csv` (which logic answers
which mechanism), `图十一_检出率.csv` (published detection rates). Every row carries its
source and the section of the text. Plot: `脚本/04_fig11_resistance_combination.R` →
`figures/Fig11_resistance_to_combination.*`.

## 4. Repository layout

```
reproduce.sh                 rebuild everything, then verify
verify.py                    compare rebuilt files with the committed ones
environment/                 requirements.txt, install_R_packages.R, versions.txt
RAS基因与蛋白结构/           Figures 1–7, S1–S2
  数据/  数据/raw/  结构文件/  脚本/  figures/  Figure_legends.md
RAS综述示意图/               Figures 8, 9, 10, 12
  数据/  脚本/  figures/  Figure_legends.md
RAS临床试验注册分析/         Figure 11 (and the trial counts of Figures 8 and 9)
  数据/  数据/raw/  脚本/  figures/  图注_Figure_legends.md
RAS综述表格/                 Tables 1–3 (Chinese); 英文版/ holds the English versions
evidence/                    Figure 8 evidence table; regulatory documents for Table 2
RAS综述原始文献/RAG/脚本/辅助/  typography helper used by Table 1
```

Folder and file names are kept as in the project so that every script runs unchanged.
Figure legends: `Figure_legends.md` (English) and `Figure_legends_中文对照.md` (Chinese) in
each figure folder.

## 5. Licence and terms of use

**Code** (`*.py`, `*.R`, `*.sh`, `*.pml`): MIT licence — see `LICENSE`.
**Data, figures, tables and documentation**: CC BY 4.0 — see `LICENSE-DATA`.
Third-party material keeps its own terms, as set out in `LICENSE-DATA` and below.

ClinicalTrials.gov records are public-domain U.S. government data. RCSB PDB entries are
CC0. AlphaFold DB models are CC BY 4.0 (Jumper et al., *Nature* 2021; Varadi et al., *NAR*).
cBioPortal / MSK-IMPACT data are subject to the cBioPortal terms (cite Cerami et al. 2012,
Gao et al. 2013 and Zehir et al. 2017). Ensembl, UniProt and NCBI Gene data are freely
reusable with citation. FDA documents are U.S. public records; EMA, NMPA and PMDA documents
are reproduced for verification with their source named in each file. Cite the original
structures by their PDB IDs and primary publications (listed in the Figure legends).
