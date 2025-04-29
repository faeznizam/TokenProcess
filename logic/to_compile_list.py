"""
THIS CODE IS FOR COMPILING ALL TOKEN FROM CYBS FOLDER
"""

import os
import pandas as pd

# folder path
folder_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\TM File (to submit for CYBS token)\2024'
download_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\TM File (to submit for CYBS token)'

master_list = []

for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        if '_SF.xlsx' in file and 'MCO_' in file:
            
            
            df = pd.read_excel(file_path, dtype={'Instrument Identifier' : str, 'PAN 16/15 digits': str})

            df['Source File'] = file

            #df['4 Digit Truncated'] = df['Truncated CC'].apply(lambda x : x[-4:])
            #df['4 Instrument Identifier'] = df['Instrument Identifier'].apply(lambda x: str(x)[-4:] if pd.notnull(x) else None) 
            


            master_list.append(df)

# combine all df by concat. 
master_list_df = pd.concat(master_list, ignore_index=True)

# save dataframe to excel
master_list_df.to_excel(os.path.join(download_path, 'masterlist.xlsx'), index=False)

print("Completed")