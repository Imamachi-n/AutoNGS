#!/usr/bin/env python

from __future__ import print_function
import sys
import subprocess

input_file = open(sys.argv[1], 'r')
mode_infor = sys.argv[2] # SINGLE, PAIRED

infor_dict = {}
for line in input_file:
    line = line.rstrip()
    data = line.split("\t")
    srr_id = data[1]
    file_name = data[2]
    if not file_name in infor_dict:
        infor_dict[file_name] = [srr_id]
    else:
        infor_dict[file_name].append(srr_id)

for file_name in infor_dict.keys():
    srr_list = infor_dict[file_name]
    if len(srr_list) == 1:
        continue
    if mode_infor == 'SINGLE':
        srr_name_list = ["{0}_{1}.fastq".format(x, file_name) for x in srr_list]
        command = "cat {0} > {1}".format(" ".join(srr_name_list), "{0}_{1}.fastq".format("-".join(srr_list), file_name))
        proc = subprocess.call(command, shell = True)
    elif mode_infor == 'PAIRED':
        srr_name_list_1 = ["{0}_{1}_1.fastq".format(x, file_name) for x in srr_list]
        srr_name_list_2 = ["{0}_{1}_2.fastq".format(x, file_name) for x in srr_list]
        command_1 = "cat {0} > {1}".format(" ".join(srr_name_list_1), "{0}_{1}_1.fastq".format("-".join(srr_list), file_name))
        command_2 = "cat {0} > {1}".format(" ".join(srr_name_list_2), "{0}_{1}_2.fastq".format("-".join(srr_list), file_name))
        proc_1 = subprocess.call(command_1, shell = True)
        proc_2 = subprocess.call(command_2, shell = True)
    else:
        print("ERROR: Mode Information was wrong...")
        print("Choose SINGLE or PAIRED.")

# re.split(r'SRR[0-9]+','SRR1981274_RNA-seq_on_DMSO-treated_cells_treated_for_72_hrs-2_2.fastq')
# re.match(r'SRR[0-9]+','SRR1981274_RNA-seq_on_DMSO-treated_cells_treated_for_72_hrs-2_2.fastq').group()
