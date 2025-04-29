import pandas as pd
import os
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
    
    )

def extract_data_from_csv(file_path):
    """
    What does this function do?
    1. Open .csv file from file_path given.
    2. Parse the data into list and convert to dataframe and split data into 2 column by '='
    3. Return parsed df
    """
    
    desired_keys = {
        'merchantReferenceCode',
        'decision',
        'ccAuthReply_amount',
        'requestID',
        'ccAuthReply_processorResponse', 
        'ccAuthReply_paymentInsightsInformation_responseInsightsCategory'

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

    # for consistency in column format, lets fix the column arrangement. 
    format_column = ['merchantReferenceCode', 'decision', 'ccAuthReply_processorResponse', 'ccAuthReply_paymentInsightsInformation_responseInsightsCategory', 'ccAuthReply_amount',  'requestID']
    parsed_df = parsed_df[format_column]

    return parsed_df

def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

def return_file_from_cybs_onetime_main(folder_path):



    #folder_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\CYBS Token - OT Files\2025\Mar\110325'

    payment_data_list = []
    donation_data_list = []
    extracted_data_list = []

    for file in os.listdir(folder_path):
        if 'unicef_malaysia' in file and 'reply.all' in file:

            file_path = os.path.join(folder_path, file)

            batch_id = file[-22:-14]
            
            logging.info(f"Extracting data from {file}...")
            extracted_df = extract_data_from_csv(file_path)
            extracted_df['BatchID'] = batch_id

            payment_data = extracted_df.copy()
            donation_data = extracted_df.copy()
            
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

    logging.info('Saving files...')

    extracted_data_file_name = 'extracted_data_from_reply.all_file.xlsx'
    extracted_data.to_excel(os.path.join(folder_path, extracted_data_file_name ), index=False)
    logging.info(f"{extracted_data_file_name} file has been created")

    payment_data_file_name = 'to_map_with_query_file_payment.xlsx'
    payment_data.to_excel(os.path.join(folder_path, payment_data_file_name), index=False)
    logging.info(f"{payment_data_file_name} file has been created")

    donation_data_file_name = 'to_map_with_query_file_donation.xlsx'
    donation_data.to_excel(os.path.join(folder_path, donation_data_file_name), index=False)
    logging.info(f"{donation_data_file_name} has been created")

    logging.info("Process completed.")

"""
if __name__ == '__main__':
    main()
"""