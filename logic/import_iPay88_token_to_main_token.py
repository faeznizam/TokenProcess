import logging
import pandas as pd
import os

"""
THE PURPOSE OF THIS CODE IS TO SIMPLIFY PREPARATION PROCESS FOR TOKEN FILE 
BEFORE UPLOAD TO SALESFORCE USING DATALOADER. THE SIMPLIFICATIONS ARE:

1. DROPPING UNWANTED COLUMN.
2. RENAME THE COLUMN TO MATCH COLUMN REFERENCE IN SALESFORCE.
3. COUNT HOW MANY RECORDS THAT HAVE NOT TOKENIZED.
4. SAVE FILE AS .csv TO ELIMINATE MANUALLY CONVERT THE FILE.
"""

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_column(df, filename):
    # TO DELETE UNWANTED COLUMNS.
    
    delete_column_list = [
        'Donor Id','Title','First Name','Last Name','Ethnic','Gender','Street','City','State',
        'Post Code','Country','Home Phone','Work Phone','Mobile Phone','Email','Date of Birth',
        'National Id','Last Pledge Amount','Last Pledge Date','Last Cash Amount','Last Cash Date',
        'Pledge id','Pledge Date','Pledge Start Date','Pledge End Date','Donation Amount',
        'Payment Method','Payment Submethod','Frequency','Cardholder Name',
        'Gift Date','Bank Account Holder Name','Bank Account Number','Bank','DRTV Time','Unique Id',
        'Membership No','Action','Description','Campaign','Campaign Name',
        'DRTV Channel','Creative','Result']
    
    df = df.drop(columns=delete_column_list)

    return df

def rename_column(df, filename):
    # RENAME COLUMN BASED ON FILE NAME.

    if 'VSMC_SF' in filename:
        df = df.rename(columns={
        'Truncated CC' : 'sescore__Card_Number_Masked__c',
        'Expiry Date' : 'sescore__Card_Expiry__c',
        'External Pledge Reference Id' : 'sescore__External_Pledge_Reference_Id__c',
        'iPay88 Tokenized ID' : 'sescore__Card_Token__c'
        })

    elif 'Token_SF' in filename:
        df = df.rename(columns={
        'Truncated CC' : 'sescore__Card_Number_Masked__c',
        'Expiry Date' : 'sescore__Card_Expiry__c',
        'External Pledge Reference Id' : 'sescore__Pledge_Id__c',
        'iPay88 Tokenized ID' : 'sescore__Card_Token__c'
        })

    return df
     
def rename_file(filename):
    # USING THE SAME FILE NAME FOR UPDATED FILE.
    
    return f'{filename[:-5]}.csv'

def analyze_file(df, filename):
    # TO GET TOKENIZED STATUS AND COUNT.
    
    condition = df['Result'] != 'Tokenized OK'

    if condition.any():
        logging.info(f'{condition.sum()} data from {filename} not tokenized!')
    else:
        logging.info(f'All data in {filename} has been tokenized!')

def process_file(folder_path, filename):
    # TO PROCESS FILES WITH ALL FUNCTIONS.
    
    file_path = os.path.join(folder_path, filename)
    df = pd.read_excel(file_path)
    analyze_file(df, filename)
    df = delete_column(df, filename)
    df = rename_column(df, filename)
    new_file_name = rename_file(filename)
    df.to_csv(os.path.join(folder_path, new_file_name), index=False)

    logging.info('Process complete')

def import_iPay88_token_to_main_token_main(folder_path):
    # OVERALL FLOW
    
    for filename in os.listdir(folder_path):
        if 'VSMC_SF' in filename:
            process_file(folder_path, filename)
        elif 'Token_SF' in filename:
            process_file(folder_path, filename)
    





