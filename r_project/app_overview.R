#! /usr/bin/env Rscript

clusters <- 5

app_overview <- read.delim("~/app_overview_0224")
df = app_overview[which(app_overview$valid_days>=60 & app_overview$pay_dates >=30 & app_overview$payment_user>=50 & app_overview$payamount > 100 & app_overview$payamount/app_overview$payment_user<1000),]
df[which(df$retain_d14_rate==0),]$retain_d14_rate = 0.0234
input = df[,c("payamount", "dau", "avg_new_user", "actives_days", "payment_user", "retain_d14_rate", "ltv_15")]


#标准化处理

kc <- kmeans(scale(input), clusters, iter.max = 20)
rs <- data.frame(kc$cluster)
mytable <- with(rs, table(rs$kc.cluster))
mytable
input <- cbind(input, rs)
#聚类结果可视化 
plot(scale(input)[,2:3], col = kc$cluster, pch = as.integer(d$kc.cluster))
#不同的颜色代表不同的聚类结果，不同的形状代表训练数据集的原始分类情况。
points(kc$centers[,2:3], col = 1:10, pch = 8, cex=2)


#paytimes_d30 <- c()
#payamount_d30 <- c()
#date_diff <- c()
#logintimes_d30 <- c()
#duration_d30 <- c()
#R <- c()
#F <- c()
#M <- c()
#total <- c()
#for (i in 1:clusters) {
#	cls <- d[which(d$kc.cluster==i),]
#	paytimes_d30 <- append(paytimes_d30, round(median(cls$paytimes_d30), digits=0))
#	payamount_d30 <- append(payamount_d30, round(median(cls$payamount_d30), digits=2))
#	date_diff <- append(date_diff, round(median(cls$date_diff), digits=2))
#	logintimes_d30 <- append(logintimes_d30, round(median(cls$logintimes_d30), digits=0))
#	duration_d30 <- append(duration_d30, round(median(cls$duration_d30), digits=2))
#	R <- append(R, round(median(cls$date_diff) - median(d$date_diff), digits=0))
#	F <- append(F, round(median(cls$paytimes_d30) - median(d$paytimes_d30), digits=0))
#	M <- append(M, round(median(cls$payamount_d30) - median(d$payamount_d30), digits=2))
#	total <- append(total, mytable[i])
#	print(paste("kcuster ", i, " size ", nrow(cls), "payment_sum", sum(cls$payamount_d30)))
#	print(summary(cls))
#	}
#print(median(d$date_diff))
#print(median(d$paytimes_d30))
#print(median(d$payamount_d30))
#print(median(d$logintimes_d30))
#print(median(d$duration_d30))
#out <- data.frame(date_diff, paytimes_d30, payamount_d30, R, F, M, logintimes_d30, duration_d30, total)
#print(out)
#write.table(out, "rfm.txt", sep="\t")
###dev.off()
