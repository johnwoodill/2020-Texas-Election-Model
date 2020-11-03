library(tidyverse)
library(scales)

#setwd("~/Projects/2020-Texas-Election-Model/")

#Jon's working directory
#setwd("/Users/Jon/Dropbox/Documents/consulting_projects/2020-Texas-Election-Model/")

dat <- read_csv("data/processed_election_results.csv")




head(dat)

# Calculate observed votes from counties reporting
obs_dat <- dat %>%
  filter(corr_county == county) %>%
  group_by(county, N) %>%
  summarize(obs_v = first(pred_v))

# Replace predicted with observed for counties observed
obs_pdat <- dat %>%
  left_join(obs_dat, by = c("county", "N")) %>%
  mutate(pred_v = ifelse(is.na(obs_v) == F, obs_v, pred_v)) %>%
  group_by(county, pred_year, N) %>% 
  summarise(mean_pred_v = mean(pred_v),
            sd_pred_v = sd(pred_v)) %>% 
  ungroup() %>% 
  group_by(pred_year, N) %>% 
  summarise(total_v = sum(mean_pred_v)) %>% 
  group_by(pred_year) %>% 
  mutate(perc = (total_v / sum(total_v)) * 100)

pdat <- dat %>%
  group_by(county, pred_year, N) %>% 
  summarise(mean_pred_v = mean(pred_v),
            sd_pred_v = sd(pred_v)) %>% 
  ungroup() %>% 
  group_by(pred_year, N) %>% 
  summarise(total_v = sum(mean_pred_v)) %>% 
  group_by(pred_year) %>% 
  mutate(perc = (total_v / sum(total_v)) * 100)

# Calculate percent of counties reporting
per_report <- round((n_distinct(dat$corr_county) / n_distinct(dat$county)) * 100, 1)

pdat$N <- factor(pdat$N, levels = c("TRUMP", "BIDEN", "OTHER"))

#########
# Remember to uncomment/comment the line below the data starts flowing.
#########
#ggplot(obs_pdat, aes(x=factor(pred_year),  y=perc, fill=factor(N))) + 
ggplot(pdat, aes(x=factor(pred_year),  y=perc, fill=factor(N))) + 
  geom_bar(stat='identity', position = "dodge") +
  geom_text(aes(label=round(perc, 2)), position=position_dodge(width=0.75), vjust=-0.5, size=2.5) +
  theme_classic() +
  labs(x=NULL, y="Percentage of Predicted Vote", fill=NULL) +
  scale_fill_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  theme(legend.title = element_blank(),
        legend.position = c(0.9, 0.85)) +
  ylim(0, 100) +
  annotate("text", x = as.factor(2014), y = 100, label = str_c(as.character(per_report), str_c("% reporting as of ", as.character(format(Sys.time(), format="%H:%M %Z"))))) +
  NULL

ggsave("figures/predictions.png", width=6, height=4)  

  





pdat1 <- dat %>% 
  filter(N != "OTHER") %>%
  group_by(county, pred_year, N) %>% 
  summarise(mean_pred_v = mean(pred_v)) %>% 
  ungroup() %>% 
  mutate(etime = max(pred_year) - pred_year,
         w_mean_pred_v = mean_pred_v * (exp(-etime / max(etime)))) %>% 
  group_by(N) %>% 
  summarise(total_v = sum(mean_pred_v),
            w_total_v = sum(w_mean_pred_v)) %>% 
  mutate(perc = (total_v / sum(total_v) * 100),
         w_perc = (w_total_v / sum(w_total_v)) * 100,
         nlabel = paste0(N, ": ", round(w_perc, 2)))

pdat1$election <- "2020 Election Results \n (Weighted by Year)"

pdat1$N <- factor(pdat1$N, arrange(pdat1, w_perc)$N)

trump_label = paste0("Trump: ", round(filter(pdat1, N == "TRUMP")$w_perc, 2), "%")
biden_label = paste0("Biden: ", round(filter(pdat1, N == "BIDEN")$w_perc, 2), "%")

