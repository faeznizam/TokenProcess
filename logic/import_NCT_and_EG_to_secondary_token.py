import pandas as pd
import os
import logging

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

    if 'VSMC_SF' in filename or 'VSMC_redrop_SF' in filename:
        df = df.rename(columns={
        'Truncated CC' : 'sescore__Card_Number_Masked__c',
        'Expiry Date' : 'sescore__Card_Expiry__c',
        'External Pledge Reference Id' : 'sescore__External_Pledge_Reference_Unique_Id__c', 
        'iPay88 Tokenized ID' : 'sescore__Secondary_Token__c'
        })

    elif 'Token_SF' in filename:
        df = df.rename(columns={
        'Truncated CC' : 'sescore__Card_Number_Masked__c',
        'Expiry Date' : 'sescore__Card_Expiry__c',
        'External Pledge Reference Id' : 'sescore__Pledge_Id__c',
        'iPay88 Tokenized ID' : 'sescore__Secondary_Token__c'
        })

    return df

def rename_file(filename):
    # USING THE SAME FILE NAME FOR UPDATED FILE.
    
    return f'{filename[:-5]}.csv'

def process_file(folder_path, filename):
    # TO PROCESS FILES WITH ALL FUNCTIONS.
    
    file_path = os.path.join(folder_path, filename)
    df = pd.read_excel(file_path)
    df = delete_column(df, filename)
    df = rename_column(df, filename)
    new_file_name = rename_file(filename)
    df.to_csv(os.path.join(folder_path, new_file_name), index=False)

    logging.info('Process complete')

def import_NCT_EG_to_secondary_token_main(folder_path):
    # OVERALL FLOW
    
    for filename in os.listdir(folder_path):
        if 'VSMC_SF' in filename or 'VSMC_redrop_SF' in filename:
            process_file(folder_path, filename)
        elif 'Token_SF' in filename:
            process_file(folder_path, filename)

