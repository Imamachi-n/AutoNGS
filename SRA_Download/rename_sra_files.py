#!/usr/bin/env python

from __future__ import print_function
import sys
import subprocess

input_file = open(sys.argv[1], 'r')

for line in input_file:
    line = line.rstrip()
    data = line.split("\t")
    command = "mv {0} {1}{2}".format(data[1], "_".join([data[1], data[2]]), ".sra")
    proc = subprocess.call(command, shell = True)
