#!/usr/bin/env Rscript
# 图10（图件基名 Fig9_RAS_milestones_timeline）：历史大事记时间线，v4。
#
# v3 → v4 只动作者点名的两件事，版式骨架不变（等距主轴 + 顶部真实标尺）：
#   ① 只留阳性里程碑。2004 年那两项（FTI+吉西他滨 III 期阴性、CI-1040 无缓解）
#      是阴性结果，不占时间线；`milestone` 改 N、`result` 记 negative，规则写进本文件。
#      14 条 → 12 条，槽位 22 → 12（2004 一撤，整年没有节点，槽位随之消失）。
#   ② 元素看得清、配色重挑：引线 grey80/0.15 → grey55/0.30；卡片描边 grey90/0.22 →
#      grey78/0.30；年份移到轴线上方单独一行、引线从年份上方起笔（不再穿字）；阶段号
#      改成压轴的浅色圆角签（在轴下方，只标中心，不做等宽条带，免得把「槽位宽度＝
#      节点数」读成「宽度＝年数」）；顶部标尺不再重复分期，只做同 12 个节点的压缩镜像，
#      两泳道各占一行。全部文字 Arial（PDF 只内嵌 ArialMT/Arial-BoldMT/Arial-ItalicMT）。
#
# 数据：数据/图九_大事记.csv（33 条候选，milestone=Y 的 12 条上）＋ 数据/图九_分期.csv。
# 用法：Rscript 11_fig9_timeline.R <示意图项目根>            （默认配色 A，写入 figures/）
#       PAL=B Rscript 11_fig9_timeline.R <示意图项目根>      （换配色重出；样张路径已废弃）
# 出图：<根>/figures/Fig9_RAS_milestones_timeline.{pdf,svg,png}（这是交付图件，由本脚本生成）
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(grid); library(ggtext)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")           # 交付图件由本脚本生成，make 会重跑
dir.create(OUT, showWarnings = FALSE)
mm <- function(x) x / 25.4
pt <- function(x) x / .pt

# ---- 配色 --------------------------------------------------------------------
# 两色同明度带（L* 30–45）、低饱和、色相相隔 55–65°，沿「冷 → 暖土」走；浅带取同色系
# 极浅一档，不用纯白。三款都能过黑白打印（两色明度差 ≥ 12）。
PALS <- list(
  A = c(bio = "#0F5B75", drug = "#A9502F", band = "#EDF2F4"),   # 深青 + 砖红（默认）
  B = c(bio = "#2E4B6E", drug = "#BE7238", band = "#F3F1EA"),   # 墨蓝 + 赭橙
  C = c(bio = "#1D4E42", drug = "#B85C3C", band = "#EDF1EA"))   # 墨绿 + 陶土

# ---- 版式（全部 mm，画在 mm 坐标里）-------------------------------------------
W <- 180; H <- 101
LX <- 13; RX <- 168                # 轴线两端；左边 0–13 mm 留给竖排泳道名
YSP <- 50                          # 主轴 y
YRY <- 52.6                        # 年份行中心（轴线正上方）
YLEAD <- 54.2                      # 生物学引线起点：从年份上方起笔，不穿字
STEP_B <- 12.6; STEP_D <- 12.4     # 层间距（生物卡最多五行、药物卡最多四行）
BOXW <- 17.8                       # 标签框宽（槽距 13.65，上下两层交替，两张卡最宽可到 26 mm）
SP <- 85; SHT <- 12                # 顶部标尺的下沿与高度（顶部留白 4 mm）
BIO0 <- 62.8                       # 生物学泳道第一层
DRUG0 <- 39.6                      # 药物泳道第一层
Y0 <- 1962; Y1 <- 2030
SX <- (RX - LX) / (Y1 - Y0)        # 标尺 2.28 mm/年
xof <- function(yr) LX + (yr - Y0) * SX

TS <- 5.4; TT <- 4.8               # 卡片标题 / 出处字号
INK <- "#111111"; SUB <- "#6B6B6B"   # 正文墨色 / 次要文字（对比度 5.9:1）

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
nodes <- nodes_all[nodes_all$milestone == "Y", , drop = FALSE]
stopifnot(nrow(nodes) == 12)
stopifnot(!any(nodes$result == "negative"))
stopifnot(!any(nodes$kind == "wdr"))    # 撤销的适应证已在数据层排除

