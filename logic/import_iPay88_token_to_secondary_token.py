import logging
import pandas as pd
import os

"""
THE PURPOSE OF THIS CODE IS TO SIMPLIFY PREPARATION PROCESS FOR TOKEN FILE 
BEFORE UPLOAD TO SALESFORCE USING DATALOADER. THE SIMPLIFICATIONS ARE:

1. DROPPING UNWANTED COLUMN.
2. RENAME THE COLUMN TO MATCH COLUMN REFERENCE IN SALESFORCE.
3. COUNT HOW MANY RECORDS THAT HAVE NOT TOKENIZED.
4. APPEND DATA INTO ONE LIST TO AVOID UPLOADING MULTIPLE TIMES.
5. SAVE THE MASTER LIST IN CSV
"""

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_column(df):
    # TO DELETE UNWANTED COLUMNS.
    
    delete_column_list = [
        'Donor Id','Title','First Name','Last Name','Ethnic','Gender','Street','City','State',
        'Post Code','Country','Home Phone','Work Phone','Mobile Phone','Email','Date of Birth',
        'National Id','Last Pledge Amount','Last Pledge Date','Last Cash Amount','Last Cash Date',
        'Pledge Date','Pledge Start Date','Pledge End Date','Donation Amount',
        'Payment Method','Payment Submethod','Frequency','Cardholder Name',
        'Gift Date','Bank Account Holder Name','Bank Account Number','Bank','DRTV Time','Unique Id',
        'Membership No','Action','Description','Campaign','Campaign Name',
        'DRTV Channel','Creative','Result', 'External Pledge Reference Id']
    
    df = df.drop(columns=delete_column_list)

    return df

def rename_column(df,filename):
    # RENAME COLUMN

    if 'MCO_UTS' in filename:

        df = df.rename(columns={
                                'Truncated CC' : 'sescore__Card_Number_Masked__c',
                                'Expiry Date' : 'sescore__Card_Expiry__c',
                                'Pledge id' : 'Id',
                                'iPay88 Tokenized ID' : 'sescore__Secondary_Token__c'
        })

    return df
     
def analyze_file(df, filename):
    # TO GET TOKENIZED STATUS AND COUNT.
    
    condition = df['Result'] != 'Tokenized OK'

    if condition.any():
        logging.info(f'{condition.sum()} data from {filename} not tokenized!')
    else:
        logging.info(f'All data in {filename} has been tokenized!')

def process_file(folder_path, filename, list):
    # TO PROCESS FILES WITH ALL FUNCTIONS.
    
    file_path = os.path.join(folder_path, filename)
    df = pd.read_excel(file_path)
    analyze_file(df, filename)
    df = delete_column(df)
    df = rename_column(df, filename)
    df['Filename'] = filename # ADD FILE NAME COLUMN FOR TRACKKING
    
    list.append(df)

def import_iPay88_token_to_secondary_token_main(folder_path):
    # OVERALL FLOW

    # CHECK IF PREP FOLDER EXIST OR NOT
    prep_folder_path = os.path.join(folder_path, 'Prep')
    if not os.path.exists(prep_folder_path):
        os.makedirs(prep_folder_path)

    # INITIATE LIST     
    master_list = []

    # ITERATE OVER ALL ITEM IN THE FOLDER AND PROCESS FILE
    for filename in os.listdir(folder_path):
        if 'MCO_UTS' in filename:
            process_file(folder_path, filename, master_list)
        
    # COMBINE AND SAVE LIST TO .CSV
    combined_df = pd.concat(master_list, ignore_index=True)
    combined_df.to_csv(os.path.join(prep_folder_path, f'master_list_{os.path.basename(folder_path)}.csv'), index=False)



