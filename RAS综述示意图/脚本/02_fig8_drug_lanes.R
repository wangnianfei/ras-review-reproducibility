#!/usr/bin/env Rscript
# 图9（图件基名 Fig8_drug_class_swimlanes）：RAS 靶向药物分类泳道图
#
# 2026-11-02 重画（作者：字号与版式不合理、没用好 Word 版心、缺顶刊品味、配色与前文不一致）：
#   · 与图1–8 同一套版式：画布 180 mm 宽（排进 14.66 cm 版心按 0.81 缩放），
#     图内文字一律 Arial 7.5 pt，面板字母 9 pt 粗体；不再有 5.4–6.8 pt 的杂号；
#   · 面板 a 由单栏 59 行（原图 180 × 272 mm）改为**双栏**：左栏泳道 1–3（直接结合 RAS 的
#     OFF 态与 ON 态抑制剂），右栏泳道 4–6；每栏四列：药名、靶标、阶段轨、登记试验数；
#   · 泳道色取自图8 的机制色（MAPK 蓝、PI3K 绿、RAS-GTP 红、RAL 紫、赭、灰），全文一套；
#   · 在研代号不再上图（代号逐药列在表1），行标签只留药名，靶标单列且省去 KRAS 前缀；
#   · 面板 b 的覆盖矩阵横排在底部，图例放在右侧留白里。
# 全图在一个以 mm 为单位的坐标系里手工排版（ggplot 只当画布用），每个字的位置可算；
# 出图前做一次文字越界检查：任何药名/靶标超出本列宽度即报错退出。
#
# 数据：数据/图八_药物泳道.csv（lane, drug, code, stage, n_trials, target, regulatory）
#       数据/图八_等位基因覆盖.csv（lane × 八个等位基因：full / partial / none）
# 用法：Rscript 02_fig8_drug_lanes.R <示意图项目根>
suppressPackageStartupMessages({
  library(ggplot2); library(grid); library(dplyr); library(tidyr)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")
dir.create(OUT, showWarnings = FALSE)

# ---- 版式常量（与图1–8 一致） ------------------------------------------------
W <- 180
FS_PT <- 7.5; PN_PT <- 9
FS <- FS_PT / .pt; PN <- PN_PT / .pt          # geom_text 的 size（mm）
FS_MM <- FS_PT * 25.4 / 72                       # 字号对应的 mm
INK <- "#1A1A1A"; GREY <- "#59656B"; RULE <- "#D5DBDE"; TRACK <- "#EEF1F2"
FAM <- "Arial"

LANE <- c(`1` = "OFF-state covalent", `2` = "Non-covalent / reversible",
          `3` = "RAS(ON) tri-complex", `4` = "Degraders and other modalities",
          `5` = "Upstream and immune", `6` = "Downstream pathway combination")
# 图8 的机制色：MAPK 蓝、PI3K 绿、RAS-GTP 红、RAL 紫、其他效应器赭、GAP 灰
LANE_COL <- c(`1` = "#2E6F9E", `2` = "#1C7C54", `3` = "#D7263D",
              `4` = "#6A4C93", `5` = "#A0522D", `6` = "#59656B")
COLS <- list(left = 1:3, right = 4:6)            # 两栏各放哪几条泳道

STAGE_K <- c("Preclinical" = 0, "Phase 1" = 1, "Phase 1/2" = 2,
             "Phase 2" = 3, "Phase 3" = 4, "Approved" = 5)
STAGE_LAB <- c("Pre", "I", "I/II", "II", "III", "Appr.")

# 靶标栏的短写：省去 KRAS 前缀（图注写明），蛋白与疗法类型照写
TGT <- c(
  "KRAS G12C" = "G12C", "KRAS G12D" = "G12D", "KRAS G12V (OFF)" = "G12V (OFF)",
  "KRAS G12D (ON)" = "G12D (ON)", "KRAS G12C (ON)" = "G12C (ON)",
  "KRAS G12V (ON)" = "G12V (ON)", "multi-selective RAS(ON)" = "multi (ON)",
  "pan-KRAS" = "pan-KRAS", "pan-RAS" = "pan-RAS",
  "KRAS G12C (ON/OFF)" = "G12C (ON/OFF)", "KRAS G12D degrader" = "G12D degrader",
  "KRAS G12D mRNA/siRNA" = "G12D siRNA", "SHP2" = "SHP2", "SOS1" = "SOS1",
  "farnesyl transferase (HRAS)" = "FTase (HRAS)",
  "mutant-RAS peptide vaccine" = "peptide vaccine",
  "mutant-RAS whole-yeast vaccine" = "yeast vaccine",
  "mutant-KRAS mRNA vaccine" = "mRNA vaccine",
  "adoptive T-cell therapy" = "TCR-T", "RAF/MEK clamp + FAK" = "RAF/MEK + FAK")

d <- read.csv(file.path(DATA, "图八_药物泳道.csv"), check.names = FALSE,
              stringsAsFactors = FALSE)
stopifnot(all(d$stage %in% names(STAGE_K)), all(d$target %in% names(TGT)),
          all(as.character(unique(d$lane)) %in% names(LANE)),
          setequal(unique(as.integer(d$lane)), unlist(COLS)))
d <- d %>% mutate(lane = as.integer(lane), k = unname(STAGE_K[stage]),
                  n_trials = as.integer(n_trials), tgt = unname(TGT[target])) %>%
  arrange(lane, desc(k), desc(n_trials), drug)

# ---- 量字宽：用认 Arial 的 cairo 设备 -----------------------------------------
tmp <- tempfile(fileext = ".pdf"); grDevices::cairo_pdf(tmp, family = FAM)
tw <- function(s, face = "plain")
  vapply(s, function(x) convertWidth(grobWidth(textGrob(x, gp = gpar(
    fontfamily = FAM, fontsize = FS_PT, fontface = face))), "mm", valueOnly = TRUE), 0)

# ---- 面板 a 几何 ---------------------------------------------------------------
PITCH <- 3.4                 # 行距（7.5 pt × 1.27 ≈ 3.36 mm）
HEAD_H <- 4.4                # 泳道题头行
LANE_GAP <- 2.2
COLW <- 87.5
X0 <- c(left = 2.3, right = 91.7)          # 右栏数字右缘落在 179.2 mm，不贴画布边
OFF <- list(name = 3.4, tgt = 28.2, trk = 50.4, stp = 5.7, n = COLW)
NAME_W <- OFF$tgt - OFF$name - 1.8
TGT_W <- OFF$trk - OFF$tgt - 2.4
Y_HDR <- 3.4                 # 列标题行（与面板字母 a 同一行）
Y_START <- 7.2

# 基因斜体不用 plotmath（cairo 下 italic() 的字距会被拉开），而是按实测字宽
# 把「正体—斜体—正体」三段并排写出：FTase (HRAS) → "FTase (" + HRAS + ")"
split_gene <- function(s) {
  m <- regmatches(s, regexec("^(.*\\()(KRAS|NRAS|HRAS)(\\).*)$", s))[[1]]
  if (length(m)) list(c(m[2], "plain"), c(m[3], "italic"), c(m[4], "plain"))
  else list(c(s, "plain"))
}

rows <- list(); heads <- list(); stripes <- list(); y_end <- c()
for (side in names(COLS)) {
  y <- Y_START; x0 <- X0[[side]]
  for (ln in COLS[[side]]) {
    heads[[length(heads) + 1]] <- data.frame(side = side, lane = ln, x0 = x0, y = y)
    y <- y + HEAD_H
    dl <- d[d$lane == ln, ]
    y_lane0 <- y
    for (i in seq_len(nrow(dl))) {
      nm <- dl$drug[i]
      lines <- if (tw(nm) > NAME_W) strsplit(sub(" \\+ ", " +\n", nm), "\n")[[1]] else nm
      h <- PITCH * length(lines)
      rows[[length(rows) + 1]] <- data.frame(
        side = side, lane = ln, x0 = x0, yc = y + h / 2, name = paste(lines, collapse = "\n"), nlines = length(lines),
        tgt = dl$tgt[i], k = dl$k[i], n = dl$n_trials[i], stringsAsFactors = FALSE)
      y <- y + h
    }
    stripes[[length(stripes) + 1]] <- data.frame(lane = ln, x0 = x0, y0 = y_lane0, y1 = y)
    y <- y + LANE_GAP
  }
  y_end[side] <- y - LANE_GAP
}
rows <- bind_rows(rows); heads <- bind_rows(heads); stripes <- bind_rows(stripes)

# 越界检查：药名、靶标不得越过本列
bad <- c(rows$name[vapply(strsplit(rows$name, "\n"), function(v) max(tw(v)), 0) > NAME_W],
         rows$tgt[tw(rows$tgt) > TGT_W])
hw <- tw(sprintf("%s  %s", heads$lane, LANE[as.character(heads$lane)]), "bold")
if (any(hw + 4 > COLW)) bad <- c(bad, "lane header")
if (length(bad)) stop("文字越界：", paste(unique(bad), collapse = "; "))

# ---- 面板 b 几何（底部横排） -----------------------------------------------------
cov_raw <- read.csv(file.path(DATA, "图八_等位基因覆盖.csv"), check.names = FALSE,
                    stringsAsFactors = FALSE)
alleles <- colnames(cov_raw)[-1]
stopifnot(setequal(as.integer(cov_raw$lane), unique(d$lane)),
          all(unlist(cov_raw[-1]) %in% c("full", "partial", "none")))
YB <- max(y_end[["left"]], y_end[["right"]] + 4.6 + 2 * PITCH) + 6.0   # 面板 b 字母所在行（a 图例在右栏下方）
CELL_W <- 10.5; CELL_H <- 3.2; CPITCH <- 4.1
XB_LAB <- 3.0; XB_CELL <- 50.0
YB_H1 <- YB; YB_H2 <- YB + PITCH          # 等位基因两行表头
YB_ROW0 <- YB + 2 * PITCH + 1.8           # 第一行格子中心
cov <- cov_raw %>% pivot_longer(-lane, names_to = "allele", values_to = "cover") %>%
  mutate(lane = as.integer(lane), j = match(allele, alleles),
         i = match(lane, sort(unique(lane))),
         xc = XB_CELL + (j - 0.5) * (CELL_W + 0.8), yc = YB_ROW0 + (i - 1) * CPITCH)
H <- ceiling(max(cov$yc) + CELL_H / 2 + 1.2)
XB_END <- XB_CELL + length(alleles) * (CELL_W + 0.8)

tint <- function(col, f) {              # 与白色按 f 混合
  m <- grDevices::col2rgb(col) / 255
  grDevices::rgb(t(m + (1 - m) * f))
}

# ---- 作图 --------------------------------------------------------------------
Y <- function(y) -y
p <- ggplot() + coord_fixed(xlim = c(0, W), ylim = c(-H, 0), expand = FALSE) +
  theme_void(base_family = FAM) + theme(plot.margin = margin(0, 0, 0, 0))
txt <- function(p, x, y, lab, hjust = 0, col = INK, face = "plain",
                size = FS)
  p + annotate("text", x = x, y = Y(y), label = lab, hjust = hjust, vjust = 0.5,
               family = FAM, size = size, colour = col, fontface = face,
               lineheight = 0.95)

# 面板字母
p <- txt(p, 0.3, Y_HDR - 0.2, "a", face = "bold", size = PN)
p <- txt(p, 0.3, YB_H1, "b", face = "bold", size = PN)

for (side in names(COLS)) {
  x0 <- X0[[side]]; tx <- x0 + OFF$trk
  # 列标题
  p <- txt(p, x0 + OFF$name, Y_HDR, "Agent", col = GREY)
  p <- txt(p, x0 + OFF$tgt, Y_HDR, "Target", col = GREY)
  p <- txt(p, tx + OFF$stp * (0:5), Y_HDR, STAGE_LAB, hjust = 0.5, col = GREY)
  p <- txt(p, x0 + OFF$n, Y_HDR, "n", hjust = 1, col = GREY)
  p <- p + annotate("segment", x = x0, xend = x0 + COLW, y = Y(Y_HDR + 2.0),
                    yend = Y(Y_HDR + 2.0), colour = INK, linewidth = 0.25)
  # 阶段网格线（贯穿该栏）
  p <- p + annotate("segment", x = tx + OFF$stp * (0:5), xend = tx + OFF$stp * (0:5),
                    y = Y(Y_START), yend = Y(y_end[[side]]), colour = RULE,
                    linewidth = 0.18)
}

# 泳道题头：色块编号＋粗体名；左侧色条贯穿本泳道各行
for (r in seq_len(nrow(heads))) {
  h <- heads[r, ]; col <- LANE_COL[[as.character(h$lane)]]; yc <- h$y + HEAD_H / 2 - 0.2
  p <- p + annotate("rect", xmin = h$x0, xmax = h$x0 + 3.0, ymin = Y(yc + 1.5),
                    ymax = Y(yc - 1.5), fill = col, colour = NA)
  p <- txt(p, h$x0 + 1.5, yc, as.character(h$lane), hjust = 0.5, col = "white",
           face = "bold")
  p <- txt(p, h$x0 + 4.4, yc, LANE[[as.character(h$lane)]], face = "bold")
}
for (r in seq_len(nrow(stripes))) {
  s <- stripes[r, ]
  p <- p + annotate("rect", xmin = s$x0 + 1.0, xmax = s$x0 + 1.6, ymin = Y(s$y1 - 0.5),
                    ymax = Y(s$y0 + 0.5), fill = tint(LANE_COL[[as.character(s$lane)]], 0.55),
                    colour = NA)
}

# 各药一行
for (r in seq_len(nrow(rows))) {
  w <- rows[r, ]; col <- LANE_COL[[as.character(w$lane)]]
  x0 <- w$x0; tx <- x0 + OFF$trk; xe <- tx + OFF$stp * w$k; yc <- w$yc
  p <- txt(p, x0 + OFF$name, yc, w$name)
  xx <- x0 + OFF$tgt
  for (sg in split_gene(w$tgt)) {
    p <- txt(p, xx, yc, sg[1], col = GREY, face = sg[2]); xx <- xx + tw(sg[1], sg[2])
  }
  # 阶段轨：浅底 → 泳道色实杠 → 末端标记
  p <- p + annotate("segment", x = tx, xend = tx + OFF$stp * 5, y = Y(yc), yend = Y(yc),
                    colour = TRACK, linewidth = 2.6, lineend = "round")
  if (w$k > 0)
    p <- p + annotate("segment", x = tx, xend = xe, y = Y(yc), yend = Y(yc),
                      colour = col, linewidth = 1.25, lineend = "round")
  if (w$k == 5) {
    p <- p + annotate("point", x = xe, y = Y(yc), shape = 23, size = 2.5, fill = col,
                      colour = col, stroke = 0.35)
  } else if (w$k == 0) {
    p <- p + annotate("point", x = xe + 0.3, y = Y(yc - 0.15), shape = 24, size = 2.1,
                      fill = "white", colour = col, stroke = 0.7)
  } else {
    p <- p + annotate("point", x = xe, y = Y(yc), shape = 21, size = 2.2, fill = "white",
                      colour = col, stroke = 0.75)
  }
  p <- txt(p, x0 + OFF$n, yc, format(w$n), hjust = 1)
}

# 面板 a 图例：右栏下方的留白
YL <- y_end[["right"]] + 4.6; XL <- X0[["right"]] + OFF$name
lg <- function(p, x, y, shape, fill, col, lab, size = 2.3, stroke = 0.75) {
  p <- p + annotate("point", x = x, y = Y(y), shape = shape, size = size, fill = fill,
                    colour = col, stroke = stroke)
  txt(p, x + 2.4, y, lab)
}
p <- lg(p, XL + 1, YL, 23, GREY, GREY, "Approved (≥1 regulatory approval)", 2.5, 0.35)
p <- lg(p, XL + 1, YL + PITCH, 21, "white", GREY, "Clinical stage")
p <- lg(p, XL + 30, YL + PITCH, 24, "white", GREY, "Preclinical only", 2.1, 0.7)
p <- txt(p, XL, YL + 2 * PITCH, "n, registered trials in the 1,133-trial corpus",
         col = GREY)

# 面板 b：表头（基因斜体）、行名、格子
gene_of <- sub(" .*", "", alleles); rest_of <- sub("^\\S+ ?", "", alleles)
for (j in seq_along(alleles)) {
  xc <- XB_CELL + (j - 0.5) * (CELL_W + 0.8)
  p <- txt(p, xc, YB_H1, gene_of[j], hjust = 0.5, face = "italic")
  if (nzchar(rest_of[j])) p <- txt(p, xc, YB_H2, rest_of[j], hjust = 0.5)
}
for (ln in sort(unique(cov$lane))) {
  yc <- YB_ROW0 + (match(ln, sort(unique(cov$lane))) - 1) * CPITCH
  col <- LANE_COL[[as.character(ln)]]
  p <- p + annotate("rect", xmin = XB_LAB, xmax = XB_LAB + 3.0, ymin = Y(yc + 1.5),
                    ymax = Y(yc - 1.5), fill = col, colour = NA)
  p <- txt(p, XB_LAB + 1.5, yc, as.character(ln), hjust = 0.5, col = "white", face = "bold")
  p <- txt(p, XB_LAB + 4.4, yc, LANE[[as.character(ln)]])
}
fill_of <- function(lane, cover) {
  col <- LANE_COL[[as.character(lane)]]
  switch(cover, full = col, partial = tint(col, 0.68), none = "#F3F5F6")
}
for (r in seq_len(nrow(cov))) {
  cc <- cov[r, ]
  p <- p + annotate("rect", xmin = cc$xc - CELL_W / 2, xmax = cc$xc + CELL_W / 2,
                    ymin = Y(cc$yc + CELL_H / 2), ymax = Y(cc$yc - CELL_H / 2),
                    fill = fill_of(cc$lane, cc$cover), colour = NA)
}
stopifnot(max(tw(LANE)) + XB_LAB + 4.4 < XB_CELL - 1)
# 面板 b 图例：矩阵右侧
XLB <- XB_END + 4.0
legb <- list(c("full", "Clinical-stage agent"), c("partial", "Partial or early"),
             c("none", "Not covered"))
for (q in seq_along(legb)) {
  yy <- YB_ROW0 + (q - 1) * CPITCH
  p <- p + annotate("rect", xmin = XLB, xmax = XLB + 5.0, ymin = Y(yy + CELL_H / 2),
                    ymax = Y(yy - CELL_H / 2),
                    fill = fill_of(6, legb[[q]][1]), colour = NA)
  p <- txt(p, XLB + 6.4, yy, legb[[q]][2])
}
stopifnot(XLB + 6.4 + max(tw(vapply(legb, `[`, "", 2))) < W)
dev.off(); unlink(tmp)

# ---- 输出 --------------------------------------------------------------------
mm <- function(x) x / 25.4
grDevices::cairo_pdf(file.path(OUT, "Fig8_drug_class_swimlanes.pdf"), mm(W), mm(H),
                     family = FAM)
print(p); invisible(dev.off())
if (requireNamespace("svglite", quietly = TRUE)) {
  svglite::svglite(file.path(OUT, "Fig8_drug_class_swimlanes.svg"), mm(W), mm(H),
                   bg = "white"); print(p); invisible(dev.off())
}
png(file.path(OUT, "Fig8_drug_class_swimlanes.png"), mm(W), mm(H), units = "in",
    res = 400, type = "cairo", family = FAM, bg = "white")
print(p); invisible(dev.off())

cat(sprintf("-> figures/Fig8_drug_class_swimlanes.{pdf,svg,png}  %d × %d mm\n", W, H))
cat(sprintf("自查：%d 药 / %d 泳道 / 获批 %d / 临床 %d / 临床前 %d；试验数合计 %d\n",
            nrow(d), n_distinct(d$lane), sum(d$k == 5), sum(d$k %in% 1:4),
            sum(d$k == 0), sum(d$n_trials)))
