#!/usr/bin/env python

from __future__ import print_function
import sys

input_file = open(sys.argv[1], 'r')
mode_infor = sys.argv[2] # SINGLE, PAIRED
project_dict = sys.argv[3] # 20_PRJNA312917

filename_srrid_dict = {}
filename_label_dict = {}
Project_id = ""

output_file = open("RNA-seq_unstr_0_sra2fastq_for_run.sh", 'w')
sra2fastq_count = 0
core_line_1 = """#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -soft -l ljob,lmem
#$ -l s_vmem=4G
#$ -l mem_req=4G

"""
print(core_line_1, end="\n", file=output_file)

sra2fastq_job_list = []
for line in input_file:
    line = line.rstrip()
    data = line.split("\t")
    Project_id = data[0]
    srr_id = data[1]
    file_name = data[2]

    # create each sra2fastq script
    output_sra_file = open("RNA-seq_unstr_0_sra2fastq_No{0}.sh".format(sra2fastq_count), 'w')
    sra_name = "{0}_{1}.sra".format(srr_id, file_name)
    sra_line_2 = ""
    if mode_infor == "SINGLE":
        sra_line_2 = "fastq-dump {0}".format(sra_name)
    elif mode_infor == "PAIRED":
        sra_line_2 = "fastq-dump --split-files {0}".format(sra_name)
    print(core_line_1, end="\n", file=output_sra_file)
    print(sra_line_2, end="\n", file=output_sra_file)

    # Create qsub line for sra2fastq
    job_id = "sra2fastq_{0}_{1}".format(project_dict, sra2fastq_count)
    sra2fastq_job_list.append(job_id)
    qsub_line = "qsub -N {1} ./RNA-seq_unstr_0_sra2fastq_No{0}.sh".format(sra2fastq_count, job_id)
    print(qsub_line, end="\n", file=output_file)

    sra2fastq_count += 1
    output_sra_file.close()


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

# sra2fstq run script
x_analysis_name = "RNA-seq_unstr_0_X_analysis_for_run.sh"    # Merge, mapping, quant
merge_fastq_line = "qsub -hold_jid {0} {1}".format(','.join(sra2fastq_job_list), x_analysis_name)
print(merge_fastq_line, end="\n", file=output_file)

# merge, mapping, quant run script
merge_fastq_file = open(x_analysis_name, 'w')
print(core_line_1, end="\n", file=merge_fastq_file)
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

ref_infor = {}
ref_infor_edger = {}
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
        print("bash ./RNA-seq_unstr_single-end_1_mapping.sh {0}".format(fastq_name), end="\n", file=output_file)
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    elif mode_infor == "PAIRED":
        print("bash ./RNA-seq_unstr_paired-end_1_mapping.sh {0}".format(fastq_name), end="\n", file=output_file)
        job_id_list.append("job_{0}_{1}".format(Project_id, str(job_count)))
    else:
        print("Error: mode_infor should be SINGLE or PAIRED")
        sys.exit()
    job_count += 1

    filepass = "./STAR_output_{0}/{0}_4_STAR_result_Aligned.sortedByCoord.out.bam".format(srr_name)
    filepass_edger = "./featureCounts_result_{0}/featureCounts_result_{0}_for_R.txt".format(srr_name)
    for sample_label in label_list:
        sample_label_counter = sample_label.replace("C", "")
        sample_label_counter = sample_label_counter.replace("T", "")
        if not sample_label_counter in count_list:
            count_list.append(sample_label_counter)
        if not sample_label in ref_infor:
            ref_infor[sample_label] = [filepass]
            ref_infor_edger[sample_label] = [filepass_edger]
        elif not filepass in ref_infor[sample_label]:
            ref_infor[sample_label].append(filepass)
            ref_infor_edger[sample_label].append(filepass_edger)

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

    # edgeR
    edger_filepass = []
    control_filepass_edger = ref_infor_edger[control]
    treated_filepass_edger = ref_infor_edger[treated]
    edger_filepass.extend(control_filepass_edger)
    edger_filepass.extend(treated_filepass_edger)
    edger_control = ["C"] * len(control_filepass_edger)
    edger_treatment = ["T"] * len(treated_filepass_edger)
    edger_label = []
    edger_label.extend(edger_control)
    edger_label.extend(edger_treatment)

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

    # Cuffdiff
    print(test, file=output_file)
    print(filename, file=output_file)
    print("\n", file=output_file)
    print(test2, file=output_file)
    print(",".join(control_filepass), " \\", sep=" ", end="\n", file=output_file)
    print(",".join(treated_filepass), sep=" ", end="\n", file=output_file)
    print(test3, file=output_file)

    # edgeR
    print("mkdir edgeR_output_${filename}", end="\n", file=output_file)
    print("Rscript ~/custom_command/edgeR_test.R", " \\", sep=" ", end="\n", file=output_file)
    print(",".join(edger_filepass), " \\", sep=" ", end="\n", file=output_file)
    print(",".join(edger_label), " \\", sep=" ", end="\n", file=output_file)
    print("edgeR_output_${filename}", " \\", sep=" ", end="\n", file=output_file)
    if len(control_filepass) == 1 and len(treated_filepass) == 1:
        print("No", end="\n", file=output_file)
    else:
        print("Yes", end="\n", file=output_file)

    rdger_line ="""
# Add Annotation
gene_list="/home/akimitsu/database/gencode.v19.annotation_filtered_symbol_type_list.txt"
python2 ~/custom_command/annotate_gene_symbol_type.py  ${gene_list} edgeR_output_${filename}/edgeR_test_result.txt edgeR_output_${filename}/edgeR_test_result_anno_plus.txt
python2 ~/custom_command/split_into_each_gene_type.py edgeR_output_${filename}/edgeR_test_result_anno_plus.txt
"""
    print(rdger_line, end="\n", file=output_file)

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
