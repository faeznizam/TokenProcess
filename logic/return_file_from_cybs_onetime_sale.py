"""
CODE PURPOSE: 
To generate 2 .xlsx files from .csv file to update data in Salesforce

WORKFLOW: 
1. Extract data from .csv file
2. Split data into 2 data set and label donation and payment
3. Map both data set with original file to get Id
4. Save both data set into .xlsx format. 
"""

# import module
import pandas as pd
import os
from datetime import datetime
import logging
import re
import time


# setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', 
    datefmt="%Y-%m-%d %H:%M:%S")


def extract_batch_id(filename):
    logging.info(f'Extract batch id from {filename}')
    match = re.search(r'\b(\d{8})\b', filename)
    if match:
        extracted_number = match.group(1)
        return extracted_number
    else:
        logging.error(f'Unable to extract batch id from file name. Check file name!')


def extract_data_from_csv(file_path):
    
    """
    What does this function do?
    1. Open .csv file from file_path given.
    2. Parse the data into list and convert to dataframe and split data into 2 column by '='
    3. Return parsed df
    """
    parsed_data = []
    desired_keys = {
        'merchantReferenceCode',
        'decision',
        'ccAuthReply_amount',
        'requestID',
        'ccAuthReply_processorResponse', 
        'ccAuthReply_paymentInsightsInformation_responseInsightsCategory'}

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

    # for consistency in column format, lets fix the column arrangement. 
    format_column = ['merchantReferenceCode', 'decision', 'ccAuthReply_processorResponse', 'ccAuthReply_paymentInsightsInformation_responseInsightsCategory', 'ccAuthReply_amount',  'requestID']
    parsed_df = parsed_df[format_column]

    return parsed_df


def get_current_date():
    logging.info('Generate current date data')
    return datetime.now().strftime('%Y-%m-%d')


def process_extracted_file(df):

    payment_data = df.copy()
    donation_data = df.copy()

    logging.info('Transform data for payment...')
    payment_data['sescore__Status__c'] = payment_data['decision'].apply(lambda x : 'Paid' if x == 'ACCEPT' else 'Payment Failed')
    payment_data['npe01__Payment_Date__c'] = get_current_date()
    payment_data['npe01__Paid__c'] = payment_data['decision'].apply(lambda x : 'TRUE' if x == 'ACCEPT' else 'FALSE')
    payment_data['sescore__Payment_Response_Code__c'] = payment_data['decision'].apply(lambda x : 'CYBS_201_AUTHORIZED' if x == 'ACCEPT' else 'CYBS_CAT_201_01')
    payment_data['sescore__Response_Category__c'] = payment_data['decision'].apply(lambda x : 'Success' if x == 'ACCEPT' else 'Hard Failure')
    payment_data['sescore__Payment_Gateway__c'] = 'CyberSource'

    logging.info('Transform data for donation...')
    donation_data['sescore__External_Donation_Reference_Id__c'] = donation_data['requestID']
    donation_data['sescore__Reason_for_Donation_Failure__c'] = donation_data['ccAuthReply_processorResponse'] + ' ' + donation_data['ccAuthReply_paymentInsightsInformation_responseInsightsCategory']
    donation_data['sescore__Reason_for_Donation_Failure__c'] = donation_data['sescore__Reason_for_Donation_Failure__c'].str.replace('00', '', regex=False)

    logging.info('Reformat columns')
    delete_extracted_df_coumns = ['decision', 'ccAuthReply_processorResponse', 'ccAuthReply_paymentInsightsInformation_responseInsightsCategory', 'ccAuthReply_amount',  'requestID']
    payment_data.drop(columns=delete_extracted_df_coumns, inplace=True)
    donation_data.drop(columns=delete_extracted_df_coumns, inplace=True)

    payment_column_order = [
        'BatchID', 'merchantReferenceCode', 'sescore__Status__c', 'npe01__Payment_Date__c',	
        'npe01__Paid__c', 'sescore__Payment_Response_Code__c',	'sescore__Response_Category__c',
        'sescore__Payment_Gateway__c']

    payment_data = payment_data[payment_column_order]

    payment_data.rename(columns={'merchantReferenceCode' : 'Id'}, inplace=True)

    donation_column_order = [
        'BatchID',	'merchantReferenceCode', 'sescore__External_Donation_Reference_Id__c',
        'sescore__Reason_for_Donation_Failure__c']

    donation_data = donation_data[donation_column_order]

    donation_data.rename(columns={'merchantReferenceCode' : 'Id'}, inplace=True)

    return df, payment_data, donation_data
    

def save_file(extracted_data, payment_data, donation_data, folder_path):
    logging.info('Saving files...')

    data_map = {
        'extracted_data_from_reply.all_file.xlsx': extracted_data,
        'to_map_with_query_file_payment.xlsx': payment_data,
        'to_map_with_query_file_donation.xlsx': donation_data
    }

    for filename, df in data_map.items():
        try:
            file_path = os.path.join(folder_path, filename)
            df.to_excel(file_path, index=False)
            logging.info(f"{filename} has been created.")
        except Exception as e:
            logging.error(f"Failed to save {filename}: {e}")

    logging.info("All files saved successfully.")


def main():
    logging.info('Process Starts!')
    start_time = time.time() 

    folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\1 Project\Setup one time file to Cybs Token SW and UTS'
    folder_directory = os.listdir(folder_path)

    payment_data_list = []
    donation_data_list = []
    extracted_data_list = []

    for file in folder_directory:
        if 'unicef_malaysia' in file and 'reply.all' in file:
            file_path = os.path.join(folder_path, file)

            batch_id = extract_batch_id(file)

            logging.info(f"Extracting data from {file}")
            extracted_df = extract_data_from_csv(file_path)
            extracted_df['BatchID'] = batch_id


            extracted_df, payment_data, donation_data = process_extracted_file(extracted_df)

            logging.info('Append data to list')
            extracted_data_list.append(extracted_df)
            payment_data_list.append(payment_data)
            donation_data_list.append(donation_data)

    if extracted_data_list:
        logging.info('Combine main list')
        extracted_data = pd.concat(extracted_data_list, ignore_index=True)

    if payment_data_list:
        logging.info('Combine payment list')
        payment_data = pd.concat(payment_data_list, ignore_index=True)

    if donation_data_list:
        logging.info('Combine donation list')
        donation_data = pd.concat(donation_data_list, ignore_index=True)

    logging.info('Read one time query file')
    query_file = pd.read_excel(os.path.join(folder_path, 'OT Query.xlsx'), dtype={'sescore__Contact_Mobile_Phone__c': str})

    
    query_column = ['Id', 'npe01__Opportunity__r.Id']
    query_file = query_file[query_column]

    donation_merge = donation_data.merge(
        query_file,
        left_on='Id',
        right_on='Id',
        how='left'
    )

    donation_merge['Id'] = donation_merge['npe01__Opportunity__r.Id']
    donation_merge.drop(columns='npe01__Opportunity__r.Id', inplace=True)

    save_file(extracted_data, payment_data, donation_merge, folder_path)

    elapsed_time = time.time() - start_time
    logging.info(f'Process Completed. Elapsed time : {elapsed_time:.2f} seconds.')
            


if __name__ == '__main__':
    main()