#!/usr/bin/env python

import glob
import subprocess

cuffdiff_result_list = glob.glob("[0-9]*/cuffdiff_out_*")

for filepath in cuffdiff_result_list:
    file_dir = filepath.split("/")[0]
    file_name = filepath.split("/")[1]
    cmd_1 = "cp {0}/cuffdiff_result_lncRNA.txt RNA-seq_NCBI_GEO_repository/cuffdiff/{1}_{2}_lncRNA.txt".format(filepath, file_dir, file_name)
    subprocess.call(cmd_1, shell = True)


cuffdiff_result_list = glob.glob("[0-9]*/single_end/cuffdiff_out_*")
for filepath in cuffdiff_result_list:
    file_dir = filepath.split("/")[0]
    file_type = filepath.split("/")[1]
    file_name = filepath.split("/")[2]
    cmd_1 = "cp {0}/cuffdiff_result_lncRNA.txt RNA-seq_NCBI_GEO_repository/cuffdiff/{1}_{3}_{2}_lncRNA.txt".format(filepath, file_dir, file_name, file_type)
    subprocess.call(cmd_1, shell = True)

cuffdiff_result_list = glob.glob("[0-9]*/paired_end/cuffdiff_out_*")
for filepath in cuffdiff_result_list:
    file_dir = filepath.split("/")[0]
    file_type = filepath.split("/")[1]
    file_name = filepath.split("/")[2]
    cmd_1 = "cp {0}/cuffdiff_result_lncRNA.txt RNA-seq_NCBI_GEO_repository/cuffdiff/{1}_{3}_{2}_lncRNA.txt".format(filepath, file_dir, file_name, file_type)
    subprocess.call(cmd_1, shell = True)
