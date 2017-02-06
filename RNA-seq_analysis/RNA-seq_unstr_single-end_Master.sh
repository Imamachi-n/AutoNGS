#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

python ~/custom_command/prep_cuffdiff_settings.py srafile_name_label.txt SINGLE
fastq-dump *.sra
python ~/custom_command/merge_fastq.py srafile_name_label.txt SINGLE
bash ./RNA-seq_unstr_1_mapping_for_run.sh
bash ./RNA-seq_unstr_2_quantification_for_run.sh
