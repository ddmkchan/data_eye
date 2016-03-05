K <- 2:8
round <- 30 # 每次迭代30次，避免局部最优
rst <- sapply(K, function(i){
  print(paste("K=",i))
  mean(sapply(1:round,function(r){
    print(paste("Round",r))
    result <- kmeans(norm.data, i)
    stats <- cluster.stats(dist(norm.data), result$cluster)
    stats$avg.silwidth
  }))
})
plot(K,rst,type='l',main='轮廓系数与K的关系', ylab='轮廓系数')


# 开始与结果边界
begin = 2; 
length = 15;
count = 50;
end = begin + length - 1;

# 结果容器
result = c();
result[begin:end] = -1;

# 遍历计算kmeans的SSE
library(cluster);

for(i in begin:end) {
  # Silhouette coefficient
  tmp = c();
  tmp[1:count] = 0;
  for(j in 1:count) {
    kcluster = kmeans(input, i, iter.max = 20);
    tmp[j] = kcluster$silinfo$avg.width;
  }
  result[i] = mean(tmp);
}

# 绘制结果
plot(result, type="o", xlab="Number of Cluster", ylab="Silhouette Coefficient");



#设簇个数在2到5之间取值
x=c()
y=c()
for (i in 2:5){
  #K聚类结果存于result变量
  result <- pam(input,i)
  #求出聚类评价统计量
  stats=cluster.stats(dist(input), result$cluster)
  #将结果存入X
  x[i-1]=stats$avg.silwidth
  y[i-1]=i
}
plot(y,x)
