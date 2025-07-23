library(ggplot2)
library(ggradar)
library(patchwork)
library(ggrepel)
library(dplyr)
library(tidyr)

args <- commandArgs(trailingOnly = TRUE)
cornRecov <- read.csv(paste0(args[1], 'healthy_stressed_results.csv'))

recCold <- cornRecov[cornRecov$Treatment == 'cold',]
recCon <- cornRecov[cornRecov$Treatment == 'control',]

plotCold <- recCold %>%
  group_by(Genotype) %>%
  arrange(Day) %>%
  summarize(
    A_start = A[Day == 13],
    A_end = A[Day == 20],
    B_start = B[Day == 13],
    B_end = B[Day == 20]
  )

plotCon <- recCon %>%
  group_by(Genotype) %>%
  arrange(Day) %>%
  summarize(
    A_start = A[Day == 13],
    A_end = A[Day == 20],
    B_start = B[Day == 13],
    B_end = B[Day == 20]
  )

coldplot <- ggplot(plotCold, aes(x = A_start, y = B_start, color = Genotype)) +
  # Add points for day 3
  geom_point(size = 1, shape = 16) +
  # Add points for day 10
#  geom_point(aes(x = A_end, y = B_end), size = 3, shape = 17) +
  # Add arrows showing the change
  geom_segment(aes(xend = A_end, yend = B_end),
               arrow = arrow(length = unit(0.2, "cm")), 
               size = 0.5) +
  coord_cartesian(xlim = c(-6, 2), ylim = c(1, 20)) +
  labs(title = "Color Change, Cold Recovery (Day 3 to 10)",
       x = "A (green → magenta)",
       y = "B (blue → yellow)") +
  theme_bw()

conplot <- ggplot(plotCon, aes(x = A_start, y = B_start, color = Genotype)) +
  # Add points for day 3
  geom_point(size = 1, shape = 16) +
  # Add points for day 10
  #  geom_point(aes(x = A_end, y = B_end), size = 3, shape = 17) +
  # Add arrows showing the change
  geom_segment(aes(xend = A_end, yend = B_end),
               arrow = arrow(length = unit(0.2, "cm")), 
               size = 0.5) +
  coord_cartesian(xlim = c(-6, 2), ylim = c(1, 20)) +
  labs(title = "Color Change, Control (Day 3 to 10)",
       x = "A (green → magenta)",
       y = "B (blue → yellow)") +
  theme_bw()

plotAll <- cornRecov %>%
  group_by(Genotype, Treatment) %>%
  arrange(Day) %>%
  summarize(
    A_start = A[Day == 13],
    A_end = A[Day == 20],
    B_start = B[Day == 13],
    B_end = B[Day == 20]
  )
allplot <- ggplot(plotAll, aes(x = A_start, y = B_start, color = Genotype)) +
  # Add points for day 3
  geom_point(size = 1, shape = 16) +
  # Add points for day 10
  #  geom_point(aes(x = A_end, y = B_end), size = 3, shape = 17) +
  # Add arrows showing the change
  geom_segment(aes(xend = A_end, yend = B_end, linetype = Treatment),
               arrow = arrow(length = unit(0.2, "cm")), 
               size = 0.5) +
  coord_cartesian(xlim = c(-6, 2), ylim = c(1, 20)) +
  labs(title = "Color Change (Day 3 to 10)",
       x = "A (green → magenta)",
       y = "B (blue → yellow)") +
  theme_bw()

ggsave(paste0(args[1], 'colorchange_cold.png'), coldplot)
ggsave(paste0(args[1], 'colorchange_control.png'), conplot)
ggsave(paste0(args[1], 'colorchange_combined.png'), allplot)