build <- function(PAL) {
  COL <- PALS[[PAL]]
  nd <- nodes
  nd$shape <- ifelse(nd$kind == "pivot", 23, ifelse(nd$kind == "reg", 22, 19))
  nd$psize <- ifelse(nd$kind == "pivot", 2.8, 2.1)

  # ---- 序数主轴：每个「有节点的年份」一个等距槽位 ------------------------------
  slots <- sort(unique(nd$year))                        # 12 个
  sx <- seq(LX + 2.4, RX - 2.4, length.out = length(slots))
  names(sx) <- slots
  nd$x <- sx[as.character(nd$year)]

  free_center <- function(occ, x, w, lo, hi) {
    if (is.null(occ)) occ <- matrix(numeric(0), 0, 2)
    occ <- matrix(occ, ncol = 2)
    occ <- occ[order(occ[, 1]), , drop = FALSE]
    gaps <- if (nrow(occ) == 0) matrix(c(lo - w / 2, hi + w / 2), 1, 2) else {
      cbind(c(lo - w / 2, occ[, 2]), c(occ[, 1], hi + w / 2))
    }
    ok <- which(gaps[, 2] - gaps[, 1] >= w)
    if (!length(ok)) return(NA_real_)
    cand <- pmin(pmax(x, gaps[ok, 1] + w / 2), gaps[ok, 2] - w / 2)
    cand <- pmin(pmax(cand, lo), hi)
    cand[which.min(abs(cand - x))]
  }

  # 基因符号斜体、蛋白正体（图注撰写须知第 8 条）：数据文件里写 markdown 的 *KRAS*，
  # 这里换成 <i>，因为整串文字已包在 <b>/<span> 里，ggtext 不再解析 HTML 标签内的 markdown
  gsym <- function(x) gsub("\\*([^*]+)\\*", "<i>\\1</i>", x)
  nd$txt <- sprintf("<b>%s</b><br><span style='font-size:%0.1fpt;color:%s'>%s</span>",
                    gsym(nd$label), TT, SUB, gsym(nd$tag))
  nd <- nd[order(nd$year, nd$kind != "lit"), ]
  nd$shelf <- NA_integer_; nd$bx <- NA_real_
  for (side in c("bio", "drug")) {
    occ <- vector("list", 4)
    for (i in which(nd$lane == side)) {
      best <- NULL
      for (s in seq_len(4)) {
        bc <- free_center(occ[[s]], nd$x[i], BOXW + 0.7, LX + 0.9 + BOXW / 2,
                          RX - 0.9 - BOXW / 2)
        if (is.na(bc)) next
        # 同层内尽量按年份从左到右：允许回退会让后一年的卡片坐到前一年左边、两根
        # 引线交叉；做成软约束，落不进去时才回退
        back <- if (is.null(occ[[s]])) 0 else max(0, max(occ[[s]][, 2]) + 0.7 - (bc - BOXW / 2))
        cost <- abs(bc - nd$x[i]) + 0.5 * (s - 1) + 9 * back
        if (is.null(best) || cost < best$cost) best <- list(s = s, bx = bc, cost = cost)
      }
      if (is.null(best)) stop("排不下：加层或缩框")
      nd$shelf[i] <- best$s; nd$bx[i] <- best$bx
      old <- if (is.null(occ[[best$s]])) matrix(numeric(0), 0, 2) else matrix(occ[[best$s]], ncol = 2)
      occ[[best$s]] <- rbind(old, c(best$bx - BOXW / 2, best$bx + BOXW / 2))
    }
  }
  nd$by <- ifelse(nd$lane == "bio", BIO0 + (nd$shelf - 1) * STEP_B,
                  DRUG0 - (nd$shelf - 1) * STEP_D)
  # 卡片高度按最坏情况估：生物泳道三行题＋一行出处 ≈ 12.6 mm，药物泳道四行 ≈ 10.6 mm
  HB <- 6.4; HD <- 5.4
  if (any(nd$by[nd$lane == "bio"] + HB > SP - 2.2))
    stop("生物学泳道卡片顶到标尺：减层或缩框")
  if (any(nd$by[nd$lane == "drug"] - HD < 21.2))
    stop("药物泳道卡片压到图例：减层或缩框")

  # ---- 阶段：轴下浅色圆角签，只标中心 ------------------------------------------
  bs <- bands
  bs$sa <- sapply(seq_len(nrow(bs)), function(i) {
    v <- sx[slots >= bs$y0[i] & slots < bs$y1[i]]
    if (length(v)) min(v) else NA
  })
  bs$sb <- sapply(seq_len(nrow(bs)), function(i) {
    v <- sx[slots >= bs$y0[i] & slots < bs$y1[i]]
    if (length(v)) max(v) else NA
  })
  bs <- bs[!is.na(bs$sa), , drop = FALSE]
  bs$nlab <- as.character(as.roman(seq_len(nrow(bs))))
  # 阶段分界落在两个槽位之间：序数轴上「换阶段」不在某一个槽位上
  bdiv <- data.frame(x = sapply(seq_len(nrow(bs) - 1),
                                function(i) (bs$sb[i] + bs$sa[i + 1]) / 2))
  # 圆角签落在「两段分界之间」的中点，而不是节点中点——签代表一段，不代表一个节点
  edges <- c(LX - 1.5, bdiv$x, RX + 1.5)
  bs$cx <- (edges[-length(edges)] + edges[-1]) / 2
  bs$e0 <- edges[-length(edges)]; bs$e1 <- edges[-1]

  yr_ax <- data.frame(x = sx, year = slots)

  # ---- 顶部真实标尺：线性，两泳道各一行 ---------------------------------------
  rug <- data.frame(x = xof(nd$year), lane = nd$lane, shape = nd$shape, psize = nd$psize,
                    y = ifelse(nd$lane == "bio", SP + 9.0, SP + 4.4))
  rug <- rug[!duplicated(rug[, c("x", "lane", "shape")]), ]
  tks <- data.frame(year = c(1964, 1980, 2000, 2020))
  tks$x <- xof(tks$year)

  p <- ggplot() +
    # 顶部标尺：只做「同一批节点在真实时间上被压成什么样」，不重复分期
    geom_rect(aes(xmin = LX, xmax = RX, ymin = SP, ymax = SP + SHT),
              fill = unname(COL[["band"]]), colour = NA) +
    geom_segment(aes(x = LX, xend = RX, y = SP, yend = SP), colour = "grey65", linewidth = 0.3) +
    geom_segment(aes(x = LX, xend = RX, y = SP + SHT, yend = SP + SHT),
                 colour = "grey65", linewidth = 0.3) +
    geom_segment(data = tks, aes(x = x, xend = x, y = SP, yend = SP + 0.9),
                 colour = "grey55", linewidth = 0.3) +
    geom_text(data = tks, aes(x = x, y = SP + 1.9, label = paste0(year)),
              size = pt(5.2), family = "Arial", colour = "grey35") +
    geom_point(data = rug, aes(x = x, y = y, shape = shape, size = I(psize * 0.62),
                               colour = lane, fill = lane), stroke = 0.3, show.legend = FALSE) +
    # 主轴：轴线 → 药物泳道引线 → 阶段签 → 年份 → 标记 → 生物学引线
    geom_segment(aes(x = LX, xend = RX, y = YSP, yend = YSP), colour = "grey20",
                 linewidth = 0.6) +
    # 轴下阶段尺：浅尺只连住同一阶段的两端分界，分界短竖线顶到轴下方 1.3 mm
    geom_segment(data = bs, aes(x = e0 + 0.8, xend = e1 - 0.8, y = 47.4, yend = 47.4),
                 colour = "grey75", linewidth = 0.45) +
    geom_segment(data = bdiv, aes(x = x, xend = x, y = 45.7, yend = 48.7),
                 colour = "grey55", linewidth = 0.5) +
    geom_segment(data = nd[nd$lane == "drug", ], aes(x = x, xend = x,
                                                     y = YSP - 0.8, yend = by),
                 colour = "grey55", linewidth = 0.3) +
    geom_richtext(data = bs, aes(x = cx, y = 47.4, label = nlab),
                  size = pt(5.6), family = "Arial", colour = "grey25", fontface = "bold",
                  fill = unname(COL[["band"]]), label.colour = "grey82",
                  label.r = unit(0, "mm"),
                  label.padding = unit(c(0.4, 1.4, 0.4, 1.4), "mm")) +
    geom_text(data = yr_ax, aes(x = x, y = YRY, label = paste0(year)),
              size = pt(5.2), family = "Arial", colour = "grey30", fontface = "bold") +
    geom_segment(data = nd[nd$lane == "bio", ], aes(x = x, xend = x,
                                                    y = YLEAD, yend = by),
                 colour = "grey55", linewidth = 0.3) +
    geom_point(data = nd, aes(x = x, y = YSP, shape = shape, size = I(psize),
                              colour = lane, fill = lane), stroke = 0.35, show.legend = FALSE) +
    scale_shape_identity() +
    scale_colour_manual(values = c(bio = unname(COL[["bio"]]), drug = unname(COL[["drug"]]))) +
    scale_fill_manual(values = c(bio = unname(COL[["bio"]]), drug = unname(COL[["drug"]]))) +
    geom_textbox(data = nd, aes(x = bx, y = by, label = txt),
                 width = unit(BOXW, "mm"), size = pt(TS), family = "Arial",
                 colour = INK, fill = "white", box.colour = "grey78",
                 box.size = 0.3, box.r = unit(0.8, "mm"), halign = 0.5, valign = 0.5,
                 box.padding = unit(c(0.5, 0.7, 0.5, 0.7), "mm")) +
    # 泳道名：竖排贴左缘，读者不必先读图例才知道上下两行是什么
    geom_text(aes(x = 4.8, y = YSP + 18, label = "biology & structure"), angle = 90,
              size = pt(5.0), family = "Arial", colour = "grey45") +
    geom_text(aes(x = 4.8, y = YSP - 14, label = "drugs & approvals"), angle = 90,
              size = pt(5.0), family = "Arial", colour = "grey45") +
    coord_cartesian(xlim = c(0, W), ylim = c(0, H), expand = FALSE) +
    theme_void(base_family = "Arial") +
    # 图例必须关掉：任何 show.legend 漏掉的层都会在右侧硬挤出一栏（v4 第一次渲染就是）
    theme(legend.position = "none")

  # ---- 图例 ------------------------------------------------------------------
  leg_mark <- data.frame(x = c(13, 62, 112), y = 17.2,
                         shape = c(19, 23, 22), lane = c("bio", "bio", "drug"),
                         size = c(2.1, 2.8, 2.4))
  leg_txt <- data.frame(x = c(15.6, 64.6, 114.6), y = 17.2,
                        txt = c("a paper cited in the text", "switch-II pocket, 2013",
                                "regulatory approval"))
  leg_stage <- data.frame(
    x = c(13, 66, 120, 13, 66, 120), y = c(11.9, 11.9, 11.9, 7.2, 7.2, 7.2),
    txt = c("**I** &nbsp;1964-1982 &nbsp;viral oncogenes",
            "**II** &nbsp;1982-1990 &nbsp;human oncogene, the point mutation",
            "**III** &nbsp;1990-2013 &nbsp;“undruggable”: three indirect routes",
            "**IV** &nbsp;2013-2021 &nbsp;structure first",
            "**V** &nbsp;2021-2026 &nbsp;one allele, one state",
            "**VI** &nbsp;2026- &nbsp;beyond one allele"),
    stringsAsFactors = FALSE)
  list(p = p +
    geom_segment(aes(x = LX, xend = RX, y = 20.6, yend = 20.6), colour = "grey85",
                 linewidth = 0.3) +
    # 尺度说明从图顶挪到图底：顶部一行小字压在图上方，缺留白，读起来像页眉。
    # 放在图例块下方当脚注，与图注区同一处，位置固定，也不与标尺抢视线。
    geom_text(aes(x = LX, y = 3.2),
              label = sprintf(paste0("top strip: true scale, %0.2f mm per year \u2013 upper row biology, ",
                                     "lower row approvals (the milestones below are spaced by event, not by year)"),
                              SX),
              hjust = 0, size = pt(4.8), family = "Arial", colour = "grey45",
              fontface = "italic") +
    # 图例标记与图上同形同色（v3 这里 fill 丢了，方块和菱形只剩空框）
    geom_point(data = leg_mark, aes(x = x, y = y, shape = shape, colour = lane,
                                    fill = lane), size = leg_mark$size, stroke = 0.4,
               show.legend = FALSE) +
    geom_text(data = leg_txt, aes(x = x, y = y, label = txt), hjust = 0,
              size = pt(5.2), family = "Arial", colour = "grey25") +
    geom_richtext(data = leg_stage, aes(x = x, y = y, label = txt), hjust = 0,
                  size = pt(4.9), family = "Arial", colour = "grey25",
                  fill = NA, label.colour = NA),
    nd = nd, slots = slots)
}

