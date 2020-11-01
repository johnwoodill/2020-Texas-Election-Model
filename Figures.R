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

ggplot(pdat, aes(x=factor(pred_year),  y=perc, fill=factor(N))) + 
  geom_bar(stat='identity', position = "dodge") +
  geom_text(aes(label=round(perc, 2)), position=position_dodge(width=0.75), vjust=-0.5) +
  theme_bw() +
  labs(x=NULL, y="Percentage of Predicted Vote", fill=NULL) +
  scale_fill_manual("legend", values = c("BIDEN" = "darkblue", "TRUMP" = "red")) +
  theme(legend.title = element_blank(),
        legend.position = c(0.9, 0.9)) +
  ylim(0, 75) +
  annotate("text", x = as.factor(2012), y = 75, label = str_c(as.character(per_report), "% reporting"))
  NULL

ggsave("figures/predictions.png", width=6, height=4)  

  
  
