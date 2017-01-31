#!/usr/bin/env python

# Usage: python parse_sra_xml.py

from __future__ import print_function
import sys
import xml.etree.ElementTree as ET
import re
import subprocess

def escapeUnicodeEncodeError(string):
    try:
        string = string.replace('&gt;', 'to')
        string = string.replace('&lt;', 'from')
        string = string.replace('&amp;', 'and')
        string = string.replace(u'\u03b1', 'alpha')
        string = string.replace(u'\u03b2', 'beta')
        string = string.replace(u'\u03b3', 'gamma')
        string = string.replace(u'\u03bc', 'u')
        string = string.replace(u'\xef', 'i')
        string = string.replace(u'\xb5', 'u')
        string = string.replace(u'\xa0', ' ')
        string = string.encode('utf-8')
        return(string)
    except:
        return(string)

sra_list = open(sys.argv[1], 'r')
for line in sra_list:
    line = line.rstrip()
    query_name = line
    command_1 = "esearch -db sra -query {0} | efetch --format runinfo | cut -d ',' -f 1,16,20,30,13,14,15,10,28,29 > srafile_url.txt".format(line)
    command_2 = "esearch -db sra -query {0} | efetch --format native > srafile_xml.txt".format(line)
    proc_1 = subprocess.call(command_1, shell = True)
    proc_2 = subprocess.call(command_2, shell = True)

    # Divide url & xml file
    input_file = open("srafile_url.txt", 'r')
    xml_file = open("srafile_xml.txt", 'r')

    input_counter = 0
    input_subfile = ''
    for line in input_file:
        line = line.rstrip()
        data = line.split(',')
        if data[0] == 'Run':
            input_subfile = open("srafile_url_{0}.txt".format(str(input_counter)), 'w')
            input_counter += 1
            continue
        print(line, end="\n", file=input_subfile)

    try:
        input_subfile.close()
    except:
        print(query_name, " : Cannot access SRA database")
        continue

    xml_counter = 0
    input_subfile = ''
    for line in xml_file:
        line = line.rstrip()
        if line == '<?xml version="1.0"  ?>':
            input_subfile = open("srafile_xml_{0}.txt".format(str(xml_counter)), 'w')
            print(line, end="\n", file=input_subfile)
            xml_counter += 1
            continue
        print(line, end="\n", file=input_subfile)

    try:
        input_subfile.close()
    except:
        print(query_name, " : Cannot access SRA database")
        continue

    output_file = open(sys.argv[2], 'a')

    # Parse Runinfo file
    ref_infor = {}
    for sra_url_number in range(input_counter):
        sra_url_file = "srafile_url_{0}.txt".format(str(sra_url_number))
        for line in open(sra_url_file, 'r'):
            line = line.rstrip()
            if line == '':
                continue
            data = line.split(',')
            srr_id = data[0]    # SRR
            srr_url = data[1]    # https://
            lib_strategy = data[2]    # RNA-seq
            lib_source = data[3]    # cDNA
            lib_selection = data[4]    # TRANSCRIPTOMIC
            mode = data[5]    # PAIRED
            model = data[6]    # Illumina HiSeq 2000
            tax_id = data[7]    # 9606
            speices = data[8]    # Homo Sapiens
            gsm_id = data[9]    # GSM
            # SRR, RNA-seq, PAIRED, TRANSCRIPTOMIC, cDNA, Illumina HiSeq 2000, GSM, 9606, Homo Sapiens, https://
            infor = "{0}||{1}||{2}||{3}||{4}||{5}||{6}||{7}||{8}||{9}".format(srr_id, lib_strategy, mode, lib_selection, lib_source, model, gsm_id, tax_id, speices, srr_url)
            if not srr_id in ref_infor:
                ref_infor[srr_id] = [infor]
            else:
                ref_infor[srr_id].append(infor)

    # Parse XML file
    for sra_xml_number in range(xml_counter):
        sra_xml_file = "srafile_xml_{0}.txt".format(str(sra_xml_number))
        tree = ''
        root = ''
        try:
            tree = ET.parse(sra_xml_file)
            root = tree.getroot()
        except:
            print(query_name, " : Several XML file include in srafile_xml.txt")
            command_3 = "rm srafile_url_*"
            proc_3 = subprocess.call(command_3, shell = True)
            command_4 = "rm srafile_xml_*"
            proc_4 = subprocess.call(command_4, shell = True)
            continue

        # GSM each information level
        for child_1 in root:
            value_infor = child_1.findall('.//VALUE')
            tag_infor = child_1.findall('.//TAG')
            detail_infor = []
            for (value,tag) in zip(value_infor, tag_infor):
                if tag.text == "GEO Accession":
                    continue
                if re.match('^parent_bioproject', tag.text):
                    continue
                value_name = value.text
                if value_name is None:
                    value_name = "NA"
                value_name = escapeUnicodeEncodeError(value_name)
                detail_infor.append("{0}||{1}".format(tag.text, value_name))
            sample_title = ""
            gsm_id = ""
            for child_2 in child_1:
                if child_2.tag == "EXPERIMENT":
                    gsm_id = child_2.attrib['alias']

                # SRR each information level
                for child_3 in child_2:
                    if child_3.tag == "Member":
                        child_3_attr_dict = child_3.attrib
                        sample_title = "NA"
                        if "sample_title" in child_3_attr_dict:
                            sample_title = re.sub(' ', '_', child_3_attr_dict["sample_title"])
                        sample_title = re.sub(',', '_', sample_title)
                        sample_title = re.sub("'", '', sample_title)
                        sample_title = re.sub('"', '', sample_title)
                        sample_title = re.sub('/', '_', sample_title)
                        sample_title = re.sub('#', '', sample_title)
                        sample_title = re.sub("\(", '', sample_title)
                        sample_title = re.sub("\)", '', sample_title)
                        sample_title = re.sub("\[", '', sample_title)
                        sample_title = re.sub("\]", '', sample_title)
                        sample_title = re.sub("&", 'and', sample_title)
                        sample_title = re.sub("=", '-', sample_title)
                        sample_title = escapeUnicodeEncodeError(sample_title)
                    if child_3.tag == "RUN":
                        srr_id = child_3.attrib['accession']
                        srr_data_list = ref_infor[srr_id]

                        for srr_data in srr_data_list:
                            srr_infor = srr_data.split("||")
                            srr_infor = map(escapeUnicodeEncodeError, srr_infor)
                            detail_infor = map(escapeUnicodeEncodeError, detail_infor)
                            print(query_name, srr_infor[0], sample_title, escapeUnicodeEncodeError(gsm_id), "\t".join(srr_infor[1:]), "\t".join(detail_infor), sep="\t", end="\n", file = output_file)

    command_5 = "rm srafile_url_*"
    proc_5 = subprocess.call(command_5, shell = True)
    command_6 = "rm srafile_xml_*"
    proc_6 = subprocess.call(command_6, shell = True)