# ---- 输出 --------------------------------------------------------------------
write_all <- function(p, base, w = W, h = H, dpi = 600) {
  grDevices::cairo_pdf(paste0(base, ".pdf"), mm(w), mm(h), family = "Arial"); print(p); dev.off()
  if (requireNamespace("svglite", quietly = TRUE)) {
    svglite::svglite(paste0(base, ".svg"), mm(w), mm(h), bg = "white"); print(p); dev.off()
  }
  png(paste0(base, ".png"), mm(w), mm(h), units = "in", res = dpi, type = "cairo",
      family = "Arial", bg = "white"); print(p); dev.off()
}

PAL <- toupper(Sys.getenv("PAL", "A"))
if (!PAL %in% names(PALS)) PAL <- "A"

B <- build(PAL)
write_all(B$p, file.path(OUT, "Fig9_RAS_milestones_timeline"))
cat(sprintf("-> figures/Fig9_RAS_milestones_timeline.{pdf,svg,png}  %d x %d mm  配色 %s\n",
            W, H, PAL))
cat(sprintf("自查：%d 里程碑（候选 %d 条，阴性共 %d 条未上轴）/ %d 槽位；上 %d 层、下 %d 层；槽距 %0.2f mm；标尺 %0.2f mm/年\n",
            nrow(B$nd), CAND, nrow(NEG), length(B$slots),
            max(B$nd$shelf[B$nd$lane == "bio"]), max(B$nd$shelf[B$nd$lane == "drug"]),
            if (length(B$slots) > 1) min(diff(sort(unique(B$nd$x)))) else NA_real_, SX))
