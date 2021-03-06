#! /usr/bin/env Rscript

clusters <- 5
tt <- read.delim("/home/cyp/data_eye/r_project/uid_rfm_payment_d30", header=TRUE)
#tt <- read.delim("/home/cyp/data_eye/r_project/test_set", header=TRUE)
d <- data.frame(tt[, c(2,10,11,12,13)], row.names=tt$uid)
d$playtimes_d30 <- round(ifelse(d$logintimes_d30==0, 0, (d$duration_d30 / 30 / 60)), digits=2)
#d$playtimes_d30 <- round(ifelse(d$logintimes_d30==0, 0, (d$duration_d30 / d$logintimes_d30 / 60)), digits=2)
#summary(d$playtimes_d30)
#d$level[d$playtimes_d30>=0 & d$playtimes_d30<5] <- 1
#d$level[d$playtimes_d30>=5 & d$playtimes_d30<10] <- 2
#d$level[d$playtimes_d30>=10 & d$playtimes_d30<30] <- 3
#d$level[d$playtimes_d30>=30 & d$playtimes_d30<60] <- 4
#d$level[d$playtimes_d30>=60] <- 5
#mt <- with(d, table(d$level))
#mt
#d$logintimes_d30 <- NULL
d$duration_d30 <- NULL
cl <- kmeans(scale(d), clusters, iter.max = 20)
rs <- data.frame(cl$cluster)
mytable <- with(rs, table(rs$cl.cluster))
mytable
#dev.off()
d <- cbind(d, rs)
#d[which(d$cl.cluster==2),][1:10,]
paytimes_d30 <- c()
payamount_d30 <- c()
playtimes_d30 <- c()
date_diff <- c()
total <- c()
for (i in 1:clusters) {
	c <- d[which(d$cl.cluster==i),]
	paytimes_d30 <- append(paytimes_d30, round(median(c$paytimes_d30), digits=0))
	payamount_d30 <- append(payamount_d30, round(median(c$payamount_d30), digits=2))
	playtimes_d30 <- append(playtimes_d30, round(median(c$playtimes_d30), digits=2))
	date_diff <- append(date_diff, round(median(c$date_diff), digits=2))
	total <- append(total, mytable[i])
	print(paste("cluster ", i, " size ", nrow(c)))
	print(summary(c))}
out <- data.frame(paytimes_d30, payamount_d30, playtimes_d30, date_diff, total)
print(out)
write.table(out, "out.txt", sep="\t")
