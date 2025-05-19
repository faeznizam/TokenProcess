import pandas as pd
import os

import os
import pandas as pd

directory_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\TM File (to submit for CYBS token)\2025\May'

master_list = []

for folder in os.listdir(directory_path):
    folder_path = os.path.join(directory_path, folder)

    # ✅ Check if it's a directory before continuing
    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('_SF.xlsx'):
                file_path = os.path.join(folder_path, file)

                df = pd.read_excel(
                        file_path,
                        dtype={
                            'Post Code': str,
                            'Instrument Identifier': str
                        }
                    )
                
                #filtered_df = df[df['Action'] == 'RDA']

                #master_list.append(filtered_df)

                master_list.append(df)
                
                """
                try:
                    df = pd.read_excel(
                        file_path,
                        dtype={
                            'Post Code': str,
                            'Instrument Identifier': str
                        }
                    )

                    required_cols = ['Instrument Identifier', 'IPay88 Tokenized ID']
                    if all(col in df.columns for col in required_cols):
                        filtered_df = df[required_cols].copy()
                        filtered_df['Source'] = file
                        master_list.append(filtered_df)
                    else:
                        print(f"Skipping {file}: Missing required columns")

                except Exception as e:
                    print(f"Error reading {file}: {e}")

                """

# Only write if there's data
if master_list:
    master_df = pd.concat(master_list, ignore_index=True)
    output_path = os.path.join(directory_path, 'masterlist_all.xlsx')
    master_df.to_excel(output_path, index=False)
    print(f"Masterlist created: {output_path}")
else:
    print("No valid files found. Masterlist not created.")
