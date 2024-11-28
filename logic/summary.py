import os
import pandas as pd
import numpy as np
"""
def process_file(file_path):
    desired_keys = {'merchantReferenceCode',
                    'decision',
                    'paySubscriptionCreateReply_subscriptionID',
                    'paySubscriptionCreateReply_instrumentIdentifierID', 
                    'ccAuthReply_processorResponse'
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
"""

import pandas as pd

def process_file(file_path):
    # Use a set for faster lookups
    desired_keys = {
        'merchantReferenceCode',
        'decision',
        'paySubscriptionCreateReply_subscriptionID',
        'paySubscriptionCreateReply_instrumentIdentifierID',
        'ccAuthReply_processorResponse'
    }

    parsed_data = []
    
    with open(file_path, 'r') as file:
        # Skip the first two lines
        next(file)
        next(file)

        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                parsed_dict = {key: '' for key in desired_keys}
                for item in line.split(','):
                    if '=' in item:
                        key, value = item.split('=', 1)  # Split only on the first '='
                        key = key.strip()
                        value = value.strip()
                        if key in desired_keys:
                            parsed_dict[key] = value
                parsed_data.append(parsed_dict)
    
    # Convert to DataFrame directly
    parsed_df = pd.DataFrame(parsed_data)
    
    return parsed_df


def map_to_original_file(file_path, parsed_df, folder_path, filename, batch_id):

    result_df = None

    if 'MCO_UTS' in filename:
        original_df = pd.read_excel(file_path, dtype={'Post Code' : str, 'Card Number' : str, 
                                                'Expiry Date': str, 'Payment Submethod': str,
                                                'Membership No' : str, 'National Id' : str})

        original_df['Reason Code'] = ''
        original_df['Batch ID'] = batch_id
        original_df['File Name'] = filename
        
        

        if 'Mobile Phone' not in original_df.columns and 'merchantReferenceCode' not in parsed_df.columns:
            print("Unable to Map data to original file. ")
            print("Makesure 'Mobile Phone' column in file with 'MCO_UTS' in file name")
            print("Makesure 'merchantReferenceCode' in file with 'unicef_malaysia' in file name")
        else:
            merged_df = original_df.merge(
                                        parsed_df[[
                                            'merchantReferenceCode',
                                            'paySubscriptionCreateReply_subscriptionID',
                                            'paySubscriptionCreateReply_instrumentIdentifierID',
                                            'ccAuthReply_processorResponse'
                                            ]],
                                        left_on='Mobile Phone', 
                                        right_on='merchantReferenceCode', 
                                        how='left')
            
            
            original_df['IPay88 Tokenized ID'] = merged_df['paySubscriptionCreateReply_subscriptionID']
            original_df['Instrument Identifier'] = merged_df['paySubscriptionCreateReply_instrumentIdentifierID']
            original_df['Reason Code'] = merged_df['ccAuthReply_processorResponse']

            

            if 'DRTV Channel' in original_df.columns and 'Creative' in original_df.columns:
                original_df.drop(columns=[
                    'Donor Id', 'Title', 'First Name', 'Last Name', 'Ethnic', 'Gender', 'Street', 'City', 
                    'State', 'Post Code', 'Country', 'Home Phone', 'Work Phone', 'Mobile Phone', 'Email', 
                    'Date of Birth', 'National Id', 'Last Pledge Amount', 'Last Cash Amount', 'Last Pledge Date', 
                    'Last Cash Date', 'Pledge Date', 'Pledge Start Date', 'Pledge End Date', 
                    'Donation Amount', 'Payment Method', 'Payment Submethod', 'Truncated CC', 'Expiry Date', 
                    'Frequency', 'Cardholder Name', 'Gift Date', 'Campaign', 'Action', 
                    'Bank Account Number', 'Bank Account Holder Name', 'Preferred Change Date', 'Description', 
                    'DRTV Time', 'Bank', 'Unique Id', 'Membership No', 'Card Number', 'DRTV Channel', 'Creative'
                    ], inplace=True)

            else:   
                original_df.drop(columns=[
                    'Donor Id', 'Title', 'First Name', 'Last Name', 'Ethnic', 'Gender', 'Street', 'City', 
                    'State', 'Post Code', 'Country', 'Home Phone', 'Work Phone', 'Mobile Phone', 'Email', 
                    'Date of Birth', 'National Id', 'Last Pledge Amount', 'Last Cash Amount', 'Last Pledge Date', 
                    'Last Cash Date', 'Pledge Date', 'Pledge Start Date', 'Pledge End Date', 
                    'Donation Amount', 'Payment Method', 'Payment Submethod', 'Truncated CC', 'Expiry Date', 
                    'Frequency', 'Cardholder Name', 'Gift Date', 'Campaign', 'Action', 
                    'Bank Account Number', 'Bank Account Holder Name', 'Preferred Change Date', 'Description', 
                    'DRTV Time', 'Bank', 'Unique Id', 'Membership No', 'Card Number'
                    ], inplace=True)

            column_placement = ['Batch ID', 'File Name', 'Campaign Name', 'Pledge id',  'IPay88 Tokenized ID', 'Reason Code', 'Instrument Identifier']

            original_df = original_df[column_placement]

            result_df = original_df

            

    elif 'New Card Token' in filename:
        original_df2 = pd.read_excel(file_path)

        original_df2['IPay88 Tokenized ID'] = ''
        original_df2['Instrument Identifier'] = ''
        original_df2['Reason Code'] = ''
        original_df2['Batch ID'] = batch_id
        original_df2['File Name'] = filename

        if 'Pledge ID' not in original_df2.columns and 'merchantReferenceCode' not in parsed_df.columns:
            print("Unable to Map data to original file. ")
            print("Makesure 'Mobile Phone' column in file with 'MCO_UTS' in file name")
            print("Makesure 'merchantReferenceCode' in file with 'unicef_malaysia' in file name")
        else:
            merged_df2 = original_df2.merge(
                                        parsed_df[[
                                            'merchantReferenceCode',
                                            'paySubscriptionCreateReply_subscriptionID',
                                            'paySubscriptionCreateReply_instrumentIdentifierID',
                                            'ccAuthReply_processorResponse'
                                            ]],
                                        left_on='Pledge ID', 
                                        right_on='merchantReferenceCode', 
                                        how='left')
            
            original_df2['IPay88 Tokenized ID'] = merged_df2['paySubscriptionCreateReply_subscriptionID']
            original_df2['Instrument Identifier'] = merged_df2['paySubscriptionCreateReply_instrumentIdentifierID']
            original_df2['Reason Code'] = merged_df2['ccAuthReply_processorResponse']
            original_df2['Campaign Name'] = 'In House'

            original_df2 = original_df2.rename(columns={'Pledge ID' : 'Pledge id'})

            original_df2.drop(columns=[
                'Supporter ID','First Name', 'Last Name', 'PAN 16/15 digits','Expiry Date MM/YY format',
                'Issuing Bank', 'CardHolder Name', 'Payment Method (DC/CC)', 'Payment Submethod (Mastercard/Visa/Amex)',
                'Mobile Number', 'Current Payment Gateway', 'New PL/OT Case Number'
                ],
                 inplace=True)
            
        
            column_placement = ['Batch ID', 'File Name', 'Campaign Name', 'Pledge id',  'IPay88 Tokenized ID', 'Reason Code', 'Instrument Identifier']

            original_df2 = original_df2[column_placement]

            result_df = original_df2

    return result_df

