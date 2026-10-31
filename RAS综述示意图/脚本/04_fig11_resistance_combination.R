#!/usr/bin/env Rscript
# 图12（图件基名 Fig11_resistance_to_combination）：耐药机制 × 联合逻辑矩阵热图
# 版本沿革：v2 定结构（矩阵热图）→ v3 去分面 → v4 回 v2 版式并修三处 → v5 换配色与列头。
# 本脚本即 v5，产出 `figures/` 的正式图件。
#
# 原图是一张「左栏九类机制、右栏五条逻辑、中间用弧线连」的映射图。弧线一多就交叉，
# 读者看不出**谁没有对上谁**——而这张图真正的论点是：九类机制里有六类只落到第 4 条
# 逻辑上；第 3 条逻辑不对应任何单一机制；第 5 条根本不在这条轴上。这三件「空」
# 在弧线图里被埋掉，在矩阵里是白的。
#
# v2 换矩阵热图：行＝九类机制（分三组），列＝五条联合逻辑，
# 格＝这条逻辑能不能直接对上这类机制（深／浅／空白三档），有对上的格写「要打哪个节点」。
# 作者定：按 v2 的版式（三组分面、整格填充）排，但有三处必须改——
#   1) 格子太大：整图 152 mm 高、九行摊开，行高 12 mm，字只占三分之一，空得慌。
#      改 118 mm，行高降到 8 mm 上下，格子缩到与字相称（不改编码方式）。
#   2) 面板 b 的条形轨道右端没跟上图对齐：b 的 x 轴留了 0–108% 的余量，
#      100% 那根线落在面板内侧 7% 处，右端比 a 短一截。改 limits 0–100、expand 0，
#      轨道右端就落在面板右边框上；再把 b 的右边距补到与 a 的右留白相等，
#      两块面板左右边框逐像素对齐。
#   3) 列头文字没对齐：五列各自居中，三行长短不一，右端那列最长、顶出去一截。
#      五列列头统一竖排（自下而上），都贴在面板顶边上，长短不再影响对齐。
#
# 数据：数据/图十一_耐药机制.csv、图十一_联合逻辑.csv、图十一_矩阵.csv、图十一_检出率.csv
#
# v5 两处（作者第二轮意见）：
#   · 配色难看、不协调：原先是蓝＋紫＋赭三色，紫是"设计感"的紫，赭又偏脏，
#     三色明度还差一截。改成同明度、同饱和度的三角：墨蓝／松绿／土黄，
#     色相相隔 60° 左右，饱和度压低，印出来像墨不像蜡笔。
#   · 列头不要竖排：改回横排，但五列统一**左对齐到列左边界**，右端不再长短不齐；
#     列头另画一层（geom_text，clip = "off"），不靠轴文字，位置可控。
#
# 用法：Rscript 04_fig11_resistance_combination.R <示意图项目根>
suppressPackageStartupMessages({
  library(ggplot2); library(patchwork); library(cowplot); library(grid)
library(dplyr); library(tidyr); library(scales)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- getwd()
DATA <- file.path(root, "数据")
OUT <- file.path(root, "figures")
dir.create(OUT, showWarnings = FALSE)
mm <- function(x) x / 25.4

mech <- read.csv(file.path(DATA, "图十一_耐药机制.csv"), check.names = FALSE,
                 stringsAsFactors = FALSE)
mat <- read.csv(file.path(DATA, "图十一_矩阵.csv"), check.names = FALSE,
                stringsAsFactors = FALSE)
det <- read.csv(file.path(DATA, "图十一_检出率.csv"), check.names = FALSE,
                stringsAsFactors = FALSE)
map <- read.csv(file.path(DATA, "图十一_对应.csv"), check.names = FALSE,
                stringsAsFactors = FALSE)
logics <- read.csv(file.path(DATA, "图十一_联合逻辑.csv"), check.names = FALSE,
                   stringsAsFactors = FALSE)

# 矩阵是三态编码，对应关系是「谁对上谁」的清单：两份必须一格不多一格不少，
# 否则改了 对应.csv 而忘了改矩阵，图上会静默少一条或凭空多一条。
stopifnot(setequal(paste0(map$from, "-", sub("^L", "", map$to)),
                   paste0(mat$mechanism, "-", mat$logic)))

GRP <- c(genetic = "Read out by sequencing", nongenetic = "Non-genetic programme",
         carrier = "Carrier (6.4)")
# 三组＝三种"可测性"，色相沿冷—冷绿—暖土走，明度压在同一档（L* 38–45），
# 白字压得住，缩到 6 mm 的格子里也不糊。PAL 可切换，便于对比后定稿。
PALS <- list(
  A = c(genetic = "#1B4965", nongenetic = "#427A6B", carrier = "#A9782F"),
  B = c(genetic = "#22405C", nongenetic = "#5C8A79", carrier = "#9C6B3F"),
  C = c(genetic = "#2C4F6B", nongenetic = "#4E8B7E", carrier = "#B08442"),
  D = c(genetic = "#2A4A5E", nongenetic = "#4E7C6F", carrier = "#9A7A4E"),
  E = c(genetic = "#33556B", nongenetic = "#6B8F80", carrier = "#A8895A"))
PAL <- Sys.getenv("PAL", "D")
GRP_COL <- PALS[[PAL]]

# 列名就把「读数」写进去：两行标签不会被版面挤错位，也不用再摆一层对齐的文字面板。
# 文字一律从 图十一_联合逻辑.csv 的 head_* 三列读，脚本只管排位与换行——列头上的
# 数字与出处曾经硬写在脚本里，一处改动就漏在另一处（2026-10-31 督导更正令第一组）。
# head_title／head_readout／head_source 依次是缩写标题、最好的临床读数、该读数的出处。
stopifnot(all(c("head_title", "head_readout", "head_source") %in% names(logics)),
          setequal(as.character(logics$logic), as.character(1:5)))
logics <- logics[order(as.integer(logics$logic)), ]
COLNAME <- setNames(
  sprintf("%s  %s\n%s\n%s", logics$logic, logics$head_title,
          logics$head_readout, logics$head_source),
  as.character(logics$logic))

# 格内文字：机制被这条逻辑针对时要打的那个节点（长名字短写，避免压格）
NODE_FIX <- c("cell state -> GPX4" = "cell state\n→ GPX4",
              "lineage programme" = "lineage\nprogramme",
              "ARAF condensates" = "ARAF\ncondensates",
              "mevalonate; ZBTB11" = "mevalonate\nZBTB11",
              "PI3K-AKT" = "PI3K-AKT", "EGFR (CRC)" = "EGFR\n(CRC)",
              "SOS1" = "SOS1", "ERK" = "ERK", "IRE1a" = "IRE1α",
              "YAP-MRAS" = "YAP-MRAS")

grid <- expand.grid(mechanism = mech$id, logic = as.character(1:5),
                    stringsAsFactors = FALSE) %>%
  left_join(mat %>% select(mechanism, logic, level, node) %>%
              mutate(logic = as.character(logic)), by = c("mechanism", "logic")) %>%
  mutate(level = ifelse(is.na(level), "none", level),
         node = ifelse(is.na(node), "", node),
         node = ifelse(node %in% names(NODE_FIX), NODE_FIX[node], node)) %>%
  left_join(mech %>% select(id, group, title), by = c("mechanism" = "id")) %>%
  mutate(group = factor(group, levels = names(GRP)),
         mechanism = factor(mechanism, levels = rev(mech$id)),
         logic = factor(logic, levels = as.character(1:5),
                        labels = unname(COLNAME)))

base <- theme_minimal(base_family = "Arial", base_size = 7) +
  theme(panel.grid = element_blank(),
        axis.text = element_text(size = 6, colour = "grey10"),
        axis.title = element_text(size = 6.6, colour = "grey10"),
        plot.margin = margin(1, 1, 1, 1, "mm"),
        plot.tag = element_text(size = 8, face = "bold", family = "Arial"))

# ---- 面板 a：矩阵
pa <- ggplot(grid, aes(logic, mechanism)) +
  # 格子略缩到 0.94：整格铺满时九行连成三片色块，看着笨重；缩一点后每格自成一块，
  # 格与格之间透出一条白发丝，空白格与有值格的分界也更干净
  geom_tile(aes(fill = group, alpha = level), colour = "grey90", linewidth = 0.28,
            width = 0.94, height = 0.94) +
  geom_text(aes(label = node), size = 1.75, family = "Arial", colour = "white",
            lineheight = 0.9) +
  scale_fill_manual(values = GRP_COL, guide = "none") +
  scale_alpha_manual(values = c(direct = 1, partial = 0.42, none = 0),
                     limits = c("direct", "partial", "none"),
                     breaks = c("direct", "partial", "none"),
                     labels = c("Answered directly", "Answered in part", "Not answered"),
                     name = "Logic answers the mechanism:",
                     drop = FALSE) +
  scale_x_discrete(expand = expansion(0)) +
  scale_y_discrete(expand = expansion(0),
                   labels = function(x) mech$title[match(x, mech$id)]) +
  labs(x = NULL, y = NULL, tag = "a") +
  guides(alpha = guide_legend(nrow = 1, title.position = "left",
                              override.aes = list(fill = "grey35"))) +
  facet_grid(group ~ ., scales = "free_y", space = "free_y", switch = "y",
             labeller = as_labeller(GRP)) +
  base +
  theme(strip.text.y.left = element_text(angle = 0, hjust = 0, size = 5.9,
                                         face = "bold", colour = "grey10"),
        strip.placement = "outside", strip.background = element_blank(),
        # 列头交给上面的 ph 条，矩阵自己的 x 轴文字一律不画
        axis.text.x = element_blank(), axis.ticks.x = element_blank(),
        axis.text.y = element_text(size = 6),
        legend.position = "bottom", legend.direction = "horizontal",
        legend.title = element_text(size = 5.6), legend.text = element_text(size = 5.4),
        legend.key.size = unit(3, "mm"), legend.margin = margin(2, 0, 0, 0),
        panel.border = element_rect(colour = "grey75", fill = NA, linewidth = 0.3))

# ---- 面板 b：两种检出口径（与原图第三段同数据、同「分母不同」的告诫）
# 标签从数据行自身拼，不按位置赋——按位置写过一次，两条就互换了
# 行标签只留「口径＋分母」，介质／瘤种／方案的细节进图注——标签一长，
# b 的标签栏就比 a 的还宽，面板只能往右挤，最后被画布切掉。
det <- det %>%
  mutate(caption = sprintf("%s, %s", label, n),
         caption = factor(caption, levels = caption[order(pct)]))

pb <- ggplot(det, aes(pct, caption)) +
  geom_col(aes(x = 100), fill = "grey95", width = 0.6) +
  geom_col(fill = "grey58", width = 0.6) +
  geom_text(aes(label = paste0(round(pct), "%")), hjust = -0.35, size = 2,
            family = "Arial", colour = "grey15") +
  # 0–100 且不留余量：灰色轨道正好铺到面板右边界，与上图矩阵右边框同一条竖线
  scale_x_continuous(limits = c(0, 100), breaks = c(0, 50, 100),
                     labels = c("0", "50", "100%"), expand = expansion(0)) +
  labs(x = "Acquired alteration detected (two denominators, not comparable)",
       y = NULL, tag = "b") +
  base +
  theme(panel.grid.major.x = element_line(linewidth = 0.2, colour = "grey92"),
        axis.text.y = element_text(size = 5.8, lineheight = 1.02),
        axis.line.x = element_line(linewidth = 0.3, colour = "grey20"),
        plot.margin = margin(2, 1, 1, 2.4, "mm"))

# 拼图：a 与 b 的面板左边界对齐。a 的行标签（九类机制名＋分面条带）比 b 的两行
# 说明宽得多，差值补成 b 的左边距；宽从 gtable 用 `layout$l` 现量。
panel_gutter <- function(p) {
  grDevices::pdf(NULL)
  on.exit(grDevices::dev.off())
  g <- ggplotGrob(p)
  l <- g$layout$l[grepl("^panel", g$layout$name)][1]
  sum(grid::convertWidth(g$widths[seq_len(l - 1)], "mm", valueOnly = TRUE))
}

# 右留白：面板列之后的所有列宽之和（刻度、轴题、边距都算）
panel_gutter_right <- function(p) {
  grDevices::pdf(NULL)
  on.exit(grDevices::dev.off())
  g <- ggplotGrob(p)
  r <- max(g$layout$r[grepl("^panel", g$layout$name)])
  if (r >= length(g$widths)) return(0)
  sum(grid::convertWidth(g$widths[seq(r + 1, length(g$widths))], "mm",
                         valueOnly = TRUE))
}

MARGIN_L <- 1
# 4.4mm 是实测残差：a 的分面条带与 b 的 tag/轴题排版差，gtable 难以完全拆开，
# 改完必用「渲染后数像素」复核（a 的面板左边框 vs b 的条起点），不靠估算收工。
# ---- 列头条：单独一块面板 ------------------------------------------------------
# 不把列头塞进矩阵面板：矩阵的 y 是离散轴，往里加数值层会把 y 轴改性质，
# 列头会按分面复制三遍（试过，整张图糊掉）。单开一条，x 用连续坐标
# （0.5–5.5，与矩阵的五个离散列一一对应），横排、左对齐到列左边界，
# 五列左缘因此齐平；右端长短不齐的问题也就不存在了。
ph <- ggplot() +
  annotate("text", x = seq_along(COLNAME) - 0.46, y = 0.5,
           label = unname(COLNAME), hjust = 0, vjust = 0.5,
           # geom_text 的 size 是毫米制（≈ ×2.83 才是 pt），这里要的是 5.15 pt
           size = 5.15 / .pt, lineheight = 1.05, family = "Arial", colour = "grey15") +
  scale_x_continuous(limits = c(0.5, 5.5), expand = expansion(0)) +
  scale_y_continuous(limits = c(0, 1), expand = expansion(0)) +
  coord_cartesian(clip = "off") +
  base + theme(axis.text = element_blank(), axis.title = element_blank(),
               panel.grid = element_blank(),
               plot.margin = margin(3, 1, 0, 1, "mm"))

# 左右都对齐：按两块面板各自量出的左留白、右留白之差补边距。差值现量，
# 不写死常数（v2 那个 −4.4 mm 是给旧标签栏调的，改一次标签就失效）。
# 先把两边的边距归到同一基准再量，否则量到的差值里含着 pb 原有的 2.4 mm，
# 补完之后正好差这一截（第一次就差了 1.23 mm，逐像素量出来的）
pa <- pa + theme(plot.margin = margin(2, 1, 0, 1, "mm"))
pb <- pb + theme(plot.margin = margin(2, 1, 1, 1, "mm"))
ph <- ph + theme(plot.margin = margin(2, 1, 0, 1, "mm"))
DL <- panel_gutter(pa) - panel_gutter(pb)
DR <- panel_gutter_right(pa) - panel_gutter_right(pb)
DLh <- panel_gutter(pa) - panel_gutter(ph)
DRh <- panel_gutter_right(pa) - panel_gutter_right(ph)
cat(sprintf("留白差：pb 左 %+.2f 右 %+.2f；ph 左 %+.2f 右 %+.2f（mm）\n",
            DL, DR, DLh, DRh))
pb <- pb + theme(plot.margin = margin(2, 1 + DR, 1, 1 + DL, "mm"))
ph <- ph + theme(plot.margin = margin(2, 1 + DRh, 0, 1 + DLh, "mm"))
fig <- cowplot::plot_grid(ph, pa, pb, ncol = 1,
                          rel_heights = c(0.105, 1, 0.24))

W <- 180
H <- Sys.getenv("HH", "112") |> as.numeric()
grDevices::cairo_pdf(file.path(OUT, "Fig11_resistance_to_combination.pdf"), mm(W), mm(H),
                     family = "Arial")
print(fig); dev.off()
if (requireNamespace("svglite", quietly = TRUE)) {
  svglite::svglite(file.path(OUT, "Fig11_resistance_to_combination.svg"), mm(W), mm(H),
                   bg = "white"); print(fig); dev.off()
}
png(file.path(OUT, "Fig11_resistance_to_combination.png"), mm(W), mm(H), units = "in",
    res = 600, type = "cairo", family = "Arial", bg = "white")
print(fig); dev.off()

cat("-> figures/Fig11_resistance_to_combination.{pdf,svg,png}\n")
cat(sprintf("自查：机制 %d / 逻辑 %d / 对上 %d 格（直接 %d、部分 %d、空 %d）；检出率 %s\n",
            n_distinct(grid$mechanism), n_distinct(grid$logic),
            sum(grid$level != "none"), sum(grid$level == "direct"),
            sum(grid$level == "partial"), sum(grid$level == "none"),
            paste0(round(det$pct), "%", collapse = " / ")))
