#!/usr/bin/env Rscript
# 图10（图件基名 Fig9_RAS_milestones_timeline）：历史大事记时间线，v5。
#
# 2026-11-02 重画（作者：与图9 同样的问题——冷色调不清晰不醒目、字号与版式不合理）：
#   · 与图1–9 同一套版式：画布 180 mm 宽，图内文字一律 Arial 7.5 pt（原 4.8–5.6 pt 杂号）；
#   · 配色取全文主色板：生物学泳道用紫（图4 Q61X），药物泳道用 KRAS 珊瑚（图3/图5/图9 泳道 1），
#     阶段尺用琥珀（图4）两档浅色交替；泳道铺本色浅底，左缘通栏色带白色粗体泳道名（同图9）；
#   · 卡片白底、泳道色描边，标题粗体墨色、出处正体灰；switch-II 口袋一张描边加粗；
#     引线改泳道色；年份粗体；
#   · 卡片由脚本按实测字宽自己折行、自己算高（不再交给 ggtext 估），层高随卡片高度走；
#     出图前三项检查：单词超宽、同层卡片重叠、引线穿过别的卡片，任何一项不过即报错退出。
# 骨架不变：序数主轴（每个有节点的年份一个等距槽位）＋ 顶部真实比例镜像；只画阳性里程碑。
#
# 数据：数据/图九_大事记.csv（候选全集，milestone=Y 的 12 条上）＋ 数据/图九_分期.csv。
# 用法：Rscript 11_fig9_timeline.R <示意图项目根>
# 出图：<根>/figures/Fig9_RAS_milestones_timeline.{pdf,svg,png}
suppressPackageStartupMessages({
  library(ggplot2); library(grid); library(ggtext)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")
dir.create(OUT, showWarnings = FALSE)
mm <- function(x) x / 25.4

# ---- 版式常量（与图1–9 一致） ------------------------------------------------
W <- 180
FS_PT <- 7.5; FS <- FS_PT / .pt                 # geom_text 的 size
LH <- FS_PT * 25.4 / 72 * 1.18                   # 行高 3.12 mm
INK <- "#1A1A1A"; GREY <- "#4D5559"; FAM <- "Arial"
COL <- c(bio = "#6A4C93", drug = "#E0533D")      # 紫 / KRAS 珊瑚
AMBER <- "#E09F3E"
tint <- function(col, f) {                       # 向白色混 f
  v <- grDevices::col2rgb(col) / 255
  grDevices::rgb(t(v + (1 - v) * f))
}

nodes_all <- read.csv(file.path(DATA, "图九_大事记.csv"), check.names = FALSE,
                      stringsAsFactors = FALSE)
bands <- read.csv(file.path(DATA, "图九_分期.csv"), check.names = FALSE,
                  stringsAsFactors = FALSE)
stopifnot(nrow(bands) == 6)

# 只画里程碑：数据文件保留全部候选（milestone 列），图上只取 Y。
# 判据两条：① 每个阶段（I–VI）只留 2–3 条「改变了之后怎么做」的转折——新靶点、
# 新构象、新模态、首次获批；补读数的论文与重复的获批不进图。② **阴性结果不进图**：
# 2004 年 FTI+吉西他滨 III 期、CI-1040 无缓解两处是阴性/无效结论（作者 2026-10-30 定
# 「时间线只呈现阳性里程碑」），milestone 改 N、result 记 negative；结论仍留在正文 4.1。
CAND <- nrow(nodes_all)
NEG <- nodes_all[nodes_all$result == "negative", , drop = FALSE]
nd <- nodes_all[nodes_all$milestone == "Y", , drop = FALSE]
nd <- nd[!duplicated(nd[, c("year", "lane", "label")]), ]
stopifnot(nrow(nd) == 12, !any(nd$result == "negative"), !any(nd$kind == "wdr"))

# ---- 量字宽 ------------------------------------------------------------------
tmp <- tempfile(fileext = ".pdf"); grDevices::cairo_pdf(tmp, family = FAM)
plain <- function(s) gsub("[*]", "", s)
tw <- function(s, face = "plain")
  vapply(s, function(x) convertWidth(grobWidth(textGrob(plain(x), gp = gpar(
    fontfamily = FAM, fontsize = FS_PT, fontface = face))), "mm", valueOnly = TRUE), 0)
wrap <- function(s, wmax, face) {                # 按实测字宽贪心折行
  words <- strsplit(s, " ")[[1]]; out <- character(0); cur <- ""
  for (w in words) {
    if (tw(w, face) > wmax) stop(sprintf("单词超宽：%s", w))
    nxt <- if (cur == "") w else paste(cur, w)
    if (tw(nxt, face) <= wmax) cur <- nxt else { out <- c(out, cur); cur <- w }
  }
  c(out, cur)
}

# ---- 横向几何 ----------------------------------------------------------------
LBW <- 5.4                          # 左缘泳道名色带宽
LX <- LBW + 1.2; RX <- W - 0.6      # 主轴两端
BOXW <- 26.6; PADX <- 0.9; PADY <- 0.9
nd <- nd[order(nd$year, nd$kind != "lit"), ]
slots <- sort(unique(nd$year))
sx <- setNames(seq(LX + 2.6, RX - 3.4, length.out = length(slots)), slots)
nd$x <- unname(sx[as.character(nd$year)])
PITCH <- diff(sx)[1]

# 卡片：折行、算高；同泳道相邻槽位的卡片交替上下两层
gsym <- function(x) gsub("[*]([^*]+)[*]", "<i>\\1</i>", x)
nd$tl <- lapply(nd$label, wrap, BOXW - 2 * PADX, "bold")
nd$sl <- lapply(nd$tag, wrap, BOXW - 2 * PADX, "plain")
nd$h <- (lengths(nd$tl) + lengths(nd$sl)) * LH + 2 * PADY
# 排卡：同泳道相邻槽位交替两层；首张卡贴边时会被推离自己的槽位，所以起始层两种都试，
# 同层卡片只向右推开（推开后卡片仍须罩住自己的槽位），取第一种通过检查的排法。
place <- function(side, start) {
  ii <- which(nd$lane == side); sh <- integer(length(ii)); sh[1] <- start
  for (j in seq_along(ii)[-1])
    sh[j] <- if (nd$x[ii[j]] - nd$x[ii[j - 1]] < BOXW + 1) 3L - sh[j - 1] else 1L
  bx <- pmin(pmax(nd$x[ii], LX + BOXW / 2), RX - BOXW / 2)
  for (s in 1:2) {
    k <- which(sh == s)
    for (m in seq_along(k)[-1]) bx[k[m]] <- max(bx[k[m]], bx[k[m - 1]] + BOXW + 0.6)
  }
  l <- bx - BOXW / 2; r <- bx + BOXW / 2; x <- nd$x[ii]
  if (any(x < l + 1 | x > r - 1 | r > RX)) return(NULL)
  for (a in seq_along(ii)) for (b in seq_along(ii))   # 引线不得穿过更靠轴一层的卡片
    if (sh[b] < sh[a] && x[a] > l[b] - 0.8 && x[a] < r[b] + 0.8) return(NULL)
  list(ii = ii, shelf = sh, bx = bx)
}
nd$bx <- NA_real_; nd$shelf <- NA_integer_
for (side in c("bio", "drug")) {
  pl <- place(side, 1L); if (is.null(pl)) pl <- place(side, 2L)
  if (is.null(pl)) stop(sprintf("%s 泳道排不下：缩框或加层", side))
  nd$shelf[pl$ii] <- pl$shelf; nd$bx[pl$ii] <- pl$bx
}

# ---- 纵向几何（自下而上）------------------------------------------------------
GAP <- 2.2
LEG_Y <- c(2.4, 2.4 + LH * 1.15, 2.4 + LH * 2.3)  # 阶段图例三行
MARK_Y <- LEG_Y[3] + LH * 1.45                     # 标记图例一行
D_BOT <- MARK_Y + 3.4                              # 药物泳道底
hmax <- function(side, s) max(c(0, nd$h[nd$lane == side & nd$shelf == s]))
D_S2 <- D_BOT + GAP                                # 第二层卡片底
D_S1 <- D_S2 + hmax("drug", 2) + GAP               # 第一层卡片底
D_TOP <- D_S1 + hmax("drug", 1) + 3.2              # 药物泳道顶 = 阶段尺下方
ST0 <- D_TOP + 0.8; ST1 <- ST0 + 3.6               # 阶段尺
YSP <- ST1 + 2.6                                   # 主轴
YRY <- YSP + 2.9                                   # 年份行
B_BOT <- YSP + 0.0                                 # 生物学泳道底（色底从轴起）
B_S1 <- YRY + 2.6                                  # 第一层卡片底
B_S2 <- B_S1 + hmax("bio", 1) + GAP
B_TOP <- B_S2 + hmax("bio", 2) + GAP
SP <- B_TOP + 2.4; SHT <- 15.6                     # 顶部真实标尺
H <- SP + SHT + 0.6

nd$y0 <- ifelse(nd$lane == "bio", ifelse(nd$shelf == 1, B_S1, B_S2),
                ifelse(nd$shelf == 1, D_S1, D_S2))          # 卡片下沿
nd$y1 <- nd$y0 + nd$h
nd$l <- nd$bx - BOXW / 2; nd$r <- nd$bx + BOXW / 2

# ---- 检查：同层不重叠、引线不穿卡 --------------------------------------------
for (i in seq_len(nrow(nd))) for (j in seq_len(nrow(nd))) {
  if (i == j || nd$lane[i] != nd$lane[j]) next
  if (i < j && nd$shelf[i] == nd$shelf[j] && nd$l[j] < nd$r[i] + 0.5 && nd$l[i] < nd$r[j] + 0.5)
    stop(sprintf("卡片重叠：%s / %s", nd$label[i], nd$label[j]))
  # i 的引线从轴走到 i 的卡片；若 j 在更靠轴的一层，引线不得穿过 j
  if (nd$shelf[j] < nd$shelf[i] && nd$x[i] > nd$l[j] - 0.8 && nd$x[i] < nd$r[j] + 0.8)
    stop(sprintf("引线穿卡：%s 穿过 %s", nd$label[i], nd$label[j]))
}

# ---- 阶段：分界落在两个槽位之间 -----------------------------------------------
bs <- bands
bs$sa <- sapply(seq_len(nrow(bs)), function(i) {
  v <- sx[slots >= bs$y0[i] & slots < bs$y1[i]]; if (length(v)) min(v) else NA })
bs$sb <- sapply(seq_len(nrow(bs)), function(i) {
  v <- sx[slots >= bs$y0[i] & slots < bs$y1[i]]; if (length(v)) max(v) else NA })
bs$nlab <- as.character(as.roman(seq_len(nrow(bs))))
bs <- bs[!is.na(bs$sa), , drop = FALSE]
stopifnot(nrow(bs) == 6)
edges <- c(LX, (bs$sb[-nrow(bs)] + bs$sa[-1]) / 2, RX)
bs$e0 <- edges[-length(edges)]; bs$e1 <- edges[-1]
bs$fill <- rep(c(tint(AMBER, 0.35), tint(AMBER, 0.68)), length.out = nrow(bs))

# ---- 顶部真实标尺 --------------------------------------------------------------
Y0 <- 1962; Y1 <- 2028
SX <- (RX - LX - 2) / (Y1 - Y0)
xof <- function(yr) LX + 1 + (yr - Y0) * SX
S_AX <- SP + 5.0
rug <- unique(data.frame(x = xof(nd$year), lane = nd$lane, kind = nd$kind,
                         y = ifelse(nd$lane == "bio", SP + 12.0, SP + 8.4)))
tks <- data.frame(year = seq(1970, 2020, 10)); tks$x <- xof(tks$year)

SHAPE <- c(lit = 21, pivot = 23, reg = 22)
SIZE <- c(lit = 2.6, pivot = 3.6, reg = 2.6)

txt <- function(p, x, y, label, face = "plain", col = INK, hjust = 0.5, angle = 0)
  p + annotate("text", x = x, y = y, label = label, fontface = face, colour = col,
               hjust = hjust, vjust = 0.5, angle = angle, size = FS, family = FAM)

p <- ggplot() + coord_fixed(xlim = c(0, W), ylim = c(0, H), expand = FALSE) +
  theme_void(base_family = FAM) + theme(legend.position = "none")

# 顶部标尺
p <- p + annotate("rect", xmin = LX, xmax = RX, ymin = SP, ymax = SP + SHT,
                  fill = "#F3F1EF", colour = NA) +
  annotate("rect", xmin = 0, xmax = LBW, ymin = SP, ymax = SP + SHT, fill = GREY) +
  annotate("segment", x = LX + 1, xend = RX - 1, y = S_AX, yend = S_AX,
           colour = GREY, linewidth = 0.4) +
  annotate("segment", x = tks$x, xend = tks$x, y = S_AX, yend = S_AX - 0.9,
           colour = GREY, linewidth = 0.4)
p <- txt(p, LBW / 2, SP + SHT / 2, "True scale", "bold", "white", angle = 90)
p <- txt(p, tks$x, SP + 2.2, tks$year, col = GREY)
p <- p + geom_point(data = rug, aes(x = x, y = y, shape = I(SHAPE[kind]),
                                    size = I(SIZE[kind] * 0.78), fill = I(COL[lane])),
                    colour = "white", stroke = 0.35)

# 泳道底色与左缘色带
lanes <- data.frame(lane = c("bio", "drug"), y0 = c(B_BOT, D_BOT), y1 = c(B_TOP, D_TOP),
                    lab = c("Biology & structure", "Drugs & approvals"))
p <- p + annotate("rect", xmin = LX, xmax = RX, ymin = lanes$y0, ymax = lanes$y1,
                  fill = tint(COL[lanes$lane], 0.9), colour = NA) +
  annotate("rect", xmin = 0, xmax = LBW, ymin = lanes$y0, ymax = lanes$y1,
           fill = COL[lanes$lane], colour = NA)
p <- txt(p, LBW / 2, (lanes$y0 + lanes$y1) / 2, lanes$lab, "bold", "white", angle = 90)

# 引线（先画，阶段尺与卡片压在上面）
bio <- nd$lane == "bio"
p <- p + annotate("segment", x = nd$x[bio], xend = nd$x[bio], y = YRY + 1.8,
                  yend = nd$y0[bio], colour = COL[["bio"]], linewidth = 0.4) +
  annotate("segment", x = nd$x[!bio], xend = nd$x[!bio], y = YSP,
           yend = nd$y1[!bio], colour = COL[["drug"]], linewidth = 0.4)

# 阶段尺
p <- p + annotate("rect", xmin = bs$e0 + 0.25, xmax = bs$e1 - 0.25, ymin = ST0, ymax = ST1,
                  fill = bs$fill, colour = NA)
p <- txt(p, (bs$e0 + bs$e1) / 2, (ST0 + ST1) / 2, bs$nlab, "bold")

# 主轴、年份、节点
p <- p + annotate("segment", x = LX, xend = RX, y = YSP, yend = YSP, colour = INK,
                  linewidth = 0.7)
p <- txt(p, sx, YRY, names(sx), "bold")
p <- p + geom_point(data = nd, aes(x = x, y = YSP, shape = I(SHAPE[kind]),
                                   size = I(SIZE[kind]), fill = I(COL[lane])),
                    colour = "white", stroke = 0.5)

# 卡片
p <- p + annotate("rect", xmin = nd$l, xmax = nd$r, ymin = nd$y0, ymax = nd$y1,
                  fill = "white", colour = COL[nd$lane],
                  linewidth = ifelse(nd$kind == "pivot", 0.9, 0.45))
lines <- do.call(rbind, lapply(seq_len(nrow(nd)), function(i) {
  t <- nd$tl[[i]]; s <- nd$sl[[i]]
  lab <- c(sprintf("<b>%s</b>", gsym(t)),
           sprintf("<span style='color:%s'>%s</span>", GREY, s))
  data.frame(x = nd$bx[i], y = nd$y1[i] - PADY - LH * (seq_along(lab) - 0.5), lab = lab)
}))
p <- p + geom_richtext(data = lines, aes(x = x, y = y, label = lab), size = FS,
                       family = FAM, colour = INK, fill = NA, label.colour = NA,
                       label.padding = unit(0, "mm"), hjust = 0.5, vjust = 0.5)

# ---- 图例 ----------------------------------------------------------------------
legm <- data.frame(kind = c("lit", "pivot", "reg"), lane = c("bio", "bio", "drug"),
                   lab = c("Publication cited in the text", "Switch-II pocket (2013)",
                           "Regulatory approval"))
gapx <- 5.0; xs <- LX + 1.6
for (i in seq_len(nrow(legm))) {
  p <- p + annotate("point", x = xs, y = MARK_Y, shape = SHAPE[[legm$kind[i]]],
                    size = SIZE[[legm$kind[i]]], fill = COL[[legm$lane[i]]],
                    colour = "white", stroke = 0.5)
  p <- txt(p, xs + 2.6, MARK_Y, legm$lab[i], hjust = 0)
  xs <- xs + 2.6 + tw(legm$lab[i]) + gapx
}
if (xs - gapx > W) stop("标记图例越界")

COLX <- c(LX, LX + (RX - LX) / 2)
for (i in seq_len(nrow(bs))) {
  cx <- COLX[(i - 1) %/% 3 + 1]; cy <- rev(LEG_Y)[(i - 1) %% 3 + 1]
  p <- p + annotate("rect", xmin = cx, xmax = cx + 5.2, ymin = cy - 1.45, ymax = cy + 1.45,
                    fill = bs$fill[i], colour = NA)
  p <- txt(p, cx + 2.6, cy, bs$nlab[i], "bold")
  yr <- if (bs$y1[i] - bs$y0[i] <= 1) sprintf("%d–", bs$y0[i]) else
    sprintf("%d–%d", bs$y0[i], bs$y1[i])
  p <- txt(p, cx + 6.6, cy, yr, "bold", hjust = 0)
  lab <- gsub("\"([^\"]+)\"", "“\\1”", bs$name[i])
  p <- txt(p, cx + 6.6 + tw("0000–0000", "bold") + 1.6, cy, lab, hjust = 0)
  if (cx + 6.6 + tw("0000–0000", "bold") + 1.6 + tw(lab) > c(COLX[2] - 2, W)[(i - 1) %/% 3 + 1])
    stop("阶段图例越界")
}
invisible(dev.off()); unlink(tmp)

# ---- 输出 ----------------------------------------------------------------------
base <- file.path(OUT, "Fig9_RAS_milestones_timeline")
grDevices::cairo_pdf(paste0(base, ".pdf"), mm(W), mm(H), family = FAM); print(p); invisible(dev.off())
if (requireNamespace("svglite", quietly = TRUE)) {
  svglite::svglite(paste0(base, ".svg"), mm(W), mm(H), bg = "white"); print(p); invisible(dev.off())
}
png(paste0(base, ".png"), mm(W), mm(H), units = "in", res = 600, type = "cairo",
    family = FAM, bg = "white"); print(p); invisible(dev.off())
cat(sprintf("-> figures/Fig9_RAS_milestones_timeline.{pdf,svg,png}  %d x %0.1f mm\n", W, H))
cat(sprintf("自查：%d 里程碑（候选 %d 条，阴性共 %d 条未上轴）/ %d 槽位；上 %d 层、下 %d 层；槽距 %0.2f mm；标尺 %0.2f mm/年\n",
            nrow(nd), CAND, nrow(NEG), length(slots), max(nd$shelf[bio]), max(nd$shelf[!bio]),
            PITCH, SX))
