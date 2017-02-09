#!/usr/bin/env python

from __future__ import print_function
import sys
import re

project_id = sys.argv[2]

# Create sra parallel shell script
sra_parallel_file = open("sra_parallel_download.sh", 'w')
core_line ="""#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

"""
print(core_line, end="\n", file=sra_parallel_file)

# Create rename sra files run script
rename_sra_file = open("sra_rename.sh", 'w')
rename_sra_line_1 = "python ~/custom_command/rename_sra_files.py srafile_name.txt"
rename_sra_line_2 = """
dirpath=`pwd`
dirname=`basename ${dirpath}`
python ~/custom_command/slack_bot.py ${dirname}_download_was_finished
"""
print(core_line, end="\n", file=rename_sra_file)
print(rename_sra_line_1, end="\n", file=rename_sra_file)
print(rename_sra_line_2, end="\n", file=rename_sra_file)
rename_sra_file.close()

job_id = 0
sra_download_job_list = []
for line in open(sys.argv[1], 'r'):
    url = line.rstrip()
    if not re.match('^https', url):
        continue
    # Create each wget shell script
    filename = "sra_wget_download_No{0}.sh".format(job_id)
    sra_download_file = open(filename, 'w')
    sra_download_job_id = "sra_download_{0}_{1}".format(project_id, job_id)
    sra_download_job_list.append(sra_download_job_id)
    wget_line = "wget  {0}".format(url)
    print(core_line, end="\n", file=sra_download_file)
    print(wget_line, end="\n", file=sra_download_file)

    # Add sra parallel line to sra parallel shell script
    sra_parallel_line = "qsub -N {0} {1}".format(sra_download_job_id, filename)
    print(sra_parallel_line, end="\n", file=sra_parallel_file)

    sra_download_file.close()
    job_id += 1

sra_parallel_line_1 = "qsub -hold_jid {0} {1}".format(','.join(sra_download_job_list), "sra_rename.sh")
print(sra_parallel_line_1, end="\n", file=sra_parallel_file)
sra_parallel_file.close()
