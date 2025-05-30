"""
CODE PURPOSE: 
Create file that combine EG file, New Card Token file and query file. 
"""
# import module
from datetime import datetime
import pandas as pd
import os
import logging
import time


# logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def delete_column(df):
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

    # to avoid repeatition, use common mapping.
    common_mapping = {
        'Truncated CC': 'sescore__Card_Number_Masked__c',
        'Expiry Date': 'sescore__Card_Expiry__c',
        'iPay88 Tokenized ID': 'sescore__Secondary_Token__c',
    }

    # mapping based on file name
    mapping_by_file = {
        'VSMC_SF': {'External Pledge Reference Id': 'sescore__External_Pledge_Reference_Unique_Id__c',},
        'VSMC_redrop_SF': {'External Pledge Reference Id': 'sescore__External_Pledge_Reference_Unique_Id__c',},
        'Token_SF': {'External Pledge Reference Id': 'sescore__Pledge_Id__c',}
    }

    # Determine which file pattern is in the filename
    for key, specific_mapping in mapping_by_file.items():
        if key in filename:
            # Merge the specific and common mappings
            column_mapping = {**common_mapping, **specific_mapping}
            return df.rename(columns=column_mapping)

    return df


def process_file(folder_path, file):
    logging.info(f'Read {file}')
    file_path = os.path.join(folder_path, file)

    df = pd.read_excel(file_path)

    logging.info(f'Remove unrelated column in {file} ')
    df = delete_column(df)
    
    logging.info(f'Reorder {file} column')
    column_order = [
        'Truncated CC', 'Expiry Date', 
        'iPay88 Tokenized ID', 
        'External Pledge Reference Id']
    
    df = df[column_order]

    logging.info(f'Rename {file} column based on file name')
    df = rename_column(df, file)

    return df


def main():

    logging.info('Process Starts!')
    start_time = time.time() 

    folder_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\New Card Token & EG (to submit for iPay88 token and import into secondary token)\2025\May\270525\Test'

    directory = os.listdir(folder_path)

    for file in directory:
        if 'VSMC_SF.xlsx' in file or 'VSMC_redrop_SF' in file:

            eg_file = process_file(folder_path, file)
            eg_file['Source'] = file

        elif 'Token_SF.xlsx' in file:

            new_card = process_file(folder_path, file)
            new_card['Source'] = file

        elif 'query file.xlsx' in file:

            file_path = os.path.join(folder_path, file)        

            query_file = pd.read_excel(file_path)

    logging.info('Merge new card and eg file with query file')
    updated_new_card = new_card.merge(
        query_file[['Id', 'sescore__External_Pledge_Reference_Unique_Id__c', 'sescore__Pledge_Id__c']],
        left_on='sescore__Pledge_Id__c',
        right_on= 'sescore__Pledge_Id__c',
        how='left')

    updated_eg = eg_file.merge(
        query_file[['Id', 'sescore__External_Pledge_Reference_Unique_Id__c', 'sescore__Pledge_Id__c']],
        left_on='sescore__External_Pledge_Reference_Unique_Id__c',
        right_on= 'sescore__External_Pledge_Reference_Unique_Id__c',
        how='left')

    logging.info('Reorder column for new card and eg file')
    column_order = [
        'Id', 'sescore__Card_Number_Masked__c', 'sescore__Card_Expiry__c', 'sescore__Secondary_Token__c',
        'sescore__Pledge_Id__c',  'sescore__External_Pledge_Reference_Unique_Id__c', 'Source']

    updated_new_card = updated_new_card[column_order]
    updated_eg = updated_eg[column_order]

    logging.info('Combine updated eg and new card file')
    combine_df = pd.concat([updated_eg, updated_new_card], ignore_index=True)

    logging.info('Rename Id column to sescore__Recurring_Donation__c ')
    combine_df = combine_df.rename(columns={'Id' : 'sescore__Recurring_Donation__c'})

    logging.info('Add save mandate, preferred change date, and status column')
    combine_df['sescore__Save_Mandate__c'] = 'TRUE'
    current_date = datetime.today().strftime('%Y-%m-%d')
    combine_df['sescore__Preferred_Change_Date__c'] = current_date
    combine_df['sescore__Status__c'] = 'New'

    logging.info('Reorder column')
    column_order2 = [
        'sescore__Recurring_Donation__c', 'sescore__Card_Number_Masked__c', 'sescore__Card_Expiry__c', 
        'sescore__Save_Mandate__c', 'sescore__Preferred_Change_Date__c', 'sescore__Status__c',
        'sescore__Secondary_Token__c',
        'sescore__Pledge_Id__c',  'sescore__External_Pledge_Reference_Unique_Id__c', 'Source']
    
    combine_df = combine_df[column_order2]

    logging.info('Rename masked card number, card expiry, and secondary token')
    rename_map = {
        'sescore__Card_Number_Masked__c': 'sescore__New_Card_Number_Masked__c',
        'sescore__Card_Expiry__c': 'sescore__New_Card_Expiry__c',
        'sescore__Secondary_Token__c': 'sescore__New_Secondary_Token__c'
    }
    combine_df.rename(columns=rename_map, inplace=True)
    
    logging.info(f'Save {combine_file_name} in {folder_path}')
    combine_file_name = 'To be updated using salesforce inspector.xlsx'
    combine_df.to_excel(os.path.join(folder_path, combine_file_name), index=False)

    elapsed_time = time.time() - start_time
    logging.info(f'Process Completed. Elapsed time : {elapsed_time:.2f} seconds.')
    
    
if __name__ == "__main__":
    main()