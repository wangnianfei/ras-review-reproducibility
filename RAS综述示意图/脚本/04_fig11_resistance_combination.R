#!/usr/bin/env Rscript
# 图12（图件基名 Fig11_resistance_to_combination）：耐药机制 × 联合逻辑矩阵
#
# 论点：九类机制里有六类只落到第 4 条逻辑上；第 3 条逻辑不对应任何单一机制；
# 第 5 条根本不在这条轴上。三件「空」在矩阵里一眼可见，所以用矩阵而不用弧线映射图。
#
# 版式（2026-11-02 作者第三轮：用满 Word 版心、整齐紧凑、字号与配色同图5–图9）：
#   · 180 mm 通栏，全部文字 Arial 7.5 pt、面板字母 9 pt 粗体——与图9、图10、图11 同一套；
#   · 与图9 泳道同一语法：每组一条主色色带（白色粗体组名）、组内行铺同色浅底，
#     格子三档同图9 面板 b——直接对应＝主色、部分对应＝主色 62% 淡化、不对应＝白；
#   · 三组颜色取全书主色板（图9 第 5、4、2 泳道色：teal／purple／amber），冷色为主；
#   · 整图在一张毫米坐标画布上排，列头、矩阵、面板 b 的左右边界同一组数，不靠拼图对齐；
#   · 节点名一律一行，行高因此压到 4.4 mm。
#
# 数据：数据/图十一_耐药机制.csv、图十一_联合逻辑.csv、图十一_矩阵.csv、图十一_对应.csv、图十一_检出率.csv
# 用法：Rscript 04_fig11_resistance_combination.R <示意图项目根>
suppressPackageStartupMessages({
  library(ggplot2); library(grid); library(dplyr)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")
dir.create(OUT, showWarnings = FALSE)
mm <- function(x) x / 25.4
rd <- function(f) read.csv(file.path(DATA, f), check.names = FALSE, stringsAsFactors = FALSE)

mech <- rd("图十一_耐药机制.csv"); mat <- rd("图十一_矩阵.csv"); det <- rd("图十一_检出率.csv")
map <- rd("图十一_对应.csv"); logics <- rd("图十一_联合逻辑.csv")

# 矩阵与对应清单必须一格不多一格不少：改了 对应.csv 忘了改矩阵，图上会静默少一格
stopifnot(setequal(paste0(map$from, "-", sub("^L", "", map$to)),
                   paste0(mat$mechanism, "-", mat$logic)),
          all(c("head_title", "head_readout", "head_source") %in% names(logics)),
          setequal(as.character(logics$logic), as.character(1:5)))
logics <- logics[order(as.integer(logics$logic)), ]

# ---- 字号、颜色（全书同一套） -------------------------------------------------
FAM <- "Arial"
FS_PT <- 7.5; PN_PT <- 9
FS <- FS_PT / .pt; PN <- PN_PT / .pt
INK <- "#1A1A1A"; GREY <- "#4D5559"; RULE <- "#D5DBDE"
GRP <- c(genetic = "Read out by sequencing", nongenetic = "Non-genetic programme",
         carrier = "Carrier (6.4)")
GRP_COL <- c(genetic = "#1F8A8C", nongenetic = "#6A4C93", carrier = "#E09F3E")
tint <- function(col, f) {              # 与白色按 f 混合（同图9）
  m <- grDevices::col2rgb(col) / 255
  grDevices::rgb(t(m + (1 - m) * f))
}
cell_fill <- function(g, lv) switch(lv, direct = GRP_COL[[g]],
                                    partial = tint(GRP_COL[[g]], 0.62), none = "white")

# 节点名短写成一行（原数据里的分号、箭头记法改成印刷形式）
NODE_FIX <- c("cell state -> GPX4" = "cell state → GPX4", "IRE1a" = "IRE1α",
              "mevalonate; ZBTB11" = "mevalonate, ZBTB11")
mat$node <- ifelse(mat$node %in% names(NODE_FIX), NODE_FIX[mat$node], mat$node)

# ---- 几何（mm，y 自上而下） ---------------------------------------------------
W <- 180
R <- W - 2.2                   # 内容右边界：留出末列刻度「100」半个字宽
X_LAB <- 2.4                    # 行名缩进（同图9 药名）
X0 <- 40                        # 矩阵左边界
CW <- (R - X0) / 5              # 列宽
GAP <- 0.8                      # 格间白缝
PITCH_L <- 3.3                  # 文字行距（7.5 pt × 1.25）
ROW_H <- 4.4; BAND_H <- 4.4; GRP_GAP <- 1.4
cx0 <- function(k) X0 + (k - 1) * CW + GAP / 2     # 第 k 列格子左缘
cx1 <- function(k) X0 + k * CW - GAP / 2

tmp <- tempfile(fileext = ".pdf"); grDevices::cairo_pdf(tmp, family = FAM)
tw <- function(s, face = "plain")
  vapply(s, function(x) convertWidth(grobWidth(textGrob(x, gp = gpar(
    fontfamily = FAM, fontsize = FS_PT, fontface = face))), "mm", valueOnly = TRUE), 0)
# 自查：最长的列头、行名、格内节点都放得下
heads <- with(logics, c(paste(logic, head_title), head_readout, head_source))
stopifnot(max(tw(heads, "bold")) < CW - 1.6,
          max(tw(mech$title)) < X0 - X_LAB - 1.5,
          max(tw(mat$node)) < CW - GAP - 1.6,
          max(tw(GRP, "bold")) < W)

Y_HEAD <- 4.2                               # 列头第一行中心
Y_RULE <- Y_HEAD + 2 * PITCH_L + 2.4        # 列头下的横线
y <- Y_RULE + 1.6
rows <- list(); bands <- list()
for (g in names(GRP)) {
  bands[[g]] <- data.frame(g = g, y0 = y, y1 = y + BAND_H); y <- y + BAND_H
  ids <- mech$id[mech$group == g]
  rows[[g]] <- data.frame(id = ids, g = g, title = mech$title[match(ids, mech$id)],
                          y0 = y + (seq_along(ids) - 1) * ROW_H,
                          y1 = y + seq_along(ids) * ROW_H)
  y <- y + length(ids) * ROW_H + GRP_GAP
}
bands <- bind_rows(bands); rows <- bind_rows(rows)
Y_MAT_END <- y - GRP_GAP
cells <- merge(expand.grid(id = rows$id, k = 1:5, stringsAsFactors = FALSE),
               rows, by = "id") %>%
  left_join(mat %>% transmute(id = mechanism, k = as.integer(logic), level, node),
            by = c("id", "k")) %>%
  mutate(level = ifelse(is.na(level), "none", level), node = ifelse(is.na(node), "", node))
cells$fill <- mapply(cell_fill, cells$g, cells$level)
cells$tcol <- ifelse(cells$level == "direct", "white", INK)

# 图例（直接对应／部分对应／不对应）：中性灰示三档，与格子同一淡化比例
Y_LEG <- Y_MAT_END + 4.2
LEG <- data.frame(lab = c("Logic answers the mechanism directly", "In part", "Not answered"),
                  fill = c(GREY, tint(GREY, 0.62), "white"))
KEY <- 3.2
LEG$x <- X0 + 0.4 + cumsum(c(0, head(KEY + 1.2 + tw(LEG$lab) + 4.5, -1)))

# 面板 b：两条检出比例，横轴 0–100% 铺满矩阵同一宽度
Y_B <- Y_LEG + 6.2                          # 面板字母 b
det <- det[order(-det$pct), ]
det$yc <- Y_B + 2.4 + (seq_len(nrow(det)) - 1) * ROW_H
det$cap <- sprintf("%s, %s", det$label, det$n)
stopifnot(max(tw(det$cap)) < X0 - X_LAB - 1.5)
BX0 <- cx0(1); BX1 <- cx1(5)
bx <- function(p) BX0 + (BX1 - BX0) * p / 100
BAR <- 2.6
Y_AX <- max(det$yc) + ROW_H / 2 + 0.4
H <- ceiling(Y_AX + 1.2 + PITCH_L * 2 + 1)
invisible(dev.off()); unlink(tmp)

# ---- 作图 ----------------------------------------------------------------------
Y <- function(v) -v
rect <- function(d, ...) geom_rect(data = d, aes(xmin = x0, xmax = x1, ymin = Y(y1), ymax = Y(y0)),
                                   inherit.aes = FALSE, ...)
p <- ggplot() + coord_fixed(xlim = c(0, W), ylim = c(-H, 0), expand = FALSE, clip = "off") +
  theme_void(base_family = FAM) + theme(plot.margin = margin(0, 0, 0, 0))
tx <- function(x, y, lab, hjust = 0, col = INK, face = "plain", size = FS)
  annotate("text", x = x, y = Y(y), label = lab, hjust = hjust, vjust = 0.5, colour = col,
           fontface = face, size = size, family = FAM)

p <- p +
  tx(0, 2.0, "a", face = "bold", size = PN) +
  # 列头：编号＋逻辑名（粗）、最佳临床读数、出处（灰），左对齐到列左缘
  tx(cx0(1:5) + 0.8, Y_HEAD, paste(logics$logic, logics$head_title), face = "bold") +
  tx(cx0(1:5) + 0.8, Y_HEAD + PITCH_L, logics$head_readout) +
  tx(cx0(1:5) + 0.8, Y_HEAD + 2 * PITCH_L, logics$head_source, col = GREY) +
  annotate("segment", x = 0, xend = R, y = Y(Y_RULE), yend = Y(Y_RULE),
           linewidth = 0.5, colour = INK) +
  # 组色带与组内浅底
  rect(transform(bands, x0 = 0, x1 = R), fill = GRP_COL[bands$g], colour = NA) +
  tx(X_LAB - 1.2, (bands$y0 + bands$y1) / 2, unname(GRP[bands$g]), col = "white", face = "bold") +
  rect(transform(rows, x0 = 0, x1 = R), fill = tint(GRP_COL[rows$g], 0.88), colour = NA) +
  tx(X_LAB, (rows$y0 + rows$y1) / 2, rows$title) +
  rect(transform(cells, x0 = cx0(k), x1 = cx1(k), y0 = y0 + GAP / 2, y1 = y1 - GAP / 2),
       fill = cells$fill, colour = NA) +
  tx((cx0(cells$k) + cx1(cells$k)) / 2, (cells$y0 + cells$y1) / 2, cells$node,
     hjust = 0.5, col = cells$tcol) +
  # 图例
  rect(data.frame(x0 = LEG$x, x1 = LEG$x + KEY, y0 = Y_LEG - KEY * 0.4, y1 = Y_LEG + KEY * 0.4),
       fill = LEG$fill, colour = GREY, linewidth = 0.25) +
  tx(LEG$x + KEY + 1.2, Y_LEG, LEG$lab) +
  # 面板 b
  tx(0, Y_B, "b", face = "bold", size = PN) +
  annotate("segment", x = bx(50), xend = bx(50), y = Y(Y_B + 0.2), yend = Y(Y_AX),
           linewidth = 0.25, colour = RULE) +
  rect(data.frame(x0 = BX0, x1 = BX1, y0 = det$yc - BAR / 2, y1 = det$yc + BAR / 2),
       fill = "#ECEEEF", colour = NA) +
  rect(data.frame(x0 = BX0, x1 = bx(det$pct), y0 = det$yc - BAR / 2, y1 = det$yc + BAR / 2),
       fill = GREY, colour = NA) +
  tx(bx(det$pct) + 1.2, det$yc, paste0(det$pct, "%")) +
  tx(X_LAB, det$yc, det$cap) +
  annotate("segment", x = BX0, xend = BX1, y = Y(Y_AX), yend = Y(Y_AX),
           linewidth = 0.3, colour = INK) +
  annotate("segment", x = bx(c(0, 50, 100)), xend = bx(c(0, 50, 100)),
           y = Y(Y_AX), yend = Y(Y_AX + 1), linewidth = 0.3, colour = INK) +
  tx(bx(c(0, 50, 100)), Y_AX + 1 + PITCH_L * 0.6, c("0", "50", "100"), hjust = 0.5) +
  tx((BX0 + BX1) / 2, Y_AX + 1 + PITCH_L * 1.75,
     "Acquired alteration detected (%; two denominators, not comparable)", hjust = 0.5)

grDevices::cairo_pdf(file.path(OUT, "Fig11_resistance_to_combination.pdf"), mm(W), mm(H),
                     family = FAM)
print(p); invisible(dev.off())
if (requireNamespace("svglite", quietly = TRUE)) {
  svglite::svglite(file.path(OUT, "Fig11_resistance_to_combination.svg"), mm(W), mm(H),
                   bg = "white"); print(p); invisible(dev.off())
}
png(file.path(OUT, "Fig11_resistance_to_combination.png"), mm(W), mm(H), units = "in",
    res = 400, type = "cairo", family = FAM, bg = "white")
print(p); invisible(dev.off())

cat(sprintf("-> figures/Fig11_resistance_to_combination.{pdf,svg,png}  %d × %d mm\n", W, H))
cat(sprintf("自查：机制 %d / 逻辑 %d / 对上 %d 格（直接 %d、部分 %d、空 %d）；检出率 %s\n",
            nrow(rows), nrow(logics), sum(cells$level != "none"),
            sum(cells$level == "direct"), sum(cells$level == "partial"),
            sum(cells$level == "none"), paste0(det$pct, "%", collapse = " / ")))
