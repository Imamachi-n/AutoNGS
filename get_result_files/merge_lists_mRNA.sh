#!/bin/bash

cut -f1,2,3 1_GSE65778_cuffdiff_out_mrna_isrib_mRNA.txt > row_names.txt

for filename in *_mRNA.txt
do
    basename ${filename} _mRNA.txt > header.tmp
    paste header.tmp header.tmp > header.tmp2
    paste header.tmp2 header.tmp2 > header.tmp4
    cut -f8,9,10,11 ${filename} | tail -n +2 - | cat header.tmp4 - > ${filename}_tmp.txt
done

paste *_tmp.txt > test.tmp
paste row_names.txt test.tmp > cuffdiff_result_mRNA_all.txt

# Remove tmp files
rm -r *_tmp.txt
rm test.tmp
rm header.tmp
rm header.tmp2
rm header.tmp4
