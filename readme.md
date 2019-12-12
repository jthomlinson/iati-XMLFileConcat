This code is provided as is. Not warranty is given or implied.

Author: John Thomlinson
Company: Cluster Analytics Ltd
Date: 2019-12-12

The following command creates the file out.xml containing the concatenated XML content from all .xml files in the directory 'iati_files' that contain the root tag 'iati-activities':
 
> python3.7 XMLFileConcat.py -f iati-activities -o ~/Development/HumAI_data/test_data/out.xml -t iati ~/Development/HumAI_data/test_data/iati_files/