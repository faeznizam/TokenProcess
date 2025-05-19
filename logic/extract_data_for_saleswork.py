"""
CODE PURPOSE: To extract data from EBC Result csv file to excel file.
"""

# import modules
import pandas as pd
import os
import re

def extract_result_from_result_file(file_path):
    """
    What does this function do?
    1. Open .csv file from file_path given.
    2. Parse the data into list and convert to dataframe and split data into 2 column by '='
    3. Return as dataframe
    """
    
    desired_keys = {'merchantReferenceCode',
                    'paySubscriptionCreateReply_subscriptionID',
                    'paySubscriptionCreateReply_instrumentIdentifierID'
                    }

    parsed_data = []

    

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Skip the first two rows if necessary
        if len(lines) > 2:
            lines = lines[2:]

        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                items = line.split(',')
                parsed_dict = {key: '' for key in desired_keys}
                for item in items:
                    if '=' in item:
                        key, value = item.split('=', 1)  # Split only on the first '='
                        key = key.strip()
                        value = value.strip()
                        if key in desired_keys:
                            parsed_dict[key] = value
                parsed_data.append(parsed_dict)
    
    # Convert the parsed data to a DataFrame manually if needed
    parsed_df = pd.DataFrame(parsed_data)
    
    return parsed_df

def filename_for_result_file(file):
    match = re.search(r'\b\d{6}\b', file)
    return f'Extracted result from {match.group()}.xlsx'

def main():
    folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\SW process\May\20250514\testing'

    for file in os.listdir(folder_path):
        if 'unicef_malaysia' in file and 'reply.all' in file:
            file_path = os.path.join(folder_path, file)
            df = extract_result_from_result_file(file_path)
            df.to_excel(os.path.join(folder_path, filename_for_result_file(file)), index=False)

if __name__ == "__main__":
    main()