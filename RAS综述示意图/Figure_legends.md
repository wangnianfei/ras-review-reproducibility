# Figure legends (schematic figures of the review)

Prepared 20 October 2026 (Figures 9 and 12 redrawn as a swimlane map and a matrix
heatmap on 30 October 2026). These figures are schematics and carry no measured
quantities of their own: Figure 9 carries only trial counts (the right-hand track),
Figure 12 only the two published detection rates, and Figure 10 only years. The trial
counts come from the
ClinicalTrials.gov corpus assembled for this review (REST API v2, snapshot of
20 October 2026; 1 133 RAS-related interventional oncology trials; see
`RAS临床试验注册分析`). Regulatory status was checked against the
approving agencies' own announcements. Source files: `figures/Fig*.pdf` (vector,
editable text), `figures/Fig*.svg` (vector, text kept as text), `figures/Fig*.png`
(400 dpi, preview only). Style is identical to Figures 1–6 of the review: English
only inside the artwork, no title in the artwork, gene symbols italic and protein
names roman, categories separated by marker shape before colour.

---

## Figure 8 | The RAS signalling network: inputs, the nucleotide switch, effector branches and the points at which it can be drugged.

**a**, Signal flow from the cell surface to the effector branches. Receptor tyrosine
kinases, integrins, G-protein-coupled receptors and antigen receptors converge, through
the GRB2–SOS1 adaptor–exchange-factor axis and the tissue-restricted exchange factors, on a single nucleotide switch; SHP2 maintains assembly of that axis and
the GAPs NF1 and RASA1 drive the return reaction. Oncogenic substitutions at codons 12,
13 and 61 impair GAP-stimulated hydrolysis, so the switch accumulates in the GTP-bound
state, and the residual nucleotide cycling left to each allele determines which drug
class can act on it. Active RAS engages four effector branches — RAF–MEK–ERK,
PI3K–AKT–mTOR, RALGDS–RAL, and PLCε/TIAM1–RAC — whose relative use differs by
allele and by tissue. The dashed red line is the ERK-mediated negative feedback on SOS1,
*CRAF* and the receptors; its release on pathway inhibition is the mechanistic origin of
adaptive resistance. Tags name the drug class acting at each layer, and the marker shape
gives how far that class has reached: circle, at least one approved drug; square, in
clinical trials (phase 1–3); triangle, preclinical only or clinically tested and
abandoned. RAF and MEK inhibitors and PI3K/AKT/mTOR inhibitors are approved classes
in other indications; ERK inhibitors have no approved drug and remain in clinical
trials (square). In *RAS*-mutant tumours single-agent benefit from these classes is
limited: SELECT-1 was negative in *KRAS*-mutant non-small-cell lung cancer, and NEMO
showed only a small PFS improvement in *NRAS*-mutant melanoma (2.8 versus 1.5 months,
HR 0.62, no OS difference; as in Table 3), and neither led to approval in a
*RAS*-defined indication.
**b**, The cellular programmes that sustained RAS signalling installs — metabolic
reprogramming, macropinocytosis and autophagy, an immunosuppressive microenvironment,
and the senescence/oncogenic-stress barrier — each with the therapeutic hook, if any,
that has been derived from it. The last panel states a constraint rather than a target:
carrying a *RAS* mutation is not the same as depending on it.

## Figure 9 | Swimlane map of RAS-directed drug classes: mechanism, development stage and allele coverage.

**a**, Agents are grouped into six mechanistic lanes (a lane is the horizontal track of a
swimmer plot; Table 1 numbers the same six as groups, in the same order) — OFF-state
covalent inhibitors;
non-covalent or reversible inhibitors of non-cysteine alleles; RAS(ON) tri-complex
inhibitors built on a cyclophilin A molecular glue; degraders and other direct
modalities; upstream-node and immune strategies; and, on a lane of its own, a
downstream pathway combination that does not bind RAS at all. Each agent is drawn as a
horizontal bar that starts at preclinical development and ends at the highest stage it
has reached in the 1 133-trial ClinicalTrials.gov corpus, read from the phase field each
registration reports (Phase 1/Phase 2 counts as phase 1/2, not as phase 2); the marker at the end of the
bar gives the highest status reached at that stage — filled diamond, at least one
regulatory approval; open circle, in clinical trials; triangle, preclinical only. The
numbers on the right-hand track are how many of those trials list that agent, so they
measure registered development activity, not efficacy.

