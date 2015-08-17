#! /usr/bin/env Rscript

clusters <- 8
tt <- read.delim("/home/cyp/data_eye/r_project/uid_rfm_payment_d30", header=TRUE)
#is_new <- tt$duration_d30==tt$duation
#first_pay <- tt$payamount_d30==tt$payamount
d <- data.frame(tt[, c(2,12,13)], row.names=tt$uid)
#标准化处理
cl <- kmeans(scale(d), clusters, iter.max = 20)
rs <- data.frame(cl$cluster)
mytable <- with(rs, table(rs$cl.cluster))
mytable
d <- cbind(d, rs)
paytimes_d30 <- c()
payamount_d30 <- c()
date_diff <- c()
total <- c()
for (i in 1:clusters) {
	c <- d[which(d$cl.cluster==i),]
	paytimes_d30 <- append(paytimes_d30, round(mean(c$paytimes_d30), digits=0))
	payamount_d30 <- append(payamount_d30, round(mean(c$payamount_d30), digits=2))
	date_diff <- append(date_diff, round(mean(c$date_diff), digits=2))
	total <- append(total, mytable[i])
	print(paste("cluster ", i, " size ", nrow(c)))
	print(summary(c))}
out <- data.frame(paytimes_d30, payamount_d30, date_diff, total)
print(out)
write.table(out, "rfm.txt", sep="\t")
