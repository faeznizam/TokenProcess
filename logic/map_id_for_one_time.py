import pandas as pd
import logging
import os

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
    
    )

def map_id_for_one_time(folder_path):

    #folder_path = r'C:\Users\mfmohammad\UNICEF\MYS-CloudShare - PFP - Business Intelligence\Token\CYBS Token - OT Files\2025\Mar\120325'

    payment_file = pd.read_excel(os.path.join(folder_path, 'to_map_with_query_file_payment.xlsx'), dtype={'merchantReferenceCode': str})
    donation_file = pd.read_excel(os.path.join(folder_path, 'to_map_with_query_file_donation.xlsx'), dtype={'merchantReferenceCode': str})
    query_file = pd.read_excel(os.path.join(folder_path, 'ID from SF.xlsx'), dtype={'sescore__Contact_Mobile_Phone__c': str})

    query_file.drop(
        columns=[
            'npe01__Opportunity__r', 
            'sescore__Mandate__r', 
            'MCO_Campaign_Name__c', 
            'sescore__Secondary_Token__c', 
            'sescore__Donation_Type__c', 
            'sescore__Mandate__r.Name'
            ], 
        inplace=True
        )


    payment_merge = payment_file.merge(
        query_file, 
        left_on='merchantReferenceCode', 
        right_on='sescore__Contact_Mobile_Phone__c', 
        how='left')

    donation_merge = donation_file.merge(
        query_file, 
        left_on='merchantReferenceCode', 
        right_on='sescore__Contact_Mobile_Phone__c', 
        how='left'
    )

    # merge
    payment_merge.drop(columns=['npe01__Opportunity__r.Id', 'sescore__Contact_Mobile_Phone__c'], inplace=True)
    donation_merge.drop(columns=['Id', 'sescore__Contact_Mobile_Phone__c'], inplace=True)
    donation_merge = donation_merge.rename(columns={'npe01__Opportunity__r.Id': 'Id'})

    # create and save final file

    payment_final_file_name = 'to_update_payment_details.xlsx'
    payment_merge.to_excel(os.path.join(folder_path, payment_final_file_name ), index=False)
    logging.info(f'{payment_final_file_name} file has been created.')

    donation_final_file_name = 'to_update_donation_details.xlsx'
    donation_merge.to_excel(os.path.join(folder_path, donation_final_file_name ), index=False)
    logging.info(f'{donation_final_file_name} file has been created.')


    logging.info('Process complete.')