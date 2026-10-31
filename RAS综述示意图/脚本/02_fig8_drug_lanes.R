#!/usr/bin/env Rscript
# 图9（图件基名 Fig8_drug_class_swimlanes）：RAS 靶向药物分类泳道图
# 版本沿革：原图为「药名方块按阶段列摆放」的格子图，本脚本改为泳道图语法（v2 定稿）。
#
# 现在的图是「药名方块按阶段列摆放」的格子图：读者能看出某药在哪一列，
# 但看不出**它走了多远**，也看不出各条泳道的推进速度差——图上每一条泳道的长度
# 全由最长那行的药名决定，纵向不对称这个要点反而被格子吃掉了。
#
# 这一版按泳道图（swimmer plot）的语法重排：每味药一条横杠，从 0（临床前）
# 一直画到它到达的最高阶段；末端一个事件标记表示「获批／临床／仅临床前」；
# 右侧接两条注释轨（该药登记的试验数、覆盖的等位基因），是泳道图的常规做法。
# 结构与顶刊美图社第 028 期「泳道图」一致：横杠＝个体轨迹、实心/空心标记＝事件、
# 侧边注释轨＝个体属性、图例单独排在留白处。代码按本稿数据重写，未取该期源码
# （本机只有该库的标题与简介，没有模板 R 代码）。
#
# 数据：数据/图八_药物泳道.csv（47 药 × 6 泳道，n_trials 来自 1 133 项试验语料）
#       泳道数由数据现取（从 2026-10-31 起 avutometinib＋defactinib 单列泳道 6，
#       作者裁定：它作用在 RAS 下游与平行链，不属「上游与免疫」）
# 用法：Rscript 02_fig8_drug_lanes.R <示意图项目根>
suppressPackageStartupMessages({
  library(ggplot2); library(patchwork); library(cowplot); library(grid)
library(dplyr); library(scales); library(tidyr)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")
dir.create(OUT, showWarnings = FALSE)
mm <- function(x) x / 25.4

# 泳道名只放短名进条带；机制解释在正文与图注里，条带塞三行会把行高吃掉
LANE <- c(`1` = "1  OFF-state covalent", `2` = "2  Non-covalent / reversible",
          `3` = "3  RAS(ON) tri-complex", `4` = "4  Degraders and other modalities",
          `5` = "5  Upstream and immune",
          `6` = "6  Downstream pathway combination")
LANE_COL <- c(`1` = "#1F5C8B", `2` = "#1C7C54", `3` = "#C0392B",
              `4` = "#6A4C93", `5` = "#A0522D", `6` = "#5E6B78")
# 等距摆：阶段是序数，不是等距量，按 1／1.5 的算术语义摆会让 Ph1 与 Ph1/2 的刻度打架
STAGE_X <- c("Preclinical" = 0, "Phase 1" = 1, "Phase 1/2" = 2,
             "Phase 2" = 3, "Phase 3" = 4, "Approved" = 5)
STATUS <- c(Approved = "Approved", `Phase 3` = "In clinical trials",
            `Phase 2` = "In clinical trials", `Phase 1/2` = "In clinical trials",
            `Phase 1` = "In clinical trials", Preclinical = "Preclinical only")
SHAPE <- c("Approved" = 23, "In clinical trials" = 21, "Preclinical only" = 24)

# 右侧目标栏的缩写：全称按药名逐条写过一次，改成缩写后三栏的 gutter 才拉得平。
# 展开写在图注里（"G12C = KRAS G12C" 等），不再靠读者猜。
TGT <- c(
  "KRAS G12C" = "KRAS G12C", "KRAS G12D" = "KRAS G12D",
  "KRAS G12V (OFF)" = "G12V (OFF)", "KRAS G12D (ON)" = "G12D (ON)",
  "KRAS G12C (ON)" = "G12C (ON)", "KRAS G12V (ON)" = "G12V (ON)",
  "multi-selective RAS(ON)" = "multi (ON)", "pan-KRAS" = "pan-KRAS",
  "pan-RAS" = "pan-RAS", "KRAS G12C (ON/OFF)" = "G12C (ON/OFF)",
  "KRAS G12D degrader" = "G12D degrader", "KRAS G12D mRNA/siRNA" = "G12D siRNA",
  "SHP2" = "SHP2", "SOS1" = "SOS1",
  "farnesyl transferase (HRAS)" = "FTase (HRAS)",
  "mutant-RAS peptide vaccine" = "peptide vaccine",
  "mutant-RAS whole-yeast vaccine" = "yeast vaccine",
  "mutant-KRAS mRNA vaccine" = "mRNA vaccine",
  "adoptive T-cell therapy" = "TCR-T")

d <- read.csv(file.path(DATA, "图八_药物泳道.csv"), check.names = FALSE)
# 泳道数不写死：数据里出现几条就画几条（新增或撤掉一条泳道时改 CSV 即可）
LANE_LVL <- sort(unique(as.integer(d$lane)))
stopifnot(length(LANE_LVL) > 0,
          all(as.character(LANE_LVL) %in% names(LANE)),
          all(as.character(LANE_LVL) %in% names(LANE_COL)))
d <- d %>%
  mutate(lane = factor(lane, levels = LANE_LVL),
         x = unname(STAGE_X[stage]),
         status = unname(STATUS[stage]),
         status = factor(status, levels = names(SHAPE)),
         n_trials = as.integer(n_trials),
         target = ifelse(target %in% names(TGT), TGT[target], target),
         # 临床前的药停在 0，横杠长度为零看不见；给一个最小可见长度
         x = pmax(x, 0.08),
         # 泳道内按到达阶段、再按试验数排序：获批的在上，临床前的在下
         # 行标签把两件事一次说完：药名（＋在研代号）＋它打的目标。
         # 目标不再单开一栏——多一栏就多一条要对齐的边界，而这列文字宽度参差，
         # 一栏宽了整幅图的 gutter 就跟着不齐。
         # code 列可写多个代号（用「;」分隔，见 00_count_swimlane_trials.py 的出处注），
         # 图里显示成「HBI-2438/JMKX001899」
         code = gsub(";\\s*", "/", code),
         lab = sprintf("%s%s · %s", drug,
                       ifelse(code == "", "", paste0(" (", code, ")")), target),
         drug = reorder(lab, x * 100 + n_trials))

# ---- 基因符号斜体：用 plotmath，不用 ggtext ----------------------------------
# 为什么不用 ggtext 的 markdown：在这个脚本里 `*KRAS*  G12C` 的空格被吃掉，
# 排成 `KRASG12C` 且与后文重叠（量宽用的是临时设备，字体库不同就会算错）。
# plotmath 是 base R，字宽由同一设备自己算，没有这个问题；字体仍是 Arial。
# 判据：等位基因（KRAS G12C）与括号里的基因（farnesyl transferase (HRAS)）斜体；
# pan-KRAS、RAS(ON)、SHP2、SOS1 指蛋白，保持正体。
shq <- function(x) if (nchar(x)) sprintf("'%s'", gsub("'", "\\\\'", x)) else ""
pm_expr <- function(s) {
  pat <- "(\\b(?:KRAS|NRAS|HRAS)\\b(?=\\s*\\(?[GQ])|(?<=\\()(?:KRAS|NRAS|HRAS)(?=\\)))"
  out <- ""; rest <- s
  repeat {
    m <- regexpr(pat, rest, perl = TRUE)
    if (m[1] == -1L) break
    st <- as.integer(m[1]); ln <- attr(m, "match.length")
    pre <- substr(rest, 1L, st - 1L)
    out <- paste0(out, if (nzchar(pre)) paste0(shq(pre), "*"),
                  "italic(", substr(rest, st, st + ln - 1L), ")*")
    rest <- substr(rest, st + ln, nchar(rest))
  }
  out <- paste0(out, shq(rest))
  sub("\\*+$", "", out)
}
LAB_EXPR <- setNames(vapply(d$lab, pm_expr, ""), d$lab)

stage_lab <- c("Preclin.", "Ph 1", "Ph 1/2", "Ph 2", "Ph 3", "Approved")

# 底部留白与网格：去刻度、y 主网格、x 次网格（版面与既定样式一致）。
base_theme <- theme_bw(base_family = "Arial", base_size = 7) +
  theme(
    axis.ticks = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(linewidth = 0.2, colour = "grey90"),
    axis.text.y = element_text(size = 6, colour = "grey10"),
    axis.text.x = element_text(size = 5.8, colour = "grey10"),
    axis.title = element_text(size = 6.8, colour = "grey10"),
    strip.text.y.left = element_text(angle = 0, hjust = 0, size = 5.9,
                                     face = "bold", colour = "grey10",
                                     margin = margin(1, 2, 1, 0)),
    strip.placement = "outside",
    strip.background = element_blank(),
    # 条带文字默认按条带宽度裁切：泳道 6 的题名（Downstream pathway combination）
    # 比其余四条长，再长也要求整句可读，所以关掉裁切（ggplot2 ≥ 3.5 的 strip.clip）。
    # 关掉后文字向左侧留白溢出，不影响面板左边界（实测各泳道面板左线仍在同一列）。
    strip.clip = "off",
    panel.spacing.y = unit(1.6, "mm"),
    plot.margin = margin(1, 1, 1, 1, "mm"),
    plot.tag = element_text(size = 8, face = "bold", family = "Arial"))

# ---- 面板 a：泳道主轨（单面板，不做横向拼图） ---------------------------------
# 试验数不另开一栏，而是放在同一坐标系的右端（x > 5.2）：多一栏就多一条要对齐的
# 边界，一栏宽了整幅的 gutter 就跟着不齐。放在同一面板里，行永远是对的。
X_NUM <- 5.62                      # 试验数一列的位置
X_SEP <- 5.45                      # 与阶段轴之间的分隔线

pa <- ggplot(d, aes(y = drug)) +
  geom_vline(xintercept = X_SEP, linewidth = 0.28, colour = "grey80") +
  geom_segment(aes(x = 0, xend = x, colour = lane), linewidth = 3.1, alpha = 0.16,
               lineend = "round", show.legend = FALSE) +
  geom_segment(aes(x = 0, xend = x, colour = lane), linewidth = 0.9,
               lineend = "round", show.legend = FALSE) +
  geom_point(aes(x = x, shape = status, fill = lane), size = 2.05, colour = "grey15",
             stroke = 0.42) +
  geom_text(aes(x = X_NUM, label = n_trials), hjust = 0, size = 1.9, family = "Arial",
            colour = "grey25") +
  scale_colour_manual(values = LANE_COL) +
  scale_fill_manual(values = LANE_COL) +
  scale_shape_manual(values = SHAPE, name = "Status reached") +
  scale_y_discrete(labels = function(x) parse(text = LAB_EXPR[x])) +
  scale_x_continuous(position = "bottom", breaks = unname(STAGE_X), labels = stage_lab,
                     limits = c(-0.25, 6.25), expand = expansion(mult = c(0, 0)),
                     guide = guide_axis(n.dodge = 2),
                     sec.axis = sec_axis(~ ., breaks = X_NUM,
                                         labels = "Trials (n)")) +
  labs(x = "Highest stage reached  →", y = NULL, tag = "a") +
  guides(shape = "none", fill = "none") +
  facet_grid(lane ~ ., scales = "free_y", space = "free_y", switch = "y",
             labeller = as_labeller(LANE)) +
  base_theme +
  theme(strip.text.y.left = element_text(angle = 0, hjust = 0, size = 5.9,
                                         face = "bold", colour = "grey10"),
        strip.placement = "outside", strip.background = element_blank(),
        panel.border = element_rect(colour = "grey80", fill = NA, linewidth = 0.3),
        plot.margin = margin(1.6, 3, 1.6, 2, "mm"))

# ---- 面板 b：各泳道 × 八个等位基因的覆盖矩阵 -----------------------------------
# 原图用「实心／斜线／空心」三态，斜线要靠 ggpattern（本机没装）。改成「实心／浅色／
# 白底」三档明度＋统一描边：黑白打印与缩版下都比斜线更稳，也和 a 面板同一套色。
cov_raw <- read.csv(file.path(DATA, "图八_等位基因覆盖.csv"), check.names = FALSE,
                    stringsAsFactors = FALSE)
alleles <- colnames(cov_raw)[-1]
COV_LVL <- sort(unique(as.integer(cov_raw$lane)))
stopifnot(identical(COV_LVL, LANE_LVL))   # a 与 b 的泳道必须同一套，否则行号对不上
cov <- cov_raw %>%
  pivot_longer(-lane, names_to = "allele", values_to = "cover") %>%
  mutate(lane = factor(lane, levels = COV_LVL),
         allele = factor(allele, levels = alleles),
         cover = factor(cover, levels = c("full", "partial", "none")))

pb <- ggplot(cov, aes(allele, lane, fill = lane, alpha = cover)) +
  geom_tile(colour = "grey25", linewidth = 0.28, width = 0.94, height = 0.9) +
  scale_fill_manual(values = LANE_COL, guide = "none") +
  scale_alpha_manual(values = c(full = 1, partial = 0.32, none = 0),
                     breaks = c("full", "partial", "none"),
                     labels = c("Full coverage", "Partial or early", "Not covered"),
                     name = NULL, drop = FALSE) +
  scale_x_discrete(expand = expansion(add = 0.3),
                   labels = function(x) gsub(" ", "\n", x)) +
  scale_y_discrete(limits = rev(levels(cov$lane)),
                   labels = function(x) gsub("  ", " ", LANE[x]),
                   expand = expansion(add = 0.3)) +
  labs(x = NULL, y = NULL, tag = "b") +

  theme_minimal(base_family = "Arial", base_size = 7) +
  theme(panel.grid = element_blank(),
        axis.text.x = element_text(size = 5.4, colour = "grey10", lineheight = 0.92),
        axis.text.y = element_text(size = 5.6, colour = "grey10"),
        # 图例不画在面板里：居中放着会在左下角留一大片白，改为下方一律左对齐的独立条
        legend.position = "none",
        plot.tag = element_text(size = 8, face = "bold", family = "Arial"),
        plot.margin = margin(1.6, 3, 2, 2, "mm"))

# ---- 图例：单独一行，横排在 a 的下端 --------------------------------------------
# 作者要求：图例不要一会儿在上、一会儿在下，各自放到**相应面板的下端**。
# 这条（药物状态）原先在整图顶端，现在挪到面板 a 的下端；
# 面板 b 的覆盖度图例本来就在 b 的下端，保留不动，并改为左端对齐——
# 原先居中放在底部，左下角空出一大片。
leg <- ggplot() +
  geom_segment(aes(x = 0, xend = 0.26, y = 2, yend = 2), colour = LANE_COL[["1"]],
               linewidth = 3.1, alpha = 0.16) +
  geom_segment(aes(x = 0, xend = 0.26, y = 2, yend = 2), colour = LANE_COL[["1"]],
               linewidth = 0.9) +
  geom_point(aes(x = 0.26, y = 2), shape = 23, size = 2.05, fill = LANE_COL[["1"]],
             colour = "grey15", stroke = 0.42) +
  geom_text(aes(x = 0.33, y = 2), label = sprintf("Mechanism lane (1-%d, named at left)",
                                                  max(LANE_LVL)),
            hjust = 0, size = 2.05, family = "Arial") +
  geom_point(aes(x = 0, y = 1), shape = 23, size = 2.05, fill = "grey55",
             colour = "grey15", stroke = 0.42) +
  geom_text(aes(x = 0.06, y = 1, label = "Approved"), hjust = 0, size = 2.05,
            family = "Arial") +
  geom_point(aes(x = 0.55, y = 1), shape = 21, size = 2.05, fill = "white",
             colour = "grey15", stroke = 0.42) +
  geom_text(aes(x = 0.61, y = 1, label = "In clinical trials"), hjust = 0,
            size = 2.05, family = "Arial") +
  geom_point(aes(x = 1.36, y = 1), shape = 24, size = 2.05, fill = "white",
             colour = "grey15", stroke = 0.42) +
  geom_text(aes(x = 1.42, y = 1, label = "Preclinical only"), hjust = 0,
            size = 2.05, family = "Arial") +
  coord_cartesian(xlim = c(-0.02, 3.2), ylim = c(0.6, 2.4), clip = "off") +
  theme_void(base_family = "Arial")

# ---- 图例（面板 b）：三档覆盖度，同样横排、同样左对齐 ------------------------
leg_b <- ggplot() +
  geom_point(aes(x = 0, y = 1), shape = 22, size = 2.05, fill = "grey45",
             colour = "grey25", stroke = 0.42) +
  geom_text(aes(x = 0.06, y = 1, label = "Full coverage"), hjust = 0, size = 2.05,
            family = "Arial") +
  geom_point(aes(x = 0.62, y = 1), shape = 22, size = 2.05, fill = "grey82",
             colour = "grey25", stroke = 0.42) +
  geom_text(aes(x = 0.68, y = 1, label = "Partial or early"), hjust = 0, size = 2.05,
            family = "Arial") +
  geom_point(aes(x = 1.34, y = 1), shape = 22, size = 2.05, fill = "white",
             colour = "grey25", stroke = 0.42) +
  geom_text(aes(x = 1.40, y = 1, label = "Not covered"), hjust = 0, size = 2.05,
            family = "Arial") +
  coord_cartesian(xlim = c(-0.02, 3.2), ylim = c(0.6, 1.4), clip = "off") +
  theme_void(base_family = "Arial")

# 拼图：a 与 b 的**面板区**左右边界必须落在同一条竖线上。
# cowplot 的 align="h" 在含分面的图上不保证（实测 b 的格子比 a 的泳道左移了一大截），
# 所以这里按字宽算：a 的行标签比 b 的长，把差值补成 b 的左边距，两块面板就齐了。
# 拼图对齐：a 的行标签栏比 b 的宽，直接把差值补成 b 的左边距，
# 两块面板的左边界才落在同一条竖线上。宽度从 gtable 现量——注意要用
# `layout$l`（面板所在的**列号**），不是 `layout` 的行号：含分面的图里两者不同。
panel_gutter <- function(p) {
  # 量 gtable 用的临时设备必须是**认 Arial 的**那一个：原先用 pdf(NULL)，
  # 走 PostScript 字体库，报「font family 'Arial' not found」，连带把
  # ggtext 的斜体行宽量错——`*KRAS*  G12C` 的空格被测成 0 宽，字就叠在一起。
  tmp <- tempfile(fileext = ".pdf")
  grDevices::cairo_pdf(tmp)
  on.exit({grDevices::dev.off(); unlink(tmp)}, add = TRUE)
  g <- ggplotGrob(p)
  l <- g$layout$l[grepl("^panel", g$layout$name)][1]
  sum(grid::convertWidth(g$widths[seq_len(l - 1)], "mm", valueOnly = TRUE))
}

MARGIN_L <- 2
GUT_A <- panel_gutter(pa)
GUT_B <- panel_gutter(pb)
pb <- pb + theme(plot.margin = margin(2, 3, 2,
                                      MARGIN_L + (GUT_A - GUT_B), "mm"))

fig <- cowplot::plot_grid(pa, leg, pb, leg_b, ncol = 1,
                          rel_heights = c(1, 0.035, 0.26, 0.03))

W <- 180
# 图高随药数走：面板 a 每多一行就多 3.4 mm（照 47 行 232 mm 的行距量出来），
# 不写死高度，否则补药之后行被压扁或标题与图例打架（2026-10-31 由 47 药增到 55 药）。
ROW_MM <- 3.4
H <- round(232 - ROW_MM * 47 + ROW_MM * nrow(d))
grDevices::cairo_pdf(file.path(OUT, "Fig8_drug_class_swimlanes.pdf"), mm(W), mm(H),
                     family = "Arial")
print(fig); dev.off()
if (requireNamespace("svglite", quietly = TRUE)) {
  svglite::svglite(file.path(OUT, "Fig8_drug_class_swimlanes.svg"), mm(W), mm(H),
                   bg = "white"); print(fig); dev.off()
}
png(file.path(OUT, "Fig8_drug_class_swimlanes.png"), mm(W), mm(H), units = "in",
    res = 600, type = "cairo", family = "Arial", bg = "white")
print(fig); dev.off()

cat("-> figures/Fig8_drug_class_swimlanes.{pdf,svg,png}\n")
cat(sprintf("自查：%d 药 / %d 泳道 / 获批 %d / 临床 %d / 临床前 %d；试验数合计 %d\n",
            nrow(d), n_distinct(d$lane), sum(d$status == "Approved"),
            sum(d$status == "In clinical trials"),
            sum(d$status == "Preclinical only"), sum(d$n_trials)))
