# 《恶性肿瘤中的 RAS：从癌基因到可成药靶点》图表的数据与代码

[English → README.md](README.md)

本仓库收齐了重建综述 **12 幅正文图、2 幅补充图与 3 张表**所需的全部材料：数据库原始下载、
下载所用的脚本、整理后的数据、作图代码、软件环境与成品图。不含稿件正文，也不含综述所引的
全文文献（有版权）。

全部条目**按在正文中首次出现的顺序**排列（见第三节）。

---

## 一、快速复现

```bash
git clone <本仓库>
cd ras-review-reproducibility
pip install -r environment/requirements.txt          # Python 3.9 及以上
Rscript environment/install_R_packages.R             # R 4.6
brew install pymol                                   # 可选，macOS；见第二节
bash reproduce.sh
```

`reproduce.sh` 从 `*/数据/raw/` 里的原始下载出发，依次重建全部整理数据、重画全部图件、重出表1，
最后运行 `verify.py` 与仓库里的版本逐一比对。在第二节所列的参考环境下，最后一行是：

```
All data files and figures reproduced exactly.
```

数据、文本与 PNG 必须逐字节一致；PDF 与 SVG 内嵌生成时间与随机编号，改由同名 PNG 比对。
换用其他软件版本或另一份 Arial 字体文件时，图应在视觉上一致，但不保证逐像素相同。

`bash reproduce.sh --refetch` 会先从线上数据库重新下载原始数据。数据库在持续更新（新登记的
试验、新的 PDB 条目），此时计数与发表时的快照不同，属正常现象。

## 二、软件环境

| 组件 | 所用版本 | 用途 |
|---|---|---|
| Python | 3.9.6 | 全部数据整理；图1–8、补充图S1–S2；表1 |
| matplotlib / numpy / pillow | 3.9.4 / 2.0.2 / 11.3.0 | `environment/requirements.txt` |
| R | 4.6.1 | 图9–12 |
| R 包 | ggplot2 4.0.3、dplyr 1.2.1、tidyr 1.3.2、ggtext 0.1.2、gridtext 0.1.6、ggrepel 0.9.8、patchwork 1.3.2、cowplot 1.2.0、scales 1.4.0、maps 3.4.3、svglite 2.2.2、systemfonts 1.3.2 | `environment/install_R_packages.R` 按上述确切版本安装 |
| PyMOL（开源版） | 3.1.0 | 图3、图6c、补充图S1、S2 的分子渲染（可选：渲染图已入库） |
| 字体 | Arial | 图内全部文字；要逐像素一致须安装 |
| 操作系统 | macOS 26.7.2，arm64 | 参考环境 |

取数脚本只用 Python 标准库。完整版本清单见 `environment/versions.txt`。

## 三、图表（按正文首次出现顺序）

三张表原文为中文，`RAS综述表格/英文版/` 下各有英文版；`脚本/02_tables_en.py --check`
逐行核对中文表里的每个数在英文版里都出现。

| 编号 | 首次出现 | 内容 | 数据来源 | 作图 |
|---|---|---|---|---|
| 图1 | 1.2 | *RAS* 突变的癌种分布 | cBioPortal，MSK-IMPACT 2017 | Python |
| 图2 | 2.1 | *KRAS*、*NRAS*、*HRAS* 的基因组结构 | NCBI Gene、Ensembl | Python |
| 图3 | 2.2 | GDP 结合态 KRAS 与核苷酸结合元件 | RCSB PDB 4OBE | PyMOL＋Python |
| 图4 | 2.2 | *KRAS* 基因结构与 KRAS4B 蛋白结构的对应 | Ensembl、UniProt | Python |
| 补充图S1 | 2.2 | 全长 KRAS 的 AlphaFold 模型（按置信度着色） | AlphaFold DB | PyMOL＋Python |
| 图5 | 2.2 | 实验结构与预测结构的覆盖互补 | RCSB PDB、AlphaFold DB | Python |
| 补充图S2 | 2.3 | GDP 态与 GTP 态叠合 | RCSB PDB 4OBE、5VQ2 | PyMOL＋Python |
| 图6 | 2.3 | 核苷酸状态与抑制剂对开关区的重塑 | RCSB PDB 4OBE、5VQ2、4LDJ、6OIM | Python＋PyMOL |
| 图7 | 2.4 | 三个基因按位置分辨的突变谱 | cBioPortal，MSK-IMPACT 2017 | Python |
| 图8 | 3.5 | RAS 信号网络与药物干预点 | 所引文献；ClinicalTrials.gov | Python |
| 表3 | 3.5 | 关键临床研究汇总 | 所引试验论文 | 人工整理 |
| 表2 | 4.1 | 获批药物、适应证与监管路径 | FDA、EMA、NMPA、PMDA 一手文件 | 人工整理 |
| 图9 | 4.7 | RAS 靶向药物分类泳道图 | ClinicalTrials.gov；监管文件 | Python 计数＋R |
| 表1 | 4.7 | 药物全景表 | 图9 数据＋所引文献 | Python |
| 图10 | 4.7 | RAS 六十年时间线 | 所引文献；监管文件 | R |
| 图11 | 4.7 | RAS 相关肿瘤临床试验的全球分布 | ClinicalTrials.gov API v2 | R |
| 图12 | 4.7 | 耐药机制与联合策略 | 所引文献 | R |

