#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

dirpath=`pwd`
projectID=`basename ${dirpath}`

# sra_download.sh ${projectID}
wget -i srafile.txt
python ~/custom_command/rename_sra_files.py srafile_name.txt
python ~/custom_command/slack_bot.py ${projectID}_download_was_finished