**What the map includes.** Lanes 1–4 (agents that act on RAS itself: inhibitors, molecular glues
and degraders) are meant to be complete: every agent in the corpus that has a registered trial and
whose identity as a direct RAS inhibitor, degrader or molecular glue can be documented is accounted
for, either on the map or in `数据/图八_直接RAS候选.tsv`. An agent is drawn only if the corpus
records a stage of phase 1/2 or higher, or if the library holds a published clinical readout; the
remaining 28 agents are listed in that file (25 are phase 1 only, or appear only in review
tables and have no trial in the corpus, with no published readout; LY3499446 is registered in
the corpus as phase 2 but was discontinued; and 2, HRS-2329 and RNK08954, have no modality
recorded and no clinical readout, so they are listed but not drawn),
and 12 further codes whose target identity could not be verified are kept in the same file but are
neither drawn nor counted. Lanes 5 and 6 remain representative selections, not complete sets. **How completeness is checked
(from 31 October 2026)**: lanes 1-4 are swept exhaustively in two directions — (i) every intervention
name in the 1 133-trial corpus is split out, chemotherapy, antibodies, checkpoint inhibitors, vaccines
and known MEK/*EGFR*/SHP2/SOS1 agents are removed, and each remaining code is searched for an
identity sentence in all 518 documents of the library; (ii) the drug tables of three reviews in the
library (Ebright et al. 2025 Table 1, Wu et al. 2026 and Riedl et al. 2026) are read row by row for
codes and targets and checked against the corpus. Both directions are re-runnable through
`RAS综述示意图/脚本/05_scan_direct_ras_candidates.py`; the corpus `target_class` field is no longer
used, because it classifies direct RAS agents such as FMC-376, HYP-2090PTSA and BEBT-607 as
Not RAS-directed. Lane
assignment follows the mechanism recorded in the corpus; for the G12C agents whose conformational
state and chemistry are not stated there (HS-10370, YL-15293, GEC255), the allele they target is used
to place them in lane 1, as noted row by row in the candidate file. pan-*KRAS* and pan-RAS inhibitors
are always drawn in lane 4 (LY4066434, BGB-53038, ERAS-4001, JAB-23E73 and ZG2001 sit together),
whatever their chemistry, so that lane 2 holds only non-covalent or reversible agents defined
against a single allele. The filled diamonds are
sotorasib (FDA 2021), adagrasib (FDA 2022), fulzerasib (NMPA August 2024), garsorasib
(NMPA November 2024), glecirasib (NMPA May 2025) and sosimerasib (HBI-2438/JMKX001899,
NMPA February 2026, conditional approval), all six for *KRAS* G12C-mutant non-small-cell
lung cancer; sosimerasib was approved on a single-arm phase 2 study (145 patients, ORR
52.4%), and because the library papers predate the approval the bar still stops at phase 3
while the tip carries a filled diamond; GH35 is a different molecule and is not counted
here; daraxonrasib (FDA, 26 August 2026) for
previously treated metastatic pancreatic adenocarcinoma — the first approval in the
RAS(ON) multi-selective lane; and avutometinib with defactinib (FDA, 8 May 2025) for
*KRAS*-mutant recurrent low-grade serous ovarian cancer after prior systemic therapy,
drawn in the sixth lane, **not in the upstream-and-immune lane**, because it is **not a
RAS-binding agent**: avutometinib is a RAF/MEK clamp and defactinib a FAK inhibitor, and
the entry is made because the indication rather than the mechanism is defined by a
*KRAS* mutation. The vertical asymmetry of the map is no longer a one-lane story:
approvals now sit in three of the six lanes (OFF-state covalent, RAS(ON) tri-complex and
the downstream-combination lane), and they are no longer confined to a single allele —
daraxonrasib requires no detected mutation and the avutometinib combination any *KRAS*
mutation — yet only two of those three lanes (1 and 3) hold approved agents that bind
RAS itself, allele-specific approval is still confined to G12C, and the lanes that
address G12D, G12V and *NRAS*/*HRAS* remain in phase 1 to phase 3.
**b**, Alleles that each lane actually covers. Dark squares, covered by a clinical-stage
agent of that lane; pale squares, partial or early coverage (preclinical only, or a
single agent); open squares, not covered. The sixth lane is read from its indication
rather than from binding: the FDA indication requires any *KRAS* mutation and no
particular allele, so the five *KRAS* alleles are fully covered; wild-type RAS is only
partly covered, since the *KRAS* wild-type cohort of RAMP 201 responded at 17% against
44% in the *KRAS*-mutant cohort; and *NRAS* and *HRAS* are not covered, as no clinical
data in this corpus address the combination in *NRAS*- or *HRAS*-mutant tumours. *KRAS* G12C is
reached by five of the six lanes (1, 3, 4, 5 and 6); lane 2, which admits single-allele
agents only, covers G12D (dark) and G12V and G13D (pale) but not G12C, its two
pan-*KRAS* inhibitors (JAB-23E73, ZG2001) having been placed in lane 4 by target class;
whereas *NRAS* and *HRAS* are reached only by the multi-selective and upstream
strategies, the Q61 alleles also by the downstream-combination lane — and coverage of
wild-type RAS, which the multi-selective lane necessarily
entails, is the source of its on-target toxicity and therefore of its therapeutic-window
problem.

## Figure 10 | Sixty years of RAS: a two-lane timeline of the biology and of the drugs.

Two lanes share one axis. Above it are the milestones of RAS biology and structure;
below it, drug development and regulatory decisions. **The axis is ordinal**: every year
that carries a milestone gets one slot and the slots are equally spaced, so that no label
is crowded by its neighbour - the pitch of the slots counts events and does not measure
time. The strip at the top is the same twelve milestones drawn at **true scale, 2.28 mm
per year**; it is the only linear encoding in the figure and the place to read density.
Set against each other, the two encodings carry the quantitative claim of section 4.7,
that the intervals between stages shrink: 18 years from 1964 to 1982, 31 from 1982 to
2013, and 8 from 2013 to 2021.

Every circular node is a publication cited in the review text, and the data file records
the section that cites it. The diamond at 2013 is the pivot, the switch-II pocket, a
pocket where none was thought to exist. Filled squares are regulatory approvals - agency
records rather than papers - and are deliberately drawn with a different marker, so that
no reader takes an approval for a finding. **Only positive milestones are plotted**:
twelve of the thirty-three candidates in the data file. Negative results are not drawn - the
2004 phase 3 trial of an FTI with gemcitabine, the 2004 CI-1040 study, the trametinib
replication of 2015, SELECT-1 in 2017, and the withdrawal on 1 September 2026 of the
adagrasib plus cetuximab colorectal indication (section 5.2 and Table 2, note 6) - and
remain documented in sections 4.1 and 5.2, in Table 2 and in the data file. The
consequence is intended and visible: **the lower lane holds no node before 2021**. It
records what was approved, not what was tried; for three decades the field tried indirect
routes and failed.

The six stages I to VI are **the review's own staging of this history**, not a
periodisation taken from any single source. The rail beneath the axis names them, and its
segments are as wide as the number of milestones in each stage rather than as wide as the
stage in years; the true spans are 18, 8, 23, 8, 5 and 1 years. I, viral oncogenes
(1964-1982); II, the human oncogene and the point mutation (1982-1990); III,
"undruggable", and the three indirect routes tried in the meantime - blocking membrane
anchoring, inhibiting downstream kinases, synthetic lethality (1990-2013); IV, structure
first (2013-2021); V, one allele and one state (2021-2026); VI, beyond one allele (2026-).

## Figure 12 | What resistance is made of, and what each combination logic answers.

**a**, The two directions of the correspondence are laid out as a matrix. Rows are the
resistance classes: the four of section 6.3 that a sequencer can read — receptor-level
bypass, downstream MAPK nodes, parallel chains, cell state and lineage exit — followed by
the four carriers of section 6.4 that it cannot — proteostasis (how much protein is
left), polarity and cytoskeleton (where it goes), signalling condensates (how it is
organised locally) and metabolic reprogramming (whether the membrane still holds it, and
how the cell makes energy). Columns are the five combination logics of section 6.5. A
dark square means that logic answers the mechanism directly; a pale square, only in part
(the weight of PI3K-AKT versus YAP1/TAZ is disputed between two studies); an open square
means it does not answer it. The text inside a square is the node that logic has to hit,
and each column head gives the best clinical readout available for that logic and its
source. **The empty cells are themselves the conclusion**: six of the nine classes map
only onto logic 4, state and stress; logic 3, immunotherapy, answers no single class; and
logic 5, cytotoxic combination, is off the RAS-signalling axis altogether. Which square
is filled is this review's judgement, and a square is filled only where the prose states
the correspondence.
**b**, The single quantity this figure is allowed to carry: how often an acquired
alteration is found at all. The two published rates are shown with their own
denominators because they share none — 45% (17 of 38) in a cohort sampled by tissue
and/or plasma ctDNA (ctDNA was available for 32 of the 38 and tissue for 10), mostly
non-small-cell lung cancer, on monotherapy; and 74% (25 of 34) in paired plasma ctDNA, in
colorectal cancer, on a doublet. Neither is a general detection rate and the gap between
them is not a trend, nor is it a tissue-versus-plasma contrast: the axis title states that
the two denominators do not convert into each other. On the 45% side the arithmetic
complement is the point: in that cohort more than half the patients had no attributable
acquired alteration at all.

---

## Notes for the figure captions in the final manuscript

1. Figure 8 is a synthesis schematic: every node and every feedback arrow must be
   supported by the primary references cited in review sections 3.1–3.5, and the caption
   in the manuscript should cite them rather than a review.
2. The drug-class tags in Figure 8 and the lanes in Figure 9 must stay consistent with
   the four-dimensional classification of section 4.7 (gene — allele range —
   conformational state — mechanism) and with the master drug table; no agent may appear
   in a figure and be missing from the table.
3. Trial counts in Figure 9 are reproducible from
   `RAS临床试验注册分析/数据/表1_临床试验总表.csv`; state the snapshot date
   (20 October 2026) wherever they are quoted, and note that 2026 is an incomplete year.
4. An agent's bar ends at the highest stage it has reached in that corpus, and the
   marker at its end gives the highest status reached at that stage; a drug tested only
   inside a combination trial is counted for that trial as well, so the counts are
   activity measures and are not mutually exclusive.
5. Regulatory statements must be rechecked at proof stage: this field changes within
   months, and the figure is explicitly dated.
6. Figure 10's six stages are an induction by this review and must be presented as such;
   its stage rail beneath the axis is a label for those stages, not a band scaled in years
   (the true-scale strip at the top carries the years). Only positive milestones are
   plotted - negative results stay in the text and in the data file, where the full
   candidate list with the citing section for every node is kept.
7. Figure 12 departs from the original plan in two ways, both recorded in appendix
   three of the outline: the combination logics number **five**, not four
   (section 6.5 gained a fifth in the course of writing), and the matrix is not the
   composition pie first sketched. No study in the corpus reports a ctDNA
   resistance-mechanism composition for KRAS inhibitors, and section 6.3 forbids
   reading either published detection rate as a universal one; a pie would have
   required numbers nobody published. Which square is filled is the review's own
   judgement and tracks the prose paragraph by paragraph.
8. Figures 9, 11 and 12 contain no Chinese and no figure title, in the same style as
   Figures 7 and 8; gene symbols are italic and protein names roman.