项目内的文件名沿用早期编号，与正文编号的对应写在下面各条里。

### 图1–7 与补充图S1–S2：基因、结构与突变 —— `RAS基因与蛋白结构/`

**取数**（`脚本/01_fetch.py`，2026-10-20 运行；原始返回在 `数据/raw/`）：

| 数据库 | 取了什么 | 版本／标识 |
|---|---|---|
| NCBI Gene（E-utilities） | 基因摘要 | KRAS 3845、HRAS 3265、NRAS 4893 |
| Ensembl REST（GRCh38） | 基因、转录本、外显子、MANE Select／Plus Clinical | KRAS ENST00000311936.8（4B）与 ENST00000256078.10（4A）；HRAS ENST00000311189.8；NRAS ENST00000369535.5 |
| UniProt | 序列与特征 | P01116（及异构体 P01116-2＝KRAS4B）、P01112、P01111 |
| RCSB PDB | 12 个实验结构 | 5P21、4Q21、1WQ1、1NVV、4G0N、4OBE、4LDJ、5VQ2、6OIM、6GJ8、7RPZ、3CON（`结构文件/`） |
| AlphaFold DB | 预测模型与 pLDDT | AF-P01116-F1、AF-P01112-F1、AF-P01111-F1，模型 v6 |
| cBioPortal | 三个基因的体细胞突变 | 研究 `msk_impact_2017`，10 945 例样本（Zehir 等，*Nat Med* 2017，PMID 28481359） |

**整理**（`脚本/02_prepare.py`、`脚本/05_codon_share.py`）在 `数据/` 写出：`表1_外显子结构.csv`、
`表2_热点密码子定位.csv`、`表3_蛋白结构特征.csv`、`表4_突变谱_MSK-IMPACT.csv`、
`表5_各癌种突变频率_MSK-IMPACT.csv`、`表6_AlphaFold_pLDDT.csv`、`表6_密码子占比.csv`（热点占比，
按突变记录数计）、`表7_实验结构可见残基.csv`，以及 `alphafold_plddt.json`、`pdb_entries.json`、
`prepared_meta.json`。`02_prepare.py` 加 `--offline` 时只读 `数据/raw/` 里的缓存，不联网
（`reproduce.sh` 默认如此）。

**作图**：`脚本/03_figures.py`（正文图）、`脚本/04_supplementary.py`（补充图）；分子渲染由
`脚本/render_panelC_pymol.pml` 与 `脚本/render_supplementary_pymol.pml` 生成
（写到 `figures/_*.png`，再由作图脚本装配）。每幅图在 `figures/` 下各有 PDF（Arial 活字可编辑）、
SVG 与 PNG。

| 正文编号 | `figures/` 里的文件 | 输入数据 |
|---|---|---|
| 图1 | `Fig4_cancer_type_distribution` | `表5`、`cbioportal_mutations.json`、`cbioportal_sample_cancertype.json` |
| 图2 | `Fig1_RAS_gene_structure` | `表1`、`表2` |
| 图3 | `FigS1_KRAS_GDP_structure` | PDB 4OBE → `_S1_KRAS_GDP_4OBE.png` |
| 图4 | `Fig2_gene_to_protein_map` | `表1`、`表3` |
| 图5 | `Fig5_AlphaFold_confidence_and_coverage` | `alphafold_plddt.json`、`表7`、`pdb_entries.json`、`genes_core.json` |
| 图6 | `Fig6_conformational_switch` | PDB 4OBE、5VQ2、4LDJ、6OIM（Cα 叠合在脚本内计算）；`_panelC_6OIM.png` |
| 图7 | `Fig3_mutation_distribution` | `表4` |
| 补充图S1 | `FigS3_AlphaFold_pLDDT_model` | AF-P01116-F1 → `_S3_AlphaFold_pLDDT.png` |
| 补充图S2 | `FigS2_GDP_vs_GTP_superposition` | PDB 4OBE＋5VQ2 → `_S2_GDP_vs_GTP_overlay.png` |

