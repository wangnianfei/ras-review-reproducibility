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

PAL <- c(core = "#2E6F9E", hot = "#BF3100", grey = "#BFCBD4",
         mid = "#9FB4C7", dark = "#163B55", land = "#F0F3F5",
         border = "#FFFFFF", sea = "#FBFCFD")
PHASE_COL <- c("Early Phase 1" = "#D7DEE4", "Phase 1" = "#9FB4C7",
               "Phase 2" = "#2E6F9E", "Phase 3" = "#BF3100")

base <- theme_void(base_family = "Arial", base_size = 7) +
  theme(plot.margin = margin(1, 1, 1, 1, "mm"),
        legend.key.height = unit(2.6, "mm"), legend.key.width = unit(3.6, "mm"),
        legend.text = element_text(size = 5.8), legend.title = element_text(size = 6),
        plot.tag = element_text(size = 8, face = "bold", family = "Arial"))
axed <- theme_classic(base_family = "Arial", base_size = 7) +
  theme(axis.line = element_line(linewidth = 0.25, colour = "grey20"),
        axis.ticks = element_line(linewidth = 0.25, colour = "grey20"),
        axis.ticks.length = unit(0.8, "mm"),
        axis.text = element_text(size = 6, colour = "grey15"),
        axis.title = element_text(size = 7, colour = "grey10"),
        legend.key.height = unit(2.6, "mm"), legend.key.width = unit(3.0, "mm"),
        legend.text = element_text(size = 5.8), legend.title = element_text(size = 6),
        legend.margin = margin(0, 0, 0, 0), legend.box.spacing = unit(1, "mm"),
        plot.margin = margin(1, 2, 1, 1, "mm"),
        plot.tag = element_text(size = 8, face = "bold", family = "Arial"))

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
FILL <- setNames(c("#F2F4F6", "#E3EBF1", "#C3D5E2", "#9CBAD0", "#6F9BBC",
                   "#44759D", "#285C84", "#11324A"), LAB)

lab_pts <- data.frame(
  country = c("United States", "China", "Spain", "Italy", "France", "Germany",
              "United Kingdom", "South Korea", "Japan", "Australia", "Canada"),
  lon = c(-100, 104, -4, 13, 2.5, 10.5, -3.5, 128, 139, 134, -106),
  lat = c(40, 35, 40, 42.5, 47, 51, 54.5, 36.5, 36.5, -25, 58),
  nx  = c(-150, 104, -19, 30, -26, 9, -33, 141, 152, 134, -142),
  ny  = c(26, 47, 21, 59, 55, 70, 64, 21, 44, -42, 71))
lab_pts$n <- cn$n_trials[match(lab_pts$country, cn$country)]
lab_pts$txt <- paste0(sub("United States", "USA",
                          sub("United Kingdom", "UK", lab_pts$country)),
                      " ", lab_pts$n)

pa <- ggplot() +
  geom_polygon(data = world, aes(long, lat, group = group, fill = bin),
               colour = "white", linewidth = 0.12) +
  geom_segment(data = lab_pts, aes(x = lon, y = lat, xend = nx, yend = ny),
               linewidth = 0.18, colour = "grey35") +
  geom_point(data = lab_pts, aes(lon, lat), size = 0.35, colour = "grey20") +
  geom_text(data = lab_pts, aes(nx, ny, label = txt), family = "Arial",
            size = 1.95, colour = "grey10", vjust = -0.45) +
  scale_fill_manual(values = FILL, drop = FALSE, na.translate = FALSE,
                    name = "Trials with ≥ 1 site",
                    guide = guide_legend(nrow = 1, label.position = "bottom",
                                         title.position = "left",
                                         title.vjust = 0.1, keywidth = unit(5, "mm"))) +
  coord_fixed(1.33, xlim = c(-168, 182), ylim = c(-57, 84), expand = FALSE) +
  base + theme(legend.position = "bottom",
               panel.background = element_rect(fill = PAL[["sea"]], colour = NA))

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

pb <- ggplot(b, aes(Freq, country, fill = phase)) +
  geom_col(width = 0.72, linewidth = 0) +
  geom_text(data = tot, aes(Freq, country, label = Freq), inherit.aes = FALSE,
            hjust = -0.18, size = 1.9, family = "Arial", colour = "grey15") +
  scale_fill_manual(values = PHASE_COL, name = NULL,
                    guide = guide_legend(nrow = 2, byrow = TRUE, reverse = TRUE)) +
  scale_x_continuous("Number of trials", expand = expansion(c(0, 0.11)),
                     breaks = pretty_breaks(5)) +
  scale_y_discrete(NULL, labels = function(x) sub("Turkey \\(Türkiye\\)", "Türkiye", x)) +
  axed + theme(legend.position = c(0.72, 0.28),
               panel.grid.major.x = element_line(linewidth = 0.15, colour = "grey92"))

