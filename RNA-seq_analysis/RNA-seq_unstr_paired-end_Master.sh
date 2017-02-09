#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

dirpath=`pwd`
dirname=`basename ${dirpath}`

python ~/custom_command/prep_cuffdiff_settings.py srafile_name_label.txt PAIRED ${dirname}
bash ./RNA-seq_unstr_0_sra2fastq_for_run.sh