ggplot(pdat1, aes(y=w_perc, x=election, fill=N)) + 
  theme_classic() +
  geom_bar(stat='identity', width=.45) + 
  geom_hline(yintercept = 50, color='grey', linetype='dotted') +
  annotate("text", x = 1, y = 15, label=trump_label, color='white', size=3.75) +
  annotate("text", x = 1, y = 85, label=biden_label, color='white', size=3.75) +
  scale_fill_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  scale_color_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  labs(x=NULL, y=NULL, fill=NULL, title=paste0("Last Model Update: ", Sys.time(), "\n \n \n 2020 Texas Election Prediction")) +
  theme(legend.title = element_blank(),
        legend.position = 'none',
        panel.border = element_rect(colour = "black", fill=NA, size=2),
        plot.title = element_text(hjust = 0.5),
        axis.title.y = element_blank(),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank()) +
  coord_flip() +
  
  NULL
  

ggsave("figures/bar_predictions.png", width=6, height=2)  


# Representative turnout histogram
turnout_pdat <- dat %>%
  left_join(obs_dat, by = c("county", "N")) %>%
  mutate(pred_v = ifelse(is.na(obs_v) == F, obs_v, pred_v)) %>%
  group_by(corr_county, N, pred_year) %>%
  summarise(total_v = sum(pred_v)) %>% 
  spread(N, total_v) %>%
  mutate(sum_total = BIDEN + TRUMP + OTHER) %>%
  mutate(BIDEN_per = round(BIDEN / sum_total * 100, 1),
         TRUMP_per = round(TRUMP / sum_total * 100, 1)) %>%
  mutate(BIDEN_points = BIDEN_per - TRUMP_per) %>%
  mutate(color = ifelse(BIDEN_points > 0, "B_plus", "B_neg"))

col_pal = c("B_plus" = "darkblue",
           "B_neg" = "red")

ggplot(turnout_pdat) +
  geom_histogram(aes(x = BIDEN_points, fill = color),  binwidth = 0.1) +
  scale_x_continuous(limits = c(-8, 8), breaks = seq(-8, 8, by = 1)) +
  geom_vline(xintercept = 0, color='grey', linetype='dotted') +
  theme_classic() +
  theme(legend.position = "none") +
  scale_fill_manual(
    values = col_pal,
    limits = names(col_pal)
  ) +
  facet_grid(rows = vars(pred_year)) +
  labs(title = "Uncertainty in county turnout", x = "Percentage points for Biden", y = "Number of predictions")


ggsave("figures/county_turnout_histo.png", width=6, height=4)  

# Combined county correlation turnout uncertainty histogram
ggplot(turnout_pdat) +
  geom_histogram(aes(x = BIDEN_points, fill = color),  binwidth = 0.1) +
  scale_x_continuous(limits = c(-8, 8), breaks = seq(-8, 8, by = 1)) +
  geom_vline(xintercept = 0, color='grey', linetype='dotted') +
  theme_classic() +
  theme(legend.position = "none") +
  scale_fill_manual(
    values = col_pal,
    limits = names(col_pal)
  ) +
  labs(title = "Combining unknown county turnout and correlations", x = "Percentage points for Biden", y = "Number of predictions")


ggsave("figures/county_corr_turnout_histo.png", width=6, height=4)  

# Show counties reported and their 2018 Biden percent values

cnty_2018 <- read_csv("data/TX_cnty_2018.csv") %>%
  mutate(sum_total = REP + DEM + OTH) %>%
  mutate(DEM_per = round(DEM / sum_total * 100, 1),
         REP_per = round(REP / sum_total * 100, 1)) %>%
  mutate(DEM_points = DEM_per - REP_per) %>%
  arrange(DEM_points) %>%
  rename(county = County)

cnty_reporting <- obs_dat %>%
  group_by(county) %>%
  summarize(sum_v = sum(obs_v))

cnty_2018_reporting <- cnty_2018 %>%
  left_join(cnty_reporting, by = "county") %>%
  mutate(color = ifelse(DEM_points > 0, "B_plus", "B_neg"))

ggplot() +
  geom_bar(data = cnty_2018, aes(x = DEM_points, y = sum_total), stat = "identity", color = "grey") +
  geom_bar(data = cnty_2018_reporting, aes(x = DEM_points, y = sum_v, color = color), stat = "identity") +
  theme_classic() +
  geom_vline(xintercept = 0, color='grey', linetype='dotted') +
  scale_color_manual(
    values = col_pal,
    limits = names(col_pal)
  ) +
  theme(legend.position = "none") +
  labs(x = "Points Democratic from 2018", y = "2018 total votes", title = "Counties Reporting")

ggsave("figures/cnty_reporting.png", width=6, height=4)  

# Prediction time trend
# Gotta figure out how to join the timestamped outputs


