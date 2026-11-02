#!/usr/bin/env Rscript
# Geographic distribution of RAS-related oncology trials registered on
# ClinicalTrials.gov.  Same submission contract as the rest of this project:
# 180 mm double-column canvas, Arial, English only, no in-figure title,
# lower-case bold panel letters, PDF + SVG (live text) + PNG preview.
#
# Usage: Rscript 03_figures_country.R <root>

suppressPackageStartupMessages({
  library(ggplot2); library(maps); library(patchwork); library(scales)
  library(ggrepel)
})

root <- commandArgs(trailingOnly = TRUE)[1]
if (is.na(root)) root <- "."   # run from the RAS临床试验注册分析 directory
DATA <- file.path(root, "数据"); FIG <- file.path(root, "figures")
dir.create(FIG, showWarnings = FALSE)
mm <- function(x) x / 25.4

# ---- house style (same as Figures 1-10): one type size, house palette ------
FS_PT <- 7.5; PN_PT <- 9; FS <- FS_PT / .pt
INK <- "#1A1A1A"; GREY <- "#4D5559"; RULE <- "#D5DBDE"
# house palette: coral (KRAS, Fig 3/5), amber, wine, purple, teal, blue
HOUSE <- c(coral = "#E0533D", amber = "#E09F3E", wine = "#A3203F",
           purple = "#6A4C93", teal = "#1F8A8C", blue = "#2E86AB")
PHASE_COL <- c("Early Phase 1" = "#F3D3A1", "Phase 1" = "#E09F3E",
               "Phase 2" = "#E0533D", "Phase 3" = "#A3203F")

txt <- function(...) element_text(family = "Arial", size = FS_PT, colour = INK, ...)
base <- theme_void(base_family = "Arial", base_size = FS_PT) +
  theme(text = txt(), legend.text = txt(), legend.title = txt(face = "bold"),
        plot.margin = margin(0, 0, 0, 0, "mm"),
        plot.tag = element_text(size = PN_PT, face = "bold", family = "Arial", colour = INK))
axed <- theme_classic(base_family = "Arial", base_size = FS_PT) +
  theme(text = txt(),
        axis.line = element_line(linewidth = 0.3, colour = INK),
        axis.ticks = element_line(linewidth = 0.3, colour = INK),
        axis.ticks.length = unit(0.9, "mm"),
        axis.text = txt(), axis.title = txt(),
        axis.title.x = txt(margin = margin(1.2, 0, 0, 0, "mm")),
        axis.title.y = txt(angle = 90, margin = margin(0, 1.2, 0, 0, "mm")),
        legend.key.height = unit(2.8, "mm"), legend.key.width = unit(3.4, "mm"),
        legend.text = txt(margin = margin(0, 2.4, 0, 1, "mm")), legend.title = txt(face = "bold"),
        legend.margin = margin(0, 0, 0, 0), legend.box.spacing = unit(1, "mm"),
        legend.spacing.y = unit(0.6, "mm"),
        legend.background = element_blank(),
        plot.margin = margin(0, 1.5, 0, 0, "mm"),
        plot.tag = element_text(size = PN_PT, face = "bold", family = "Arial", colour = INK))

# ------------------------------------------------------------------ the data
cn <- read.csv(file.path(DATA, "表3_国家分布.csv"), check.names = FALSE)
names(cn) <- gsub(" ", "_", names(cn))
tr <- read.csv(file.path(DATA, "表1_临床试验总表.csv"), check.names = FALSE)

# registry spelling  ->  polygon name in maps::world.  Hong Kong has no polygon
# of its own in that database, so for the map only it is merged into China; the
# tables keep it as a separate registry entry.
XW <- c("United States" = "USA", "United Kingdom" = "UK",
        "Czechia" = "Czech Republic", "Turkey (Türkiye)" = "Turkey",
        "Hong Kong" = "China")
cn$map_region <- ifelse(cn$country %in% names(XW), XW[cn$country], cn$country)
write.csv(cn[, c("country", "map_region", "n_trials", "n_sites")],
          file.path(DATA, "表13_国家名_地图多边形对照.csv"), row.names = FALSE)

