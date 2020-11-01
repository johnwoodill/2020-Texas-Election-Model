library(tidyverse)
library(scales)

setwd("~/Projects/2020-Texas-Election-Model/")

#Jon's working directory
#setwd("/Users/Jon/Dropbox/Documents/consulting_projects/2020-Texas-Election-Model/")

dat <- read_csv("data/processed_election_results.csv")


head(dat)

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

ggplot(pdat, aes(x=factor(pred_year),  y=perc, fill=factor(N))) + 
  geom_bar(stat='identity', position = "dodge") +
  geom_text(aes(label=round(perc, 2)), position=position_dodge(width=0.75), vjust=-0.5, size=2.5) +
  theme_classic() +
  labs(x=NULL, y="Percentage of Predicted Vote", fill=NULL) +
  scale_fill_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  theme(legend.title = element_blank(),
        legend.position = c(0.9, 0.85)) +
  ylim(0, 100) +
  # annotate("text", x = as.factor(2012), y = 75, label = str_c(as.character(per_report), "% reporting")) +
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
  geom_bar(stat='identity', width=.1) + 
  geom_hline(yintercept = 50, color='grey', linetype='dotted') +
  # geom_text(aes(label=round(w_perc, 2), color=N), position=position_dodge(width=0.75), vjust=0, size=2.5) +
  # annotate("text", x = 2, y = 5.75, label=nlabel, color='white') +
  annotate("text", x = 1, y = 10, label=trump_label, color='white', size=2.25) +
  annotate("text", x = 1, y = 90, label=biden_label, color='white', size=2.25) +
  scale_fill_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  scale_color_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red", "OTHER" = "darkgreen")) +
  labs(x=NULL, y=NULL, fill=NULL) +
  theme(legend.title = element_blank(),
        legend.position = 'none',
        panel.border = element_rect(colour = "black", fill=NA, size=2)) +
  coord_flip() +
  
  NULL
  

ggsave("figures/bar_predictions.png", width=6, height=2)  

  


