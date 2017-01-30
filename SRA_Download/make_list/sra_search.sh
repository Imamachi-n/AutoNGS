#!/bin/bash

query="galactose"

python ~/custom_command/sra_search.py ${query}
python ~/custom_command/parse_sra_xml_for_making_list_NEW.py bioproject_input_${query}.txt srafile_info_${query}.txt
