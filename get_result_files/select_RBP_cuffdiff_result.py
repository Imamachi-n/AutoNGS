#!/usr/bin/env python

from __future__ import print_function
import sys

output_file = open("cuffdiff_result_mRNA_RBP_compilation.txt", 'w')

ref_dict = {}
for line in open("RBP_Compilation_list.txt", 'r'):    # RBP compilation list
    line = line.rstrip()
    data= line.split("\t")
    ref_id = data[0]
    gene_symbol = data[1]
    ref_dict[ref_id] = gene_symbol

for line in open("cuffdiff_result_mRNA_all.txt", 'r'):    # Cuffdiff result all
    line = line.rstrip()
    data = line.split("\t")
    if data[0] == "gr_id":
        sample_list = []
        for x in range(3, len(data), 2):
            status = data[x]
            value = data[x+1]
            sample_list.extend([value])
        print("\t".join(data[:3]), "\t".join(sample_list), sep="\t", end="\n", file=output_file)
        continue
    ref_id = data[1].split(".")[0]
    if ref_id in ref_dict:
        # test_list = [data[x] for x in range(3, len(data), 2)]
        sample_list = []
        for x in range(3, len(data), 2):
            status = data[x]
            value = data[x+1]
            if status == "NOTEST" or status == "FAIL":
                value = "0"
            if value == "inf" or value == "-inf":
                value = "0"
            # sample_list.extend([status, value])
            sample_list.extend([value])
        # ok_list = [x for x in test_list if x == "OK"]
        # if (len(ok_list) / len(test_list)) >= 0.5:
        print("\t".join(data[:3]), "\t".join(sample_list), sep="\t", end="\n", file=output_file)
