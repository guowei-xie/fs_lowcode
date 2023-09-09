library(tidyverse)
library(hrbrthemes)
theme_set(theme_ipsum(base_family = "Kai",
                      base_size = 8 )+
            theme(text = element_text(family = "Kai")))

## 可视化
### CHART.1-方差图：按学期展示不同业务线下老师的续报率分布

raw <- read_csv("data/eda_l1_counselor_stats.csv")

# data pre-processing
dat <-
  raw %>%
  filter(term_start_date >= "2023-05-01") %>%
  group_by(term, business_line, counselor_id) %>%
  summarise(enroll = sum(enroll),
            renewal = sum(renew_d4, na.rm = TRUE)) %>%
  mutate(renew_rate = renewal/ enroll ) %>%
  filter(enroll >= 100 & renew_rate > 0)

# draw plot
plot1 <-
  dat %>%
  ggplot(aes(x = term, y = renew_rate))+
  geom_jitter(aes(col = term),
              alpha = .5,
              size = 3)+
  stat_summary(fun = "median",
               fun.max = \(x) quantile(x, 0.75),
               fun.min = \(x) quantile(x, 0.25),
               col = "red",
               size = 1)+
  scale_fill_brewer(palette = "Dark2")+
  facet_wrap(~ business_line, scales = "free_y")+
  labs(
    x = "学期",
    y = "续报率",
    title = "按学期展示不同业务线下老师的续报率分布",
    subtitle = "仅展示2023年05月之后招生学期"
  )+
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 90))

# save
ggsave("img/plot1.jpeg", plot = plot1)

### CHART.2-哑铃图：对比两期老师的续报率是否都在下降？

# # data pre-processing
library(reshape2)
dat <-
  raw %>%
  filter(term %in% c("2023春11期", "2023春13期")) %>%
  group_by(term, business_line, counselor_id) %>%
  summarise(enroll = sum(enroll),
            renewal = sum(renew_d4, na.rm = TRUE),
            .groups = "drop") %>%
  mutate(renew_rate = renewal/ enroll ) %>%
  filter(enroll >= 100 & renew_rate > 0) %>%
  group_by(business_line, counselor_id) %>%
  summarise(term,
            renew_rate,
            n = n(),
            .groups = "keep") %>%
  filter(n == 2) %>%
  mutate(diff_rate = diff(renew_rate),
         is_down = as.factor(ifelse(diff_rate < 0, 1, 0))) %>%
  mutate(counselor_id = as.factor(counselor_id))

# draw plot
plot2 <-
  dat %>%
  ggplot(aes(x = counselor_id, y = renew_rate))+
  geom_point(aes(color = is_down),
             size = 3)+
  geom_line(aes(group = counselor_id,
                color = is_down),
            size = 1)+
  coord_flip()+
  facet_wrap(~ business_line, scales = "free_y")+
  labs(x = "",
       y = "续报率",
       color = "是否下降",
       title = "相同老师的两期续报率对比",
       subtitle = "春11期 vs 春13期")+
  theme(axis.text.y = element_blank(),
        legend.position = "top")

ggsave("img/plot2.jpeg", plot = plot2)


### CHART.3-坡度图：对比两期老师的续报率是否都在下降？
plot3 <-
  dat %>%
  ggplot(aes(x = term, y = renew_rate))+
  geom_point(aes(color = is_down),
             size = 5)+
  geom_line(aes(group = counselor_id,
                color = is_down),
            size = .5)+
  facet_wrap(~ business_line, scales = "free_y")+
  labs(
    x = "",
    y = "续报率",
    color = "是否下降",
    title = "相同老师的两期续报率对比",
    subtitle = "春11期 vs 春13期")

ggsave("img/plot3.jpeg", plot = plot3)


### CHART.4-生存曲线：通过入口月份观察近期退费率趋势
library(survival)
library(survminer)
dat <- read_csv("data/refund.csv") %>%
  filter(pay_date >= "2022-06-01" & pay_date <= "2022-12-31")

facet_fit <-
  survfit(Surv(surv_days, is_refund) ~ pay_month + parent_operation_type_name,data = dat)


ggsurv <-
  ggsurvplot(

    facet_fit,
    data = dat,
    linetype = "solid",
    conf.int = FALSE,
    xlab = "Days",
    ylab = "Surv.Prob",
    ylim = c(0.85, 1),
    pval = TRUE,
    #palette = "Greens",
    direction = 1,
    ggtheme = theme(text = element_text(family = 'Kai'),
                    plot.title = element_text(size = 12,
                                              face = "blod",
                                              family = 'Kai'))
  )

plot4 <-
  ggsurv$plot +
  scale_color_grey()+
  #scale_color_hue(h = c(120, 240))+
  geom_hline(yintercept = 0.9,
             lty = 4,
             col = "salmon")+
  facet_wrap(~ parent_operation_type_name, ncol = 2)+
  theme(legend.position = "none")

ggsave("img/plot4.jpeg", plot = plot4)

