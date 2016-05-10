app_overview <- read.delim("~/app_overview_0420")
df = app_overview[which(app_overview$valid_days>=60 & app_overview$pay_dates >=30 & app_overview$payment_user>=50 & app_overview$payamount > 100 & app_overview$payamount/app_overview$payment_user<1000),]
df[which(df$retain_d14_rate==0),]$retain_d14_rate = 0.0234
df <- df[which(df$appid!="B74456858D5FA993AD9AED2D65D52E70"),]
app_user_summary <- read.delim("~/app_user_summary")
m = merge(df, app_user_summary, by = c("qt", "platform", "appid"))
nrow(df)
nrow(m)

#input = df[,c("payamount", "dau", "avg_new_user", "payment_user", "ltv_15")]
input = m[,c("payamount", "dau", "avg_new_user", "payment_user", "ltv_15", "logintimes", "duration", "retain_d14")]
input = as.data.frame(scale(input))
library(leaps)
#l = regsubsets(payamount ~ dau + avg_new_user + payment_user+ ltv_15 + logintimes + retain_d14 + duration, data=input, nbest=5)
l = regsubsets(payamount ~ dau + avg_new_user + payment_user + ltv_15 + logintimes + duration + retain_d14 , data=input, nbest=6)
plot(l, scale = "adjr2")

fit <- lm(payamount ~ dau  + payment_user+ ltv_15  + duration + retain_d14 , data=input)
coef(fit)
summary(fit)
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


shrinkage <- function(fit,k=10){
  require(bootstrap)
  
  # define functions 
  theta.fit <- function(x,y){lsfit(x,y)}
  theta.predict <- function(fit,x){cbind(1,x)%*%fit$coef} 
  
  # matrix of predictors
  x <- fit$model[,2:ncol(fit$model)]
  # vector of predicted values
  y <- fit$model[,1]
  
  results <- crossval(x,y,theta.fit,theta.predict,ngroup=k)
  r2 <- cor(y, fit$fitted.values)**2 # raw R2 
  r2cv <- cor(y,results$cv.fit)**2 # cross-validated R2
  cat("Original R-square =", r2, "\n")
  cat(k, "Fold Cross-Validated R-square =", r2cv, "\n")
  cat("Change =", r2-r2cv, "\n")
}

relweights <- function(fit,...){
  R <- cor(fit$model)
  nvar <- ncol(R)
  rxx <- R[2:nvar, 2:nvar]
  rxy <- R[2:nvar, 1]
  svd <- eigen(rxx)
  evec <- svd$vectors
  ev <- svd$values
  delta <- diag(sqrt(ev))
  lambda <- evec %*% delta %*% t(evec)
  lambdasq <- lambda ^ 2
  beta <- solve(lambda) %*% rxy
  rsquare <- colSums(beta ^ 2)
  rawwgt <- lambdasq %*% beta ^ 2
  import <- (rawwgt / rsquare) * 100
  import <- as.data.frame(import)
  row.names(import) <- names(fit$model[2:nvar])
  names(import) <- "Weights"
  import <- import[order(import),1, drop=FALSE]
  dotchart(import$Weights, labels=row.names(import),
           xlab="% of R-Square", pch=19,
           main="Relative Importance of Predictor Variables",
           sub=paste("Total R-Square=", round(rsquare, digits=3)),
           ...)
  return(import)
}
