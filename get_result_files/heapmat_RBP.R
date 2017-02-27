setwd("C:/Users/Naoto/OneDrive/NGS解析/AutoNGS/get_result_files")

library(data.table)
raw_data <- fread("cuffdiff_result_mRNA_RBP_compilation.txt", header = T, sep="\t")

library(pheatmap)
library(made4)
kmeans_data <- cbind(kmeans(as.matrix(raw_data[,4:494]),centers=10)$cluster, raw_data)
o <- order(kmeans_data[,1])
kmeans_data <- kmeans_data[o,]
fig_data <- as.matrix(kmeans_data[,5:495])
# pheatmap(fig_data, cluster_rows=F, cluster_cols=F, color = colorRampPalette(c("royalblue", "white", "firebrick3"))(100))
heatplot(fig_data, dend = "none")

write.table(kmeans_data, sep="\t", quote = F, file = "cuffdiff_result_mRNA_RBP_compilation_clustering10.txt")
