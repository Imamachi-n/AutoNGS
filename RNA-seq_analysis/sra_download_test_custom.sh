#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

dirpath=`pwd`
dirname=`basename ${dirpath}`

python ~/custom_command/sra_parallel_download.py ./srafile.txt ${dirname}
bash ./sra_parallel_download.sh