world <- map_data("world")
world <- world[world$region != "Antarctica", ]
agg <- aggregate(cbind(n_trials, n_sites) ~ map_region, cn, sum)
stopifnot(all(agg$map_region %in% world$region))
world$n <- agg$n_trials[match(world$region, agg$map_region)]
world$n[is.na(world$n)] <- 0            # no registered site, not missing data

BRK <- c(0, 1, 2, 6, 11, 26, 51, 101, Inf)
LAB <- c("0", "1", "2–5", "6–10", "11–25", "26–50", "51–100", ">100")
world$bin <- cut(world$n, BRK, labels = LAB, right = FALSE)
# warm sequential ramp in the house palette: sand -> amber -> coral -> wine
FILL <- setNames(c("#ECEEEF", "#FBE8D3", "#F6D0A6", "#F0AF78", "#E98654",
                   "#E0533D", "#C23B3B", "#A3203F"), LAB)

# label anchors: every label sits on sea or on a pale (0-trial) land mass so it
# stays legible; hj = 0 left-aligned, 1 right-aligned, 0.5 centred
lab_pts <- data.frame(
  country = c("United States", "Canada", "China", "Japan", "South Korea",
              "Australia", "United Kingdom", "France", "Spain", "Italy", "Germany"),
  lon = c(-100, -106,  104, 139, 128,  134, -2,  2.5, -4,   13, 10.5),
  lat = c(  40,   58,   35,  36, 36.5, -25, 53,  47,  40, 42.5, 51),
  nx  = c(-132,  -40,   80, 150, 137,  134, -24, -24, -24,  14,  14),
  ny  = c(  26,   74,   47,  44,  21,  -47,  60,  49,  37,  22,  73),
  hj  = c(   1,    0,    1,   0,   0,  0.5,   1,   1,   1, 0.5, 0.5))
lab_pts$n <- cn$n_trials[match(lab_pts$country, cn$country)]
lab_pts$txt <- paste0(sub("United States", "USA",
                          sub("United Kingdom", "UK", lab_pts$country)),
                      " **", lab_pts$n, "**")
# the leader stops just short of the text: beside it for left/right-aligned
# labels, under or over it for centred ones
lab_pts$ex <- with(lab_pts, ifelse(hj == 1, nx + 1, ifelse(hj == 0, nx - 1, nx)))
lab_pts$ey <- with(lab_pts, ifelse(hj == 0.5, ny + ifelse(ny > lat, -2.2, 2.2), ny))

pa <- ggplot() +
  geom_polygon(data = world, aes(long, lat, group = group, fill = bin),
               colour = "white", linewidth = 0.1) +
  geom_segment(data = lab_pts, aes(x = lon, y = lat, xend = ex, yend = ey),
               linewidth = 0.3, colour = INK) +
  geom_point(data = lab_pts, aes(lon, lat), size = 0.9, shape = 21,
             fill = "white", colour = INK, stroke = 0.3) +
  ggtext::geom_richtext(data = lab_pts, aes(nx, ny, label = txt, hjust = hj),
                        family = "Arial", size = FS, colour = INK, vjust = 0.5,
                        fill = NA, label.colour = NA,
                        label.padding = unit(0, "mm"), label.margin = unit(0, "mm")) +
  scale_fill_manual(values = FILL, drop = FALSE, na.translate = FALSE,
                    name = "Trials with\n≥ 1 site",
                    guide = guide_legend(ncol = 1, reverse = TRUE,
                                         keywidth = unit(3.6, "mm"),
                                         keyheight = unit(2.9, "mm"))) +
  coord_fixed(1.33, xlim = c(-168, 182), ylim = c(-57, 84), expand = FALSE) +
  base + theme(legend.position = "inside",
               legend.position.inside = c(0.003, 0.02),
               legend.justification = c(0, 0),
               legend.title = txt(face = "bold", margin = margin(0, 0, 1, 0, "mm")),
               legend.text = txt(margin = margin(0, 0, 0, 1, "mm")),
               legend.key.spacing.y = unit(0.25, "mm"),
               panel.background = element_rect(fill = "white", colour = NA))

