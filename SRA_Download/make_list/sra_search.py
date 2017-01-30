#!/usr/bin/env python

# Usage: python parse_sra_xml.py

from __future__ import print_function
import sys
import xml.etree.ElementTree as ET
import re
import subprocess

query = sys.argv[1]

command_1 = "esearch -db bioproject -query '({0}) AND \"Homo sapiens\"[porgn:__txid9606]' | efetch > bioproject_number.txt".format(query)
proc_1 = subprocess.call(command_1, shell = True)

output_biop_file = open("bioproject_input_{0}.txt".format(query), 'w')
for line in open('bioproject_number.txt', 'r'):
    line = line.rstrip()
    name = "PRJNA{0}".format(line)
    print(name, end="\n", file=output_biop_file)

output_biop_file.close()
