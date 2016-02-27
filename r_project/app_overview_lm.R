app_overview <- read.delim("~/app_overview_0224")
View(app_overview)
df = app_overview[which(app_overview$valid_days>=60 & app_overview$pay_dates >=30 & app_overview$payment_user>=50 & app_overview$payamount > 100 & app_overview$payamount/app_overview$payment_user<1000),]
df[which(df$retain_d14_rate==0),]$retain_d14_rate = 0.0234
input = df[,c("payamount", "dau", "avg_new_user", "actives_days", "payment_user", "retain_d14_rate", "ltv_15")]
fit <- lm(payamount ~ dau + avg_new_user + payment_user + retain_d14_rate + ltv_15, data=input)
par(mfrow=c(2,2))
plot(fit)

