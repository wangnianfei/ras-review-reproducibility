#!/usr/bin/env bash
# Regenerate every processed data file, figure and generated table in this
# repository from the shipped raw downloads, then check the results against the
# committed versions (verify.py).
#
#   bash reproduce.sh            # raw downloads -> processed data -> figures -> tables -> verify
#   bash reproduce.sh --refetch  # first re-download raw data from the live APIs (see README:
#                                # databases change, so counts may differ from the snapshot)
#
# Run from the repository root. Requirements: see environment/ and README section 3.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)
step() { printf '\n== %s\n' "$*"; }

if [[ "${1:-}" == "--refetch" ]]; then
  step "Re-download raw data (network; ClinicalTrials.gov ~3 min)"
  python3 RAS基因与蛋白结构/脚本/01_fetch.py RAS基因与蛋白结构
  python3 RAS临床试验注册分析/脚本/01_fetch_ctgov.py RAS临床试验注册分析
else
  step "Unpack the ClinicalTrials.gov snapshot (2026-10-20)"
  gunzip -kf RAS临床试验注册分析/数据/raw/studies_raw.json.gz
fi

step "Figure 11 data: curate the ClinicalTrials.gov harvest (offline)"
python3 RAS临床试验注册分析/脚本/02_curate.py RAS临床试验注册分析

step "Figures 1-7, S1-S2 data: shape the database downloads"
if [[ "${1:-}" == "--refetch" ]]; then
  python3 RAS基因与蛋白结构/脚本/02_prepare.py RAS基因与蛋白结构              # also queries Ensembl/UniProt live
else
  python3 RAS基因与蛋白结构/脚本/02_prepare.py RAS基因与蛋白结构 --offline    # uses the snapshot in 数据/raw/
fi
python3 RAS基因与蛋白结构/脚本/05_codon_share.py

step "Molecular renders (PyMOL)"
if command -v pymol >/dev/null 2>&1; then
  (cd RAS基因与蛋白结构 && pymol -cq 脚本/render_panelC_pymol.pml && pymol -cq 脚本/render_supplementary_pymol.pml)
else
  echo "pymol not found: keeping the committed renders figures/_*.png"
fi

step "Figures 1-7 and S1-S2 (Python/matplotlib)"
(cd RAS基因与蛋白结构 && python3 脚本/03_figures.py . && python3 脚本/04_supplementary.py .)

step "Figure 8 (Python/matplotlib)"
(cd RAS综述示意图/脚本 && python3 01_fig7_network.py ..)

step "Figure 9: recount trials per drug from the curated corpus, then draw (R)"
(cd RAS综述示意图 && python3 脚本/00_count_swimlane_trials.py && python3 脚本/00_count_swimlane_trials.py --stage)
(cd RAS综述示意图 && Rscript 脚本/02_fig8_drug_lanes.R .)

step "Figures 10 and 12 (R)"
(cd RAS综述示意图 && Rscript 脚本/11_fig9_timeline.R . && Rscript 脚本/04_fig11_resistance_combination.R .)

step "Figure 11 (R)"
(cd RAS临床试验注册分析 && Rscript 脚本/03_figures_country.R .)

step "Table 1, Chinese and English (generated from the Figure 9 data); number check of English Tables 1-3"
(cd RAS综述表格 && python3 脚本/01_build_table1.py && python3 脚本/02_tables_en.py)

step "Compare with the committed versions"
python3 verify.py