# ------------------------------- panel b: top 25 countries, stacked by phase
pc <- do.call(rbind, lapply(seq_len(nrow(tr)), function(i) {
  cs <- trimws(strsplit(tr$countries[i], ";")[[1]])
  cs <- cs[nzchar(cs)]
  if (!length(cs)) return(NULL)
  data.frame(country = cs, phase = tr$phase_group[i],
             tier = tr$ras_tier[i], year = tr$first_posted_year[i])
}))
pc$phase <- factor(pc$phase, levels = names(PHASE_COL))

ord <- names(sort(table(pc$country), decreasing = TRUE))
top <- ord[1:25]
b <- as.data.frame(table(country = pc$country, phase = pc$phase))
b <- b[b$country %in% top, ]
b$country <- factor(as.character(b$country), levels = rev(top))
tot <- aggregate(Freq ~ country, b, sum)
short <- function(x) sub("Turkey \\(Türkiye\\)", "Türkiye", x)

pb <- ggplot(b, aes(Freq, country, fill = phase)) +
  geom_col(width = 0.7, linewidth = 0) +
  geom_text(data = tot, aes(Freq + 8, country, label = Freq), inherit.aes = FALSE,
            hjust = 0, size = FS, family = "Arial", colour = INK) +
  scale_fill_manual(values = PHASE_COL, name = "Highest phase",
                    guide = guide_legend(ncol = 1, reverse = TRUE)) +
  scale_x_continuous("Number of trials", expand = expansion(c(0, 0.1)),
                     breaks = seq(0, 600, 200)) +
  scale_y_discrete(NULL, labels = short, expand = expansion(add = 0.6)) +
  axed + theme(legend.position = "inside", legend.position.inside = c(0.98, 0.04),
               legend.justification = c(1, 0),
               axis.ticks.y = element_blank(),
               panel.grid.major.x = element_line(linewidth = 0.2, colour = RULE))

# ------------------------------- panel c: when each region came on line
top6 <- ord[1:6]
yr <- pc[pc$country %in% top6 & nzchar(pc$year), ]
yr$year <- as.integer(yr$year)
cc <- as.data.frame(table(country = yr$country, year = yr$year))
cc$year <- as.integer(as.character(cc$year))
cc <- cc[order(cc$country, cc$year), ]
cc$cum <- unlist(lapply(split(cc$Freq, cc$country), cumsum))
cc$country <- factor(as.character(cc$country), levels = top6)
LINE <- setNames(unname(HOUSE[c("coral", "wine", "amber", "teal", "purple", "blue")]), top6)
ends <- do.call(rbind, lapply(split(cc, cc$country), function(d) d[nrow(d), ]))

pcc <- ggplot(cc, aes(year, cum, colour = country)) +
  geom_line(linewidth = 0.75, lineend = "round") +
  ggrepel::geom_text_repel(
    data = ends, aes(label = sub("United States", "USA", country)),
    hjust = 0, nudge_x = 0.9, direction = "y", size = FS, family = "Arial",
    fontface = "bold", segment.size = 0.25, segment.colour = GREY,
    min.segment.length = 0.2, box.padding = 0.05, point.padding = 0,
    max.overlaps = Inf, seed = 1, show.legend = FALSE) +
  scale_colour_manual(values = LINE, guide = "none") +
  scale_x_continuous("Year first posted",
                     limits = c(min(cc$year), max(cc$year) + 6.5),
                     breaks = seq(2000, 2025, 5), expand = expansion(c(0.01, 0))) +
  scale_y_continuous("Cumulative trials", breaks = seq(0, 600, 200),
                     expand = expansion(c(0.01, 0.04))) +
  axed + theme(panel.grid.major.y = element_line(linewidth = 0.2, colour = RULE))

# ------------------------------- panel d: RAS-directed share, top 15 countries
top15 <- ord[1:15]
sh <- as.data.frame(table(country = pc$country, tier = pc$tier))
sh <- sh[sh$country %in% top15, ]
sh$country <- factor(as.character(sh$country), levels = rev(top15))
TIER <- c("RAS-targeted" = HOUSE[["coral"]], "RAS-regulator-targeted" = HOUSE[["teal"]],
          "RAS-biomarker-selected" = HOUSE[["amber"]], "RAS-mentioned" = "#C9CED2")
