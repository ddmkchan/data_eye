#! /usr/bin/env Rscript

clusters <- 8
#tt <- read.delim("/home/cyp/data_eye/r_project/test_set", header=TRUE)
tt <- read.delim("/home/cyp/data_eye/r_project/uid_payment_d30", header=TRUE)
#is_new <- tt$duration_d30==tt$duation
#first_pay <- tt$payamount_d30==tt$payamount
d <- data.frame(tt[, c(4,5,6)], row.names=tt$uid)
#标准化处理

kc <- kmeans(scale(d), clusters, iter.max = 20)
rs <- data.frame(kc$cluster)
mytable <- with(rs, table(rs$kc.cluster))
mytable
d <- cbind(d, tt[,2:3])
d$duration_d30 <- round(d$duration_d30/60, digits = 2)
d <- cbind(d, rs)
#聚类结果可视化 
#plot(scale(d)[,2:3], col = kc$cluster, pch = as.integer(d$kc.cluster))
#不同的颜色代表不同的聚类结果，不同的形状代表训练数据集的原始分类情况。
#points(kc$centers[,2:3], col = 1:10, pch = 8, cex=2)
paytimes_d30 <- c()
payamount_d30 <- c()
date_diff <- c()
logintimes_d30 <- c()
duration_d30 <- c()
R <- c()
F <- c()
M <- c()
total <- c()
for (i in 1:clusters) {
	cls <- d[which(d$kc.cluster==i),]
	paytimes_d30 <- append(paytimes_d30, round(median(cls$paytimes_d30), digits=0))
	payamount_d30 <- append(payamount_d30, round(median(cls$payamount_d30), digits=2))
	date_diff <- append(date_diff, round(median(cls$date_diff), digits=2))
	logintimes_d30 <- append(logintimes_d30, round(median(cls$logintimes_d30), digits=0))
	duration_d30 <- append(duration_d30, round(median(cls$duration_d30), digits=2))
	R <- append(R, round(median(cls$date_diff) - median(d$date_diff), digits=0))
	F <- append(F, round(median(cls$paytimes_d30) - median(d$paytimes_d30), digits=0))
	M <- append(M, round(median(cls$payamount_d30) - median(d$payamount_d30), digits=2))
	total <- append(total, mytable[i])
	print(paste("kcuster ", i, " size ", nrow(cls), "payment_sum", sum(cls$payamount_d30)))
	print(summary(cls))
	}
print(median(d$date_diff))
print(median(d$paytimes_d30))
print(median(d$payamount_d30))
print(median(d$logintimes_d30))
print(median(d$duration_d30))
out <- data.frame(date_diff, paytimes_d30, payamount_d30, R, F, M, logintimes_d30, duration_d30, total)
print(out)
write.table(out, "rfm.txt", sep="\t")
##dev.off()
