import pandas as pd
import os

def process_file(file_path):
    """
    What does this function do?
    1. Open .csv file from file_path given.
    2. Parse the data into list and convert to dataframe and split data into 2 column by '='
    3. Filter parsed df with condition decision = 'ACCEPT'
    4. Return parsed df
    """
    
    desired_keys = {'merchantReferenceCode',
                    'decision',
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
    
    # Filter only 'ACCEPT' rows
    if 'decision' in parsed_df.columns:
        parsed_df = parsed_df[parsed_df['decision'] == 'ACCEPT']
    
    return parsed_df

def populate_truncated_cc(df, column_name):
    """
    What does this function do?
    1. Get df as input parameter
    2. Check if Truncated CC column has data or not.
    3. If not populate with formatted data from Card Number Column.
    4. Handle if Card Number column blank to avoid error. 
    5. Return df
    """
    # Blank truncated cc then populate
    df[column_name] = df[column_name].astype(str)

    df['Truncated CC'] = df.apply(
            lambda row: row[column_name][0:2] + "********" + row[column_name][-4:]
            
            if pd.notna(row[column_name]) and row[column_name] != ''
            else row['Truncated CC'], axis=1 )
    
    return df

def reformat_nat_id(df):
    df['National Id'] = df['National Id'].apply(
        lambda x: x[:6] + '-' + x[6:8] + '-' + x[8:] 
        if isinstance(x, str) and len(x) == 12 and x.isdigit() else x
    )
    return df

def map_to_original_file(file_path, parsed_df, folder_path, filename):
    """
    What does this function do?
    1. Read the send file and assign into original_df variable.
    2. Check if Mobile phone in original_df and merchantreferencecode column in parsed_df.
    3. if yes, merge both original_df and parsed_df
    4. Populate IPay88 Tokenized ID column and Instrument Identifier column.
    5. Populate Truncated CC column.
    6. Save the file.
    7. If no, stop processing and let user know.
    """

    if 'MCO_UTS' in filename:
        original_df = pd.read_excel(file_path, dtype={'Post Code' : str, 'Card Number' : str, 
                                                'Expiry Date': str, 'Payment Submethod': str,
                                                'Membership No' : str, 'National Id' : str})
        
        original_df = reformat_nat_id(original_df)

        if 'Mobile Phone' not in original_df.columns and 'merchantReferenceCode' not in parsed_df.columns:
            print("Unable to Map data to original file. ")
            print("Makesure 'Mobile Phone' column in file with 'MCO_UTS' in file name")
            print("Makesure 'merchantReferenceCode' in file with 'unicef_malaysia' in file name")
        else:
            merged_df = original_df.merge(
                                        parsed_df[[
                                            'merchantReferenceCode',
                                            'paySubscriptionCreateReply_subscriptionID',
                                            'paySubscriptionCreateReply_instrumentIdentifierID'
                                            ]],
                                        left_on='Mobile Phone', 
                                        right_on='merchantReferenceCode', 
                                        how='left')
            
            
            original_df['IPay88 Tokenized ID'] = merged_df['paySubscriptionCreateReply_subscriptionID']
            original_df['Instrument Identifier'] = merged_df['paySubscriptionCreateReply_instrumentIdentifierID']

            # populate truncated CC column.
            original_df = populate_truncated_cc(original_df, 'Card Number')

            original_df.drop(columns=['Card Number','Preferred Change Date'], inplace=True)

            # save file with same file name and additional marking.
            original_df.to_excel(os.path.join(folder_path, f'{filename[:-5]}_SF.xlsx'), index=False)

    elif 'New Card Token' in filename:
        original_df2 = pd.read_excel(file_path)

        original_df2['IPay88 Tokenized ID'] = ''
        original_df2['Instrument Identifier'] = ''

        if 'Pledge ID' not in original_df2.columns and 'merchantReferenceCode' not in parsed_df.columns:
            print("Unable to Map data to original file. ")
            print("Makesure 'Mobile Phone' column in file with 'MCO_UTS' in file name")
            print("Makesure 'merchantReferenceCode' in file with 'unicef_malaysia' in file name")
        else:
            merged_df2 = original_df2.merge(
                                        parsed_df[[
                                            'merchantReferenceCode',
                                            'paySubscriptionCreateReply_subscriptionID',
                                            'paySubscriptionCreateReply_instrumentIdentifierID'
                                            ]],
                                        left_on='Pledge ID', 
                                        right_on='merchantReferenceCode', 
                                        how='left')
            
            original_df2['IPay88 Tokenized ID'] = merged_df2['paySubscriptionCreateReply_subscriptionID']
            original_df2['Instrument Identifier'] = merged_df2['paySubscriptionCreateReply_instrumentIdentifierID']

            # save file with same file name and additional marking.
            original_df2.to_excel(os.path.join(folder_path, f'{filename[:-5]}_SF.xlsx'), index=False)

    




def analyze_result(folder_path):
    file_mappings = {
        'RHB' : 'RHB',
        'BMMB': 'BMMB',
        'BSN' : 'BSN',
        '_UTS_': 'UTS',
        'New Card' : 'New Card' 
    }
    
    master_list = []

    for file in os.listdir(folder_path):
        if '_SF.xlsx' in file:
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


def delete_column(df):
    # TO DELETE UNWANTED COLUMNS.

    delete_column_list = ['Supporter ID', 'First Name', 'Last Name', 
                          'Issuing Bank', 'CardHolder Name', 'Payment Method (DC/CC)', 
                          'Payment Submethod (Mastercard/Visa/Amex)', 'Mobile Number', 
                          'Current Payment Gateway', 'New PL/OT Case Number', 'PAN 16/15 digits'
                          
    ]
    
    df = df.drop(columns=delete_column_list)

    return df

def rename_column(df):
    # RENAME COLUMN BASED ON FILE NAME.

    df = df.rename(columns={
        'Truncated CC' : 'sescore__Card_Number_Masked__c',
        'Expiry Date MM/YY format' : 'sescore__Card_Expiry__c',
        'Pledge ID' : 'sescore__Pledge_Id__c',
        'IPay88 Tokenized ID' : 'sescore__Card_Token__c',
        'Instrument Identifier' : 'MCO_Instrument_Identifier__c'
        })

    return df

def rename_file(filename):
    # USING THE SAME FILE NAME FOR UPDATED FILE.
    
    return f'{filename[:-5]}.csv'


def create_upload_ready_file(folder_path):
    for file in os.listdir(folder_path):
        if 'New Card Token' in file and '_SF' in file:
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path, dtype = {'IPay88 Tokenized ID' : str, 
                                                   'Instrument Identifier' : str}, engine='openpyxl')
            df = populate_truncated_cc(df, 'PAN 16/15 digits')
            df = delete_column(df)
            df = rename_column(df)
            new_file_name = rename_file(file)
            df.to_csv(os.path.join(folder_path, new_file_name), index=False)