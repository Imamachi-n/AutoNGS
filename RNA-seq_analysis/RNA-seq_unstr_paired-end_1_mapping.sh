#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=32G
#$ -l mem_req=32G

file=`basename ${1} _1.fastq`
file=`basename ${file} _2.fastq`
file=`basename ${file} .fastq`
gtfFile="/home/akimitsu/database/gencode.v19.annotation_filtered.gtf"
indexFile="/home/akimitsu/database/bowtie1_index/hg19"

## 1. Quality check
mkdir fastqc_${file}_1
fastqc -o ./fastqc_${file}_1 ./${file}_1.fastq -f fastq
mkdir fastqc_${file}_2
fastqc -o ./fastqc_${file}_2 ./${file}_2.fastq -f fastq

## 2. Quality filtering (Option)
# ## fastq_quality_trimmer -Q33 -t 20 -l 10 -i ./${file}_1.fastq | fastq_quality_filter -Q33 -q 20 -p 80 -o ${file}_1_filtered_1.fastq
# ## fastq_quality_trimmer -Q33 -t 20 -l 10 -i ./${file}_2.fastq | fastq_quality_filter -Q33 -q 20 -p 80 -o ${file}_1_filtered_2.fastq

## 3. rRNA removal (Option)
# ## bowtie -p 8 --un ./${file}_2_norrna.fastq ${indexFile} ./${file}_1_filtered.fastq > rRNA_${file}.fastq 2>> ./log_${file}.txt

## 4. Mapping to genome and transcriptome
indexFile="/home/akimitsu/database/STAR_index/hg19_Gencode_v19"
maxRAM=32000000000

mkdir STAR_output_${file}
STAR --runMode alignReads --runThreadN 8 --genomeDir ${indexFile} \
--readFilesIn ./${file}_1.fastq ./${file}_2.fastq --outFilterType BySJout \
--outFileNamePrefix ./STAR_output_${file}/${file}_4_STAR_result_ \
--outSAMstrandField intronMotif --outFilterIntronMotifs RemoveNoncanonical \
--outSAMattributes All --outSAMtype BAM SortedByCoordinate --limitBAMsortRAM ${maxRAM} \
--outFilterMultimapNmax 20 --outFilterMismatchNmax 999 \
--outFilterMismatchNoverReadLmax 0.04 --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 \
--alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --sjdbScore 1

# --outSAMattributes NH HI AS NM MD

# RNA quality check from mapped reads
mkdir geneBody_coverage_${file}
samtools index ./STAR_output_${file}/${file}_4_STAR_result_Aligned.sortedByCoord.out.bam
geneBody_coverage.py -r /home/akimitsu/database/hg19.HouseKeepingGenes_for_RSeQC.bed -i ./STAR_output_${file}/${file}_4_STAR_result_Aligned.sortedByCoord.out.bam  \
-o ./geneBody_coverage_${file}/${file}_RSeQC_output

# Visualization for UCSC genome browser
mkdir UCSC_visual_${file}
bedtools genomecov -ibam ./STAR_output_${file}/${file}_4_STAR_result_Aligned.sortedByCoord.out.bam -bg -split > ./UCSC_visual_${file}/${file}_4_result.bg
echo "track type=bedGraph name=${file} description=${file} visibility=2 maxHeightPixels=40:40:20" > ./UCSC_visual_${file}/tmp.txt
cat ./UCSC_visual_${file}/tmp.txt ./UCSC_visual_${file}/${file}_4_result.bg > ./UCSC_visual_${file}/${file}_4_result_for_UCSC.bg
bzip2 -c ./UCSC_visual_${file}/${file}_4_result_for_UCSC.bg > ./UCSC_visual_${file}/${file}_4_result_for_UCSC.bg.bz2
