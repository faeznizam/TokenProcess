import pandas as pd
import os



def main():
    folder_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\TM File (to submit for CYBS token)\Oct\291024'
    
    file_mappings = {
        'RHB' : 'RHB',
        'BMMB': 'BMMB',
        'BSN' : 'BSN',
        '_UTS_': 'UTS' 
    }
    
    master_list = []

    for file in os.listdir(folder_path):
        if '_SF' in file:
            # Determine the file name based on mappings
            file_name = next((name for key, name in file_mappings.items() if key in file), None)
            
            if file_name:
                # Process the file
                file_path = os.path.join(folder_path, file)
                df = pd.read_excel(file_path)
                total_records = len(df)
                success_count = df['IPay88 Tokenized ID'].notna().sum()  # Count non-null values for success

                # Append to master_list
                master_list.append({
                    'Agency': file_name,
                    'Total records': total_records,
                    'Success': success_count,
                    'Failed': total_records - success_count
                })
            
    master_table = pd.DataFrame(master_list)
    
    grouped_master_table = master_table.groupby('Agency').agg({
                            'Total records' : 'sum',
                            'Success' : 'sum',
                            'Failed' : 'sum'
    })

    grouped_master_table = grouped_master_table.reset_index()

    grouped_master_table.to_excel(os.path.join(folder_path, 'Summary File.xlsx'), index=False)

    



if __name__ == '__main__':
    main()
