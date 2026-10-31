# R packages for Figures 9, 10, 11 and 12. Tested with R 4.6.1.
# Installs the exact versions used to make the published figures.
#   Rscript environment/install_R_packages.R
pkgs <- c(ggplot2 = "4.0.3", dplyr = "1.2.1", tidyr = "1.3.2", ggtext = "0.1.2",
          gridtext = "0.1.6", ggrepel = "0.9.8", patchwork = "1.3.2", cowplot = "1.2.0",
          scales = "1.4.0", maps = "3.4.3", svglite = "2.2.2", systemfonts = "1.3.2")
repos <- "https://cloud.r-project.org"
if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes", repos = repos)
for (p in names(pkgs)) {
  have <- tryCatch(as.character(packageVersion(p)), error = function(e) NA)
  if (is.na(have) || have != pkgs[[p]]) remotes::install_version(p, version = pkgs[[p]], repos = repos, upgrade = "never")
}
for (p in names(pkgs)) cat(sprintf("%-12s %s\n", p, as.character(packageVersion(p))))
