#!/bin/bash
query=${1}
esearch -db sra -query ${query} | efetch --format runinfo | cut -d ',' -f 1,16,20,30,13,14,15,10,28,29 > srafile_url.txt
esearch -db sra -query ${query} | efetch --format native > srafile_xml.txt
python ~/custom_command/parse_sra_xml_NEW.py srafile_xml.txt srafile_url.txt srafile_name.txt ${query}

# Download SRA files
esearch -db sra -query ${query} | efetch --format runinfo | cut -d ',' -f 10 > srafile.txt
wget -i srafile.txt
python ~/custom_command/rename_sra_files.py srafile_name.txt