sh$tier <- factor(sh$tier, levels = rev(names(TIER)))

pd <- ggplot(sh, aes(Freq, country, fill = tier)) +
  geom_col(width = 0.7, position = "fill", linewidth = 0) +
  scale_fill_manual(values = TIER, name = NULL, breaks = names(TIER),
                    guide = guide_legend(nrow = 2, byrow = TRUE)) +
  scale_x_continuous("Share of trials", labels = percent_format(1),
                     breaks = seq(0, 1, 0.25), expand = expansion(c(0, 0.01))) +
  scale_y_discrete(NULL, labels = short, expand = expansion(add = 0.6)) +
  axed + theme(legend.position = "bottom", legend.justification = c(0, 0),
               legend.location = "plot", legend.box.spacing = unit(1.2, "mm"),
               axis.ticks.y = element_blank())

# ------------------------------------------------------------------- assembly
save_fig <- function(plot, name, w, h) {
  for (dev in c("pdf", "svg", "png")) {
    f <- file.path(FIG, paste0(name, ".", dev))
    if (dev == "pdf") grDevices::cairo_pdf(f, mm(w), mm(h), family = "Arial")
    if (dev == "svg") {
      # svglite keeps the labels as live <text>; the cairo svg device would
      # convert every glyph to a path and the figure could no longer be edited.
      if (requireNamespace("svglite", quietly = TRUE))
        svglite::svglite(f, mm(w), mm(h), bg = "white")
      else grDevices::svg(f, mm(w), mm(h), family = "Arial", bg = "white")
    }
    if (dev == "png") grDevices::png(f, mm(w), mm(h), units = "in", res = 600,
                                     type = "cairo", family = "Arial", bg = "white")
    print(plot); dev.off()
  }
  cat(sprintf("  -> %-42s %3.0f x %3.0f mm\n", name, w, h))
}

# Word column is 14.5 cm wide, so the 180 mm canvas prints at 0.81 (7.5 pt -> 6 pt,
# the same as every other figure); 205 mm tall leaves room for title and legend
# on the same page without the figure being shrunk a second time.
MAP_H <- 176 * 141 * 1.33 / 350          # 350 deg x 141 deg at aspect 1.33, 176 mm wide
layout <- "
AA
BC
BD
"
# `free(pa)` releases the map from the column alignment (otherwise it is lined
# up with b's country gutter and shrinks); b spans both right-hand rows.
fig <- free(pa, side = "lr") + pb + free(pcc, type = "label", side = "l") + pd +
  plot_layout(design = layout, heights = c(MAP_H + 4, 45, 54), widths = c(1, 1)) +
  plot_annotation(tag_levels = "a") &
  theme(plot.tag.position = c(0, 1),
        plot.tag = element_text(size = PN_PT, face = "bold", family = "Arial",
                                colour = INK, hjust = 0, vjust = 1))

FIG_H <- 205
save_fig(fig, "Figure_RAS_trials_global_distribution", 180, FIG_H)
save_fig(pa, "FigurePanel_a_world_map", 180, MAP_H + 2)
save_fig(pb, "FigurePanel_b_top25_by_phase", 88, 104)
save_fig(pcc, "FigurePanel_c_cumulative_by_year", 88, 50)
save_fig(pd, "FigurePanel_d_tier_composition", 88, 60)

# -------------------------------------------------- numbers quoted in the text
cat("\nfigure-level checks\n")
cat("  trial-country pairs      :", nrow(pc), "\n")
cat("  distinct trials with site:", length(unique(paste(tr$nct_id[nzchar(tr$countries)]))), "\n")
cat("  countries on the map     :", nrow(agg), "of", nrow(cn), "registry entries\n")
cat("  top 5                    :", paste(sprintf("%s=%d", ord[1:5],
      as.integer(sort(table(pc$country), decreasing = TRUE)[1:5])), collapse = ", "), "\n")
cat("  US share of pairs        :", sprintf("%.1f%%", 100 * sum(pc$country == "United States") / nrow(pc)), "\n")
cat("  single-country trials    :", sum(tr$is_multinational == "no" & nzchar(tr$countries)), "\n")