def analyze_file(df):
    """
    TO ANALYZE FILE BY CREATING A TABLE AND
    GROUP THE DATA BASED ON DATE SENT, AGENCY, AND CAMPAIGN NAME.
    THEN GET THE COUNT FOR TOTAL, SUCCESS, FAILED AND REASON CODE. 
    FINALLY RETURN THE TABLE.
    """
    
    # CREATE AGENCY COLUMN AND POPULATE FROM FILE NAME COLUMN
    conditions = [
    df['File Name'].str.contains('_UTS_', na=False),
    df['File Name'].str.contains('_BSN_', na=False),
    df['File Name'].str.contains('_RHB_', na=False),
    df['File Name'].str.contains('_BMMB_', na=False)
    ]

    choices = ['UTS', 'BSN', 'RHB','BMMB']

    df['Agency'] = np.select(conditions, choices, default='In House')


    # CREATE DATE SENT COLUMN AND POPULATE BY REFORMAT BATCH ID DATA
    df['Date Sent'] = df['Batch ID'].astype(str).apply(lambda x: f'20{x[0:2]}-{x[2:4]}-{x[4:6]}')

    # REPLACE EMPTY STRING WITH NA VALUE SO WE CAN COUNT
    df['IPay88 Tokenized ID'] = df['IPay88 Tokenized ID'].replace('', pd.NA)

    # CREATE A TABLE WHERE WE GROUP BY DATE SENT, AGENCY AND CAMPAIGN NAME THEN COUNT THE NUMBERS
    group = df.groupby(['Date Sent', 'Agency', 'Campaign Name']).agg(
        Total_Count = ('Batch ID', 'count'),
        Total_Success = ('IPay88 Tokenized ID', 'count'),
        Total_Failed = ('IPay88 Tokenized ID', lambda x: x.isna().sum())
    ).reset_index()

    # CREATE SAPERATE TABLE TO CREATE COLUMN BASED ON REASON CODE DATA AND COUNT THE OCCURRENCES
    na_reason_df = df[df['IPay88 Tokenized ID'].isna()]
    reason_code_counts = na_reason_df.groupby(['Date Sent', 'Agency', 'Campaign Name'])['Reason Code'] \
    .value_counts() \
    .unstack(fill_value=0) \
    .reset_index()

    # COMBINE BOTH TABLE 
    result = group.merge(reason_code_counts, on=['Date Sent', 'Agency', 'Campaign Name'], how='left')

    # REPLACE MISSING WITH 0
    result = result.fillna(0)

    print(result)

    return result


def summary_analysis(folder_path):

    batch_id_list = []
    combined_list = []

    for roots, dirs, files in os.walk(folder_path):
        for file in files:
            if 'unicef_' in file and 'reply.all' in file:
                
                # GET BATCH ID
                batch_id = file[16:24]
                batch_id_list.append(batch_id)

    for batch_id in batch_id_list:
        send_file_path = None
        return_file_path = None

        for roots, dirs, files in os.walk(folder_path):
            for file in files:
                if batch_id in file:
                    # Match send file
                    if ('MCO_UTS' in file and not '_SF' in file) or ('New Card Token' in file and not '_SF' in file):
                        send_file_name = file
                        send_file_path = os.path.join(roots, file)

                    # Match return file
                    elif 'unicef_malaysia' in file and 'reply.all' in file:
                        return_file_name = file
                        return_file_path = os.path.join(roots, file)

        # Print send file path if both paths are found for the batch ID
        if send_file_path and return_file_path:
            
            parsed_df = process_file(return_file_path)

            df = map_to_original_file(send_file_path, parsed_df, folder_path, send_file_name, batch_id)

            combined_list.append(df)
            

    combined_df = pd.concat(combined_list, ignore_index=True)
    combined_df.to_excel(os.path.join(folder_path, 'Summary.xlsx'), index=False)
    result = analyze_file(combined_df)
    result.to_excel(os.path.join(folder_path, 'Summary Table.xlsx'), index=False)

    print('Process Completed')


