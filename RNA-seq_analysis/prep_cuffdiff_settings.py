#!/usr/bin/env python

from __future__ import print_function
import sys

## Shell Script Blocks ##############
header_line_4G = """#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

"""

header_line_32G = """#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=32G
#$ -l mem_req=32G

"""

cuffdiff_core_line = """## 5. Quantification
cuffdiff -p 8 --multi-read-correct -o ./cuffdiff_out_${filename} ${gtfFile} \\"""

cuffdiff_anno_line = """
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

edger_line = """
# Add Annotation
gene_list="/home/akimitsu/database/gencode.v19.annotation_filtered_symbol_type_list.txt"
python2 ~/custom_command/annotate_gene_symbol_type.py  ${gene_list} edgeR_output_${filename}/edgeR_test_result.txt edgeR_output_${filename}/edgeR_test_result_anno_plus.txt
python2 ~/custom_command/split_into_each_gene_type.py edgeR_output_${filename}/edgeR_test_result_anno_plus.txt
"""

slack_line ="""# Slack comment
dirpath=`pwd`
dirname=`basename ${dirpath}`
python ~/custom_command/slack_bot.py ${dirname}_analysis_was_finished
"""


###############################

## Input args
sample_label_file = open(sys.argv[1], 'r')    # srafile_name_label.txt
mode_infor = sys.argv[2]    # SINGLE, PAIRED
project_dict = sys.argv[3]    # 20_PRJNA312917


## Create "sra2fastq" run shell script
output_file = open("RNA-seq_unstr_0_sra2fastq_for_run.sh", 'w')
print(header_line_4G, end="\n", file=output_file)


sra2fastq_job_list = []    # sra2fastq qsub job ID
filename_srrid_dict = {}    # SRR5011314,SRR5011315,...
filename_label_dict = {}    # C0,C1,C2,C3,T0,T1,T2,T3,...
Project_id = ""
sra2fastq_count = 0    # The number of SRA files


for line in sample_label_file:
    line = line.rstrip()
    data = line.split("\t")

    # Get basic sample information
    Project_id = data[0]    # PRJNA312917
    srr_id = data[1]    # SRR5011314
    file_name = data[2]    # C0,C1,C2 || T1 || C0,C1,T2

    # Create each "sra2fastq" number shell script for qsub command
    sra2fastq_each_filename = "RNA-seq_unstr_0_sra2fastq_No{0}.sh".format(sra2fastq_count)
    output_sra2fastq_number_file = open(sra2fastq_each_filename, 'w')

    # Prepare SRA file name
    sra_name = "{0}_{1}.sra".format(srr_id, file_name)

    # Add fastq-dump command line in "sra2fastq" number shell script for qsub command
    sra2fastq_No_line_1 = ""
    if mode_infor == "SINGLE":
        sra2fastq_No_line_1 = "fastq-dump {0}".format(sra_name)
    elif mode_infor == "PAIRED":
        sra2fastq_No_line_1 = "fastq-dump --split-files {0}".format(sra_name)
    print(header_line_4G, end="\n", file=output_sra2fastq_number_file)
    print(sra2fastq_No_line_1, end="\n", file=output_sra2fastq_number_file)

    # Add qsub command line in "sra2fastq" run shell script
    job_id = "sra2fastq_{0}_{1}".format(project_dict, sra2fastq_count)
    sra2fastq_job_list.append(job_id)
    qsub_line = "qsub -N {1} ./RNA-seq_unstr_0_sra2fastq_No{0}.sh".format(sra2fastq_count, job_id)
    print(qsub_line, end="\n", file=output_file)

    sra2fastq_count += 1
    output_sra2fastq_number_file.close()


    # Skip non-labeled samples
    if data[3] == '':
        continue

    # Prep sample labels
    sample_label_list = data[3].split(',')    # C0,C1,C2 || T0

    # Prep srr_id & sample_label for each sample
    if not file_name in filename_srrid_dict:
        # Store sample SRA ID
        filename_srrid_dict[file_name] = [srr_id]

        # Store sample labels
        filename_label_dict[file_name] = []
        for sample_label in sample_label_list:
            filename_label_dict[file_name].append(sample_label)
    else:
        # Store sample SRA ID
        filename_srrid_dict[file_name].append(srr_id)

        # Store sample labels
        for sample_label in sample_label_list:
            filename_label_dict[file_name].append(sample_label)

## Add qsub command in "sra2fastq" run shell script
x_analysis_name = "RNA-seq_unstr_0_X_analysis_for_run.sh"    # Merge, mapping, quant
merge_fastq_line = "qsub -hold_jid {0} {1}".format(','.join(sra2fastq_job_list), x_analysis_name)
print(merge_fastq_line, end="\n", file=output_file)

# merge, mapping, quant run shell script
merge_fastq_file = open(x_analysis_name, 'w')
print(header_line_4G, end="\n", file=merge_fastq_file)

x_analysis_line=""
if mode_infor == "SINGLE":
    x_analysis_line="""
