app_overview <- read.delim("~/app_overview_0224")

df = app_overview[which(app_overview$valid_days>=60 & app_overview$pay_dates >=30 & app_overview$payment_user>=50 & app_overview$payamount > 100 & app_overview$payamount/app_overview$payment_user<1000),]
df[which(df$retain_d14_rate==0),]$retain_d14_rate = 0.0234
app_user_summary <- read.delim("~/app_user_summary")
m = merge(df, app_user_summary, by = c("platform", "appid"))
#View(m)
#input = m[,c("payamount", "dau", "avg_new_user", "payment_user", "retain_d14_rate", "ltv_15", "ratio")]
input = m[,c("payamount", "dau", "avg_new_user", "payment_user", "retain_d14_rate", "ltv_15", "ratio", "logintimes", "duration")]
fit <- lm(payamount ~ dau + avg_new_user + payment_user + retain_d14_rate + ltv_15 + ratio + logintimes + duration,  data=input)
par(mfrow=c(2,2))
plot(fit)

kc <- kmeans(input, 2, iter.max = 50)
library(fpc)
library(cluster)
plotcluster(input, kc$cluster)
clusplot(input, kc$cluster, color=TRUE, shade=TRUE,labels=2, lines=0)
rs <- data.frame(kc$cluster)
input <- cbind(input, rs)
stats <- cluster.stats(dist(input), kc$cluster)
stats$avg.silwidth
kc$size



