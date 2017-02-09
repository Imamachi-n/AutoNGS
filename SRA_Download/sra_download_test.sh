#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

projectID="PRJNA264147"

sra_download.sh ${projectID}
python ~/custom_command/slack_bot.py ${projectID}_download_was_finished
