#!/usr/bin/env python

from __future__ import print_function
import sys

output_file = open("cuffdiff_result_mRNA_all_filtered.txt", 'w')


for line in open("cuffdiff_result_mRNA_all.txt", 'r'):    # Cuffdiff result all
    line = line.rstrip()
    data = line.split("\t")
    if data[0] == "gr_id":
        sample_list = []
        for x in range(3, len(data), 4):
            status = data[x]
            value1 = data[x+1]
            value2 = data[x+2]
            FC = data[x+3]
            sample_list.extend([FC])
        print("\t".join(data[:3]), "\t".join(sample_list), sep="\t", end="\n", file=output_file)
        continue
    ref_id = data[1]
    sample_list = []
    for x in range(3, len(data), 4):
        status = data[x]
        value1 = data[x+1]
        value2 = data[x+2]
        FC = data[x+3]
        if status == "NOTEST" or status == "FAIL":
            FC = "NA"
        if FC == "inf" or FC == "-inf":
            FC = "NA"
        try:
            if float(value1) < 2 and float(value2) < 2:
                FC = "NA"
            else:
                FC = round(float(FC), 2)
        except:
            FC = "NA"
        sample_list.extend([str(FC)])
    print("\t".join(data[:3]), "\t".join(sample_list), sep="\t", end="\n", file=output_file)