说明：MSK-IMPACT 是以晚期肿瘤为主的靶向 panel 队列，百分比是「该队列中」的频率，不是人群发病率。
残基编号按 KRAS4B（188 aa，MANE Select 异构体）；UniProt 的规范序列 P01116 是 KRAS4A（189 aa）。

### 图8：RAS 信号网络 —— `RAS综述示意图/`

示意图：节点与箭头的位置写在 `脚本/01_fig7_network.py` 里（统一样式见 `脚本/00_style.py`），没有数值输入。
每个节点、箭头与标签都有综述所引文献中的一句原文作支撑，列在 `evidence/图8_节点与边证据.tsv`
（70 行：元素、类型、支撑原文句、文献编号 `<节>_<第一作者>_<年>_<PMID>`、所在正文节）。
其中 5 行标为教科书骨架；3 个药物状态标签由图11 的试验语料实测。
成品：`figures/Fig7_RAS_signalling_network.{pdf,svg,png}`。

### 表3：关键临床研究汇总 —— `RAS综述表格/表三_关键临床研究汇总表.md`

据第五章所引试验论文人工整理。每个结果格都写明该数字及其引文所在的正文节；表末附注记录了对分母
与评价方式所做的核对。英文版：`RAS综述表格/英文版/Table3_key_clinical_studies.md`。

### 表2：获批药物与监管路径 —— `RAS综述表格/表二_获批药物与适应证、监管路径.md`

据一手监管文件人工整理，文件存于 `evidence/regulatory/`：FDA 批准函（PDF）与审批历史、
EMA 的 EPAR 概览与 CHMP 2026 年 10 月会议纪要、NMPA 英文站关于 garsorasib 的公告、PMDA 获批药品
清单，以及逐件摘录批准日、路径（加速／常规）与适应证原文的 `*_正文摘录.txt`。sosimerasib
（NMPA，2026-02-25）只收摘录：存档件来自第三方新闻网站的转载，NMPA 原页无法用脚本取回。
状态截至 2026-10-31。英文版：
`RAS综述表格/英文版/Table2_approved_drugs_indications_regulatory_routes.md`。

### 图9：药物分类泳道图 —— `RAS综述示意图/`

| `数据/` 里的文件 | 内容 | 来源 |
|---|---|---|
| `图八_药物泳道.csv` | 59 个药：泳道、代号、阶段、试验数、靶点、监管状态 | `n_trials` 与「已获批」以外的阶段由图11 语料**计算**（命中试验里 `phase` 的最高值）；获批状态见 `evidence/regulatory/` |
| `图八_试验命中.tsv` | 每个药计入的 NCT 号 | 由 `脚本/00_count_swimlane_trials.py` 写出 |
| `图八_直接RAS候选.tsv` | 61 个直接 RAS 候选代号的核查台账：靶点身份、证据、判定 | 据文献与语料整理 |
| `图八_等位基因覆盖.csv` | 各泳道覆盖的等位基因 | 综述正文 |

`脚本/00_count_swimlane_trials.py` 用每个药的名称与别名匹配
`RAS临床试验注册分析/数据/表1_临床试验总表.csv`，与 CSV 不符即报错（`--write` 写回计数；
`--stage` 核对阶段是否等于命中试验 `phase` 的最高值）。作图：`脚本/02_fig8_drug_lanes.R` →
`figures/Fig8_drug_class_swimlanes.*`。

### 表1：药物全景表 —— `RAS综述表格/`

由 `脚本/01_build_table1.py` 从 `图八_药物泳道.csv`（与图9 同一药物集合）和 `数据/表一_补充列.tsv`
（机制、结合方式、代表结果；每条结果标明报告它的正文节）生成 `表一_药物全景表.md`。英文版
`英文版/Table1_RAS-directed_drug_landscape.md` 由 `脚本/02_tables_en.py` 从同一份图9 数据与
`数据/表一_补充列_en.tsv` 的英文文字生成。脚本调用的
基因／蛋白写法规则 `RAS综述原始文献/RAG/脚本/辅助/geneprotein.py` 按原相对路径随包提供。
本仓库里的表与图注已用 `RAS综述原始文献/RAG/脚本/辅助/traces.py`（与稿件同一套规则）剥去项目内部的
工作记录（裁定日期、本地存档路径、修订日志，以及整段都是裁定记录的几条表注），随后重排表注编号并改全部
指向；`RAS综述表格/数据/表注重排.tsv` 记录新旧附注号，`reproduce.sh` 重出表1 后据此再剥一次再复核。

### 图10：六十年时间线 —— `RAS综述示意图/`

