#!/usr/bin/env python

from __future__ import print_function
import sys

input_file = open(sys.argv[1], 'r')
mode_infor = sys.argv[2] # SINGLE, PAIRED

filename_srrid_dict = {}
filename_label_dict = {}
Project_id = ""

for line in input_file:
    line = line.rstrip()
    data = line.split("\t")
    Project_id = data[0]
    srr_id = data[1]
    file_name = data[2]
    # Skip non-labeled samples
    if data[3] == '':
        continue
    sample_label_list = data[3].split(',')
    # Prep srr_id & sample_label for each sample
    if not file_name in filename_srrid_dict:
        filename_srrid_dict[file_name] = [srr_id]
        filename_label_dict[file_name] = []
        for sample_label in sample_label_list:
            filename_label_dict[file_name].append(sample_label)
    else:
        filename_srrid_dict[file_name].append(srr_id)
        for sample_label in sample_label_list:
            filename_label_dict[file_name].append(sample_label)

ref_infor = {}
count_list = []

output_file = open("RNA-seq_unstr_1_mapping_for_run.sh", 'w')
print("#!/bin/bash", file=output_file)
job_count = 0
job_id_list = []

for file_name in filename_srrid_dict.keys():
    srr_list = filename_srrid_dict[file_name]    # SRR001, SRR002
    label_list = filename_label_dict[file_name]    # C0, T0, C1, T1

    # Prep filepass
    srr_name = "{0}_{1}".format("-".join(srr_list), file_name)

    # Mapping shell scripts
    fastq_name = "{0}.fastq".format(srr_name)
    if mode_infor == "SINGLE":
        print("qsub -N job_{1}_{2} ./RNA-seq_unstr_single-end_1_mapping.sh {0}".format(fastq_name, Project_id, str(job_count)), end="\n", file=output_file)
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    elif mode_infor == "PAIRED":
        print("qsub -N job_{1}_{2} ./RNA-seq_unstr_paired-end_1_mapping.sh {0}".format(fastq_name, Project_id, str(job_count)), end="\n", file=output_file)
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    else:
        print("Error: mode_infor should be SINGLE or PAIRED")
        sys.exit()
    job_count += 1

    filepass = "./STAR_output_{0}/{0}_4_STAR_result_Aligned.sortedByCoord.out.bam".format(srr_name)
    for sample_label in label_list:
        sample_label_counter = sample_label.replace("C", "")
        sample_label_counter = sample_label_counter.replace("T", "")
        if not sample_label_counter in count_list:
            count_list.append(sample_label_counter)
        if not sample_label in ref_infor:
            ref_infor[sample_label] = [filepass]
        elif not filepass in ref_infor[sample_label]:
            ref_infor[sample_label].append(filepass)

output_file.close()

# Cuffdiff shell scripts
cuffdiff_run_file = open("RNA-seq_unstr_2_quantification_for_run.sh", 'w')
print("#!/bin/bash", file=cuffdiff_run_file)
job_id = '"job_{0}_*"'.format(Project_id)

counter = len(count_list)
cuff_job_id_list = []
for x in range(counter):
    output_file = open("RNA-seq_unstr_2_quantification_No{0}.sh".format(x), 'w')
    print("qsub -N cuffdiff_{2}_No{0} -hold_jid {1} RNA-seq_unstr_2_quantification_No{0}.sh".format(x, ",".join(job_id_list), Project_id), file=cuffdiff_run_file)
    cuff_job_id_list.append("cuffdiff_{1}_No{0}".format(x, Project_id))
    control = "C{0}".format(str(x))
    treated = "T{0}".format(str(x))
    control_filepass = ref_infor[control]
    treated_filepass = ref_infor[treated]
    test ="""#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=32G
#$ -l mem_req=32G

gtfFile="/home/akimitsu/database/gencode.v19.annotation_filtered.gtf"
"""
    filename = 'filename="No{0}"'.format(x)
    test2= """## 5. Quantification
cuffdiff -p 8 --multi-read-correct -o ./cuffdiff_out_${filename} ${gtfFile} \\"""

    test3 ="""
## Annotation
gene_list="/home/akimitsu/database/gencode.v19.annotation_filtered_symbol_type_list.txt" #Required
cuffnorm_data="gene_exp.diff"
# mRNA
gene_type="mRNA"
result_file="cuffdiff_result_mRNA.txt"
python ~/custom_command/cuffdiff_result.py ${gene_list} ./cuffdiff_out_${filename}/${cuffnorm_data} ${gene_type} ./cuffdiff_out_${filename}/${result_file}

# lncRNA
gene_type="lncRNA"
result_file="cuffdiff_result_lncRNA.txt"
python ~/custom_command/cuffdiff_result.py ${gene_list} ./cuffdiff_out_${filename}/${cuffnorm_data} ${gene_type} ./cuffdiff_out_${filename}/${result_file}
"""

    print(test, file=output_file)
    print(filename, file=output_file)
    print("\n", file=output_file)
    print(test2, file=output_file)
    print(",".join(control_filepass), " \\", sep=" ", end="\n", file=output_file)
    print(",".join(treated_filepass), sep=" ", end="\n", file=output_file)
    print(test3, file=output_file)

    output_file.close()

print("qsub -hold_jid {1} RNA-seq_unstr_3_finish.sh".format(x, ",".join(cuff_job_id_list)), file=cuffdiff_run_file)

cuffdiff_run_file.close()

finish_run_file = open("RNA-seq_unstr_3_finish.sh", 'w')
test4 ="""#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

# Slack comment
dirpath=`pwd`
dirname=`basename ${dirpath}`
python ~/custom_command/slack_bot.py ${dirname}_analysis_was_finished
"""
print(test4, file=finish_run_file)
finish_run_file.close()
