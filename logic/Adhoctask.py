import pandas as pd
import os

def process_file(file_path, file_name):
    """
    Open .csv file from file_path given.
    Parse the data into list and convert to dataframe and split data into 2 columns by '='.
    Filter parsed df with condition decision = 'ACCEPT'.
    Add a column with the file name.
    Return the parsed DataFrame.
    """
    desired_keys = {'merchantReferenceCode',
                    'decision',
                    'paySubscriptionCreateReply_subscriptionID',
                    'paySubscriptionCreateReply_instrumentIdentifierID'}

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
    
    # Filter only 'ACCEPT' rows
    if 'decision' in parsed_df.columns:
        parsed_df = parsed_df[parsed_df['decision'] == 'ACCEPT']
    
    # Add a column with the file name
    parsed_df['file_name'] = file_name
    
    return parsed_df

# Base directory where files are stored
import pandas as pd
import os

base_directory = r"C:\Users\mfmohammad\Downloads\File from UAT"
"""
combined_list = []

for subfolder in os.listdir(folder_path):
    subfolder_path = os.path.join(folder_path, subfolder)
    
    # Check if it's a directory
    if os.path.isdir(subfolder_path):  
        for item in os.listdir(subfolder_path):
            if 'MCO_' in item and '_SF' in item:
                item_path = os.path.join(subfolder_path, item)
                
                # Read the Excel file
                df = pd.read_excel(item_path)

                # Add source file and folder information
                df['Source File Name'] = item
                df['Folder Name'] = subfolder  # Uncomment this if you want folder info

                combined_list.append(df)

# Combine all DataFrames
combined_df = pd.concat(combined_list, ignore_index=True)

# Save the combined DataFrame to Excel
output_path = os.path.join(folder_path, "master_list_dec.xlsx")
combined_df.to_excel(output_path, index=False)

print('Completed')

"""
import os
import pandas as pd

base_directory = r"C:\Users\mfmohammad\Downloads\File from UAT"

# Desired keys to extract
desired_keys = {
    'merchantReferenceCode',
    'decision',
    'paySubscriptionCreateReply_subscriptionID',
    'paySubscriptionCreateReply_instrumentIdentifierID'
}

parsed_data = []  # List to store parsed data

# Loop through items in the directory
for item in os.listdir(base_directory):
    if 'unicef_malaysia' in item and 'reply.all' in item:
        file_path = os.path.join(base_directory, item)
        
        # Read and parse the file
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
                    
                    for entry in items:
                        if '=' in entry:
                            key, value = entry.split('=', 1)  # Split only on the first '='
                            key = key.strip()
                            value = value.strip()
                            if key in desired_keys:
                                parsed_dict[key] = value
                    
                    # Add the file name to the parsed_dict
                    parsed_dict['file_name'] = item
                    parsed_data.append(parsed_dict)

# Convert the parsed data to a DataFrame
parsed_df = pd.DataFrame(parsed_data)

# Filter only 'ACCEPT' rows
if 'decision' in parsed_df.columns:
    parsed_df = parsed_df[parsed_df['decision'] == 'ACCEPT']

# Save the DataFrame to an Excel file
output_file = os.path.join(base_directory, "data_from_uat.xlsx")
parsed_df.to_excel(output_file, index=False)

print(f"Data processing completed. Output saved at: {output_file}")
