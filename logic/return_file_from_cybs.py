"""
CODE PURPOSE: 
1. To map data from result file from EBC to original sales file. 
2. The code should add 2 new column to display token and instrument identifier. 
3. The code should check whether the instrument identifier last 4 digit is match with 
    truncated cc last 4 digit. 
"""

# import module
import logging
import os
import re
from .helper_return_file_from_cybs import process_file, map_to_original_file, analyze_result, create_upload_ready_file, match_status

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_batch_id(filename):
    # use regex to extract 8 digits number from file name
    match = re.search(r'\d{8}', filename)
    return match.group() if match else None


def index_files_by_batch_id(file_list):
    # create a dictionary where batch id becomes key and file name for sent and return as value

    batch_files = {}

    for file in file_list:
        batch_id = extract_batch_id(file)

        if batch_id:
            if batch_id not in batch_files:
                batch_files[batch_id] = {'send': None, 'return': None}

            if 'MCO_UTS' in file or 'New Card Token' in file:
                batch_files[batch_id]['send'] = file

            elif 'unicef_malaysia' in file and 'reply.all' in file:
                batch_files[batch_id]['return'] = file

    return batch_files


def return_file_from_cybs_main(folder_path):

    # get all the file names into list
    file_list = os.listdir(folder_path)

    # organize filename based on batch id in dictionary
    batch_files = index_files_by_batch_id(file_list)

    
    for batch_id, files, in batch_files.items():
        send_file = files['send']
        return_file = files['return']

        # get file path for each file 
        if send_file and return_file:
            send_file_path = os.path.join(folder_path, send_file) # original file
            return_file_path = os.path.join(folder_path, return_file)

            extracted_data_from_result_file = process_file(return_file_path)
            df = map_to_original_file(send_file_path, extracted_data_from_result_file, folder_path, send_file)
            status = match_status(df)
            analyze_result(folder_path)
            create_upload_ready_file(folder_path)

            logging.info(f"Process complete for batch {batch_id}. {status}")

