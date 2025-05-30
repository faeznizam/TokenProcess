"""
CODE PURPOSE: 
To convert sales file into EBC format for tokenization.

"""
# import module 
from datetime import datetime
import pandas as pd
import logging
import os
import time

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

def batch_counter(folder_path):
    """
    1. Check if text file name batch_count exist. If not create one.
    2. If file already exist, check date = current date.
    3. If not replace with current date and reset count to 1.
    4. If file just created, start count with 1. 
    """
    file_path = os.path.join(folder_path, 'batch_count.txt')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if os.path.exists(file_path):
        with open(file_path, 'r+') as file:
            data = file.readlines()
            last_date, last_count = data[0].strip().split(',')
            
            if last_date == current_date:
                new_count = int(last_count) + 1
            else:
                new_count = 1
            
            file.seek(0)
            file.write(f"{current_date},{new_count:02d}")
            file.truncate()
    else:
        with open(file_path, 'w') as file:
            new_count = 1
            file.write(f"{current_date},{new_count:02d}")
    
    return f"{new_count:02d}"

# get current date with different format
def get_current_date():
    return datetime.now().strftime('%y%m%d')

def create_dataframe(data, columns=None):
    return pd.DataFrame([data], columns=columns)

def new_file_name(folder_path, batch_number):
    return f'To_CYB_{get_current_date()}{batch_number}.csv'

def get_creation_date():
    return datetime.now().strftime('%Y-%m-%d')

# create template using dictionary and list and return all variable
def main_template(folder_path,df,batch_number):

    # Data Definitions
    header_data = {
        'merchant_id': 'merchantID=unicef_malaysia',
        'batch_id': f'batchID={get_current_date()}{batch_number}',
        'creation_date': f'creationDate={get_creation_date()}',
        'record_count': f'recordCount={len(df)}',
        'template': 'Template=custom',
        'reference': 'reference=MY',
        'status_email': 'statusEmail=processing-mly@unicef.org',
        'target_api': 'targetAPIVersion=1.224'
    }

    empty_row = []

    field_names = [
        'merchantReferenceCode', 	
        'recurringSubscriptionInfo_subscriptionID',
        'ccAuthService_run',
        'ccCaptureService_run',
        'purchaseTotals_currency',
        'purchaseTotals_grandTotalAmount',
        'subsequentAuth'
        
    ]

    footer_data = ['END', f"SUM={round(df['purchaseTotals_grandTotalAmount'].sum(), 2)}"]

    return header_data, field_names, footer_data, empty_row

# create file based on template
def file_creation(header_data, field_names, empty_row, footer_data, df, folder_path, batch_number):

    name = new_file_name(folder_path, batch_number)

    save_file_path = os.path.join(folder_path, name)

    # Create DataFrames
    first_row_data = create_dataframe(list(header_data.values()))
    second_row_data = create_dataframe(empty_row)
    third_row_data = create_dataframe(field_names)
    data_rows = df
    last_row_data = create_dataframe(footer_data, columns=[0, 1])

    # Write to CSV
    first_row_data.to_csv(save_file_path, index=False, header=False, mode='w')  # Write header data
    second_row_data.to_csv(save_file_path, index=False, header=False, mode='a')  # Append field names
    third_row_data.to_csv(save_file_path, index=False, header=False, mode='a')  # Append field names
    data_rows.to_csv(save_file_path, index=False, header=False, mode='a')       # Append main data rows
    last_row_data.to_csv(save_file_path, index=False, header=False, mode='a')   # Append footer data


def create_sales_template(df):
    return pd.DataFrame({
        'merchantReferenceCode': df['Id'],
        'recurringSubscriptionInfo_subscriptionID': df['sescore__Card_Token__c'],
        'ccAuthService_run': 'true',
        'ccCaptureService_run': 'true',
        'purchaseTotals_currency': 'MYR',
        'purchaseTotals_grandTotalAmount': df['npe01__Payment_Amount__c'],
        'subsequentAuth': 'true'
    })


def process_file(folder_path, file):
    # Processes the given file, reformats it, and saves the original and formatted files.

    logging.info('Create batch number and get current date')
    batch_number = batch_counter(folder_path)
    current_date = get_current_date()

    logging.info('Read file and create sales table')
    df, original_df = process_data_table(folder_path, file)

    logging.info('Create EBC template for sales table')
    header_data, field_names, footer_data, empty_row = main_template(folder_path, df, batch_number)
    
    logging.info('Merge template and sales table')
    file_creation(header_data, field_names, empty_row, footer_data, df, folder_path, batch_number)

    logging.info('Generate new file name based on date and batch number')
    new_filename = f'{file[:-5]}_{current_date}{batch_number}.xlsx'

    logging.info(f'Saving {new_file_name} in {folder_path}')
    original_filename = os.path.join(folder_path, new_filename)
    original_df.to_excel(original_filename, index=False)

    

def process_data_table(folder_path, file):
    
    file_path = os.path.join(folder_path, file)

    df = pd.read_excel(file_path) 
    new_df = create_sales_template(df)

    return new_df, df


def main():
    logging.info('Process Starts!')
    start_time = time.time()

    folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\One Time Task\Setup one time file to Cybs Token SW and UTS'
    
    file_directory = os.listdir(folder_path)

    for file in file_directory:
        if 'OT Query' in file:
            process_file(folder_path, file)

    elapsed_time = time.time - start_time
    logging.info(f'Process Completed. Elapsed time : {elapsed_time:.2f} seconds.')

if __name__ == '__main__':
    main()