python ~/custom_command/merge_fastq.py srafile_name_label.txt SINGLE
bash ./RNA-seq_unstr_1_mapping_for_run.sh
bash ./RNA-seq_unstr_2_quantification_for_run.sh
"""
elif mode_infor == "PAIRED":
    x_analysis_line="""
python ~/custom_command/merge_fastq.py srafile_name_label.txt PAIRED
bash ./RNA-seq_unstr_1_mapping_for_run.sh
bash ./RNA-seq_unstr_2_quantification_for_run.sh
"""
print(x_analysis_line, end="\n", file=merge_fastq_file)

merge_fastq_file.close()
output_file.close()


ref_infor = {}    # Cuffdiff filepath list
ref_infor_edger = {}    # edgeR filepath list
count_list = []    # The number of pairs (Control vs Treatment)

# Mapping run shell script
output_file = open("RNA-seq_unstr_1_mapping_for_run.sh", 'w')
print("#!/bin/bash", file=output_file)

job_count = 0    # The number of Cuffdiff, edgeR jobs
job_id_list = []    # Mapping job ID list

for file_name in filename_srrid_dict.keys():
    srr_list = filename_srrid_dict[file_name]    # SRR5011314, SRR5011315
    label_list = filename_label_dict[file_name]    # C0, T0, C1, T1

    # Prep filename
    srr_name = "{0}_{1}".format("-".join(srr_list), file_name)

    # Mapping shell scripts
    fastq_name = "{0}.fastq".format(srr_name)
    if mode_infor == "SINGLE":
        print("qsub -N job_{1}_{2} ./RNA-seq_unstr_single-end_1_mapping.sh {0}".format(fastq_name, Project_id, str(job_count)), end="\n", file=output_file)
        # Prep job ID list
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    elif mode_infor == "PAIRED":
        print("qsub -N job_{1}_{2} ./RNA-seq_unstr_paired-end_1_mapping.sh {0}".format(fastq_name, Project_id, str(job_count)), end="\n", file=output_file)
        # Prep job ID list
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    else:
        print("Error: mode_infor should be SINGLE or PAIRED")
        sys.exit()
    job_count += 1

    # Prep sample filepath (Cuffdiff, edgeR)
    filepass = "./STAR_output_{0}/{0}_4_STAR_result_Aligned.sortedByCoord.out.bam".format(srr_name)
    filepass_edger = "./featureCounts_result_{0}/featureCounts_result_{0}_for_R.txt".format(srr_name)

    for sample_label in label_list:
        # Count the number of cuffdiff, edgeR jobs.
        sample_label_counter = sample_label.replace("C", "")
        sample_label_counter = sample_label_counter.replace("T", "")
        if not sample_label_counter in count_list:
            count_list.append(sample_label_counter)

        # Prep sample filepath list (Cuffdiff, edgeR)
        if not sample_label in ref_infor:
            ref_infor[sample_label] = [filepass]
            ref_infor_edger[sample_label] = [filepass_edger]
        elif not filepass in ref_infor[sample_label]:
            ref_infor[sample_label].append(filepass)
            ref_infor_edger[sample_label].append(filepass_edger)

output_file.close()

# Cuffdiff/edgeR run shell scripts
cuffdiff_run_file = open("RNA-seq_unstr_2_quantification_for_run.sh", 'w')
print("#!/bin/bash", file=cuffdiff_run_file)

# Prep job ID
job_id = '"job_{0}_*"'.format(Project_id)

counter = len(count_list)    # The number of pairs (Control vs Treatment)
cuff_job_id_list = []    # Cuffdiff, edgeR job ID list

for x in range(counter):
    # Create each "Cuffdiff, edgeR" number shell script for qsub command
    output_file = open("RNA-seq_unstr_2_quantification_No{0}.sh".format(x), 'w')

    # Add bash command in cuffdiff, edgeR run shell script.
    print("qsub -N cuffdiff_{2}_No{0} -hold_jid {1} RNA-seq_unstr_2_quantification_No{0}.sh".format(x, ",".join(job_id_list), Project_id), file=cuffdiff_run_file)

    # Prep cuffdiff, edgeR job ID
    cuff_job_id_list.append("cuffdiff_{1}_No{0}".format(x, Project_id))

    # Prep cuffdiff filepath lists (Control & Treatment)
    control = "C{0}".format(str(x))
    treated = "T{0}".format(str(x))
    control_filepass = ref_infor[control]
    treated_filepass = ref_infor[treated]

    # Prep edgeR filepath lists (Control + Treatment)
    edger_filepass = []
    control_filepass_edger = ref_infor_edger[control]
    treated_filepass_edger = ref_infor_edger[treated]
    edger_filepass.extend(control_filepass_edger)
    edger_filepass.extend(treated_filepass_edger)

    # Prepr edgeR label lists (Control + Treatment)
    edger_control = ["C"] * len(control_filepass_edger)
    edger_treatment = ["T"] * len(treated_filepass_edger)
    edger_label = []
    edger_label.extend(edger_control)
    edger_label.extend(edger_treatment)

    # qsub job ID
    filename = 'filename="No{0}"'.format(x)

    # Add Cuffdiff number shell script for qsub command
    print(header_line_32G, file=output_file)
    print('gtfFile="/home/akimitsu/database/gencode.v19.annotation_filtered.gtf"', file=output_file)
    print(filename, file=output_file)
    print("\n", file=output_file)
    print(cuffdiff_core_line, file=output_file)
    print(",".join(control_filepass), " \\", sep=" ", end="\n", file=output_file)
    print(",".join(treated_filepass), sep=" ", end="\n", file=output_file)
    print(cuffdiff_anno_line, file=output_file)

    # Add edgeR number shell script for qsub command
    print("mkdir edgeR_output_${filename}", end="\n", file=output_file)
    print("Rscript ~/custom_command/edgeR_test.R", " \\", sep=" ", end="\n", file=output_file)
    print(",".join(edger_filepass), " \\", sep=" ", end="\n", file=output_file)
    print(",".join(edger_label), " \\", sep=" ", end="\n", file=output_file)
    print("edgeR_output_${filename}", " \\", sep=" ", end="\n", file=output_file)

    # Check Duplicate
    if len(control_filepass_edger) == 1 and len(treated_filepass_edger) == 1:
        print("No", end="\n", file=output_file)
    else:
        print("Yes", end="\n", file=output_file)

    print(edger_line, end="\n", file=output_file)

    output_file.close()

## Add bash command in cuffdiff, edgeR run shell script.
print("qsub -hold_jid {1} RNA-seq_unstr_3_finish.sh".format(x, ",".join(cuff_job_id_list)), file=cuffdiff_run_file)

cuffdiff_run_file.close()

# Slack finish shell script
finish_run_file = open("RNA-seq_unstr_3_finish.sh", 'w')
print(header_line_4G, file=finish_run_file)
print(slack_line, file=finish_run_file)
finish_run_file.close()