`数据/图九_大事记.csv`：34 个事件（年份、泳道、标签、说明、正文节、出处），`milestone = Y` 的 12 个
上轴，其余作为有据可查的候选保留。`数据/图九_分期.csv`：六个时期。作图：`脚本/11_fig9_timeline.R` →
`figures/Fig9_RAS_milestones_timeline.*`。

### 图11：全球临床试验分布 —— `RAS临床试验注册分析/`

**取数**（`脚本/01_fetch_ctgov.py`；ClinicalTrials.gov REST API v2，2026-10-20 12:26 北京时间抓取）。
两路检索按 NCT 号取并集：A 路为基因／生物标志物词（KRAS、NRAS、HRAS、热点等位基因、
"RAS mutation"、"RAS wild-type"、"pan-RAS"、"RAS pathway" 等），B 路为 59 个 RAS 靶向与 RAS
调控节点药名，均限于干预性研究；入排标准、关键词与结局指标一并检索。检索词见 `数据/检索词表.csv`；
带逐条检索溯源的原始返回为 `数据/raw/studies_raw.json.gz`（由 `reproduce.sh` 解压）。

**整理**（`脚本/02_curate.py`）：3 149 条干预性记录中**纳入 1 133 项**（出现 RAS 基因或 RAS 靶向药、
适应证为恶性肿瘤、分期为 Early Phase 1 至 Phase 3），排除 2 016 项，每项排除理由写在
`表2_排除记录与原因.csv`。裸写的「RAS」只在癌基因语境下采信，因为在心肾领域它指肾素—血管紧张素
系统。每项试验分层：RAS-targeted 321、RAS-regulator-targeted 132、RAS-biomarker-selected 634、
RAS-mentioned 46。产物：`表1_临床试验总表.csv`（主表）、`表3_国家分布.csv`、`表4`–`表12`（交叉计数）、
`summary.json`（全部口径数字）。

**作图**：`脚本/03_figures_country.R` → `figures/Figure_RAS_trials_global_distribution.*` 及单面板
`FigurePanel_a`–`d`。`表13_国家名_地图多边形对照.csv` 是注册库国名到地图多边形的对照（香港只在地图上
并入中国）。

局限：只覆盖 ClinicalTrials.gov；统计单位是「试验—国家对」；2026 年为不完整年份。

### 图12：耐药与联合策略 —— `RAS综述示意图/`

`数据/图十一_耐药机制.csv`（耐药机制）、`图十一_联合逻辑.csv`（联合策略及最佳读数）、
`图十一_矩阵.csv` 与 `图十一_对应.csv`（哪种策略回应哪种机制）、`图十一_检出率.csv`（已发表的检出率）。
每行都带出处与正文节。作图：`脚本/04_fig11_resistance_combination.R` →
`figures/Fig11_resistance_to_combination.*`。

## 四、目录结构

```
reproduce.sh                 全部重建并核对
verify.py                    重建结果与仓库版本比对
environment/                 requirements.txt、install_R_packages.R、versions.txt
RAS基因与蛋白结构/           图1–7、补充图S1–S2
  数据/  数据/raw/  结构文件/  脚本/  figures/  Figure_legends.md
RAS综述示意图/               图8、9、10、12
  数据/  脚本/  figures/  Figure_legends.md
RAS临床试验注册分析/         图11（及图8、图9 的试验计数）
  数据/  数据/raw/  脚本/  figures/  图注_Figure_legends.md
RAS综述表格/                 表1–3（中文）；英文版/ 下为英文版
evidence/                    图8 证据表；表2 的监管文件
RAS综述原始文献/RAG/脚本/辅助/  表1 用到的写法判定与痕迹剥离规则
```

目录名与文件名保持与项目一致，脚本无需修改即可运行。各图目录下有英文图注 `Figure_legends.md`
与中文对照 `Figure_legends_中文对照.md`。

## 五、许可证与使用条款

**代码**（`*.py`、`*.R`、`*.sh`、`*.pml`）：MIT 许可证，见 `LICENSE`。
**数据、图件、表格与文档**：CC BY 4.0，见 `LICENSE-DATA`。
第三方材料仍按其自身条款，见 `LICENSE-DATA` 与下文。

ClinicalTrials.gov 记录属美国政府公有领域数据；RCSB PDB 条目为 CC0；AlphaFold DB 模型为 CC BY 4.0
（Jumper 等，*Nature* 2021；Varadi 等，*NAR*）；cBioPortal／MSK-IMPACT 数据遵循 cBioPortal 条款
（引用 Cerami 等 2012、Gao 等 2013 与 Zehir 等 2017）；Ensembl、UniProt、NCBI Gene 注明出处即可复用。
FDA 文件属美国公共记录；EMA、NMPA、PMDA 文件为核对之用收录，每份文件内写明来源。引用结构时请按
PDB 编号及其原始论文引用（见各图注）。