# ------------------------------- panel c: when each region came on line
top6 <- ord[1:6]
yr <- pc[pc$country %in% top6 & nzchar(pc$year), ]
yr$year <- as.integer(yr$year)
cc <- as.data.frame(table(country = yr$country, year = yr$year))
cc$year <- as.integer(as.character(cc$year))
cc <- cc[order(cc$country, cc$year), ]
cc$cum <- unlist(lapply(split(cc$Freq, cc$country), cumsum))
cc$country <- factor(as.character(cc$country), levels = top6)
LINE <- setNames(c("#BF3100", "#2E6F9E", "#1C7C54", "#E09F3E", "#6A4C93", "#6F7378"),
                 top6)
ends <- do.call(rbind, lapply(split(cc, cc$country), function(d) d[nrow(d), ]))

pcc <- ggplot(cc, aes(year, cum, colour = country)) +
  geom_line(linewidth = 0.6) +
  ggrepel::geom_text_repel(
    data = ends, aes(label = sub("United States", "USA", country)),
    hjust = 0, nudge_x = 0.6, direction = "y", size = 1.9, family = "Arial",
    segment.size = 0.15, segment.alpha = 0.6, min.segment.length = 0.1,
    box.padding = 0.08, max.overlaps = Inf, seed = 1, show.legend = FALSE) +
  scale_colour_manual(values = LINE, guide = "none") +
  scale_x_continuous("Year first posted on ClinicalTrials.gov",
                     limits = c(min(cc$year), max(cc$year) + 4.5),
                     breaks = seq(2000, 2026, 5), expand = expansion(0.01)) +
  scale_y_continuous("Cumulative trials", expand = expansion(c(0.01, 0.06))) +
  axed + theme(panel.grid.major.y = element_line(linewidth = 0.15, colour = "grey92"))

# ------------------------------- panel d: RAS-directed share, top 15 countries
top15 <- ord[1:15]
sh <- as.data.frame(table(country = pc$country, tier = pc$tier))
sh <- sh[sh$country %in% top15, ]
sh$country <- factor(as.character(sh$country), levels = rev(top15))
sh$tier <- factor(sh$tier, levels = rev(c("RAS-targeted", "RAS-regulator-targeted",
                                          "RAS-biomarker-selected", "RAS-mentioned")))
TIER <- c("RAS-targeted" = "#BF3100", "RAS-regulator-targeted" = "#E09F3E",
          "RAS-biomarker-selected" = "#2E6F9E", "RAS-mentioned" = "#BFCBD4")

pd <- ggplot(sh, aes(Freq, country, fill = tier)) +
  geom_col(width = 0.72, position = "fill", linewidth = 0) +
  scale_fill_manual(values = TIER, name = NULL,
                    guide = guide_legend(nrow = 2, byrow = TRUE, reverse = TRUE)) +
  scale_x_continuous("Proportion of trials", labels = percent_format(1),
                     expand = expansion(0)) +
  scale_y_discrete(NULL, labels = function(x) sub("Turkey \\(Türkiye\\)", "Türkiye", x)) +
  axed + theme(legend.position = "bottom", legend.box.spacing = unit(1.5, "mm"))

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

layout <- "
AA
BC
DD
"
fig <- pa + pb + pcc + pd +
  plot_layout(design = layout, heights = c(1.10, 0.95, 0.80)) +
  plot_annotation(tag_levels = "a") &
  theme(plot.tag.position = c(0, 1))

save_fig(fig, "Figure_RAS_trials_global_distribution", 180, 198)
save_fig(pa, "FigurePanel_a_world_map", 180, 96)
save_fig(pb, "FigurePanel_b_top25_by_phase", 88, 92)
save_fig(pcc, "FigurePanel_c_cumulative_by_year", 88, 68)
save_fig(pd, "FigurePanel_d_tier_composition", 180, 78)

# -------------------------------------------------- numbers quoted in the text
cat("\nfigure-level checks\n")
cat("  trial-country pairs      :", nrow(pc), "\n")
cat("  distinct trials with site:", length(unique(paste(tr$nct_id[nzchar(tr$countries)]))), "\n")
cat("  countries on the map     :", nrow(agg), "of", nrow(cn), "registry entries\n")
cat("  top 5                    :", paste(sprintf("%s=%d", ord[1:5],
      as.integer(sort(table(pc$country), decreasing = TRUE)[1:5])), collapse = ", "), "\n")
cat("  US share of pairs        :", sprintf("%.1f%%", 100 * sum(pc$country == "United States") / nrow(pc)), "\n")
cat("  single-country trials    :", sum(tr$is_multinational == "no" & nzchar(tr$countries)), "\n")
