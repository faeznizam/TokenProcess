"""
CODE PURPOSE: 
The code should convert sales file format to EBC format.

"""
# Import module
import os
import logging
from .helper_send_file_to_cybs import process_data_table
from .helper_send_file_to_cybs2 import batch_counter, get_current_date, main_template, file_creation

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

def check_final_file_in_folder(folder_path):
    # Check if the file has already been processed by looking for specific prefixes in file names.
    return any('To_CYB' in file for file in os.listdir(folder_path))


def process_file(folder_path, file, payment_column, expiry_column):
    # Processes the given file, reformats it, and saves the original and formatted files.

    # create batch number
    batch_number = batch_counter(folder_path)
    current_date = get_current_date()

    df, original_df = process_data_table(folder_path, file, payment_column, expiry_column)
    header_data, field_names, footer_data, empty_row = main_template(folder_path, df, batch_number)
    
    # Create the formatted file
    file_creation(header_data, field_names, empty_row, footer_data, df, folder_path, batch_number)

    # New File Name
    new_filename = f'{file[:-5]}_{current_date}{batch_number}.xlsx'

    # Save the original file with a batch number
    original_filename = os.path.join(folder_path, new_filename)
    original_df.to_excel(original_filename, index=False)

    logging.info(f"Process completed. File {new_filename} has been created.")

def to_send_files_to_cybs_main(folder_path):
   
    if check_final_file_in_folder(folder_path):
        return logging.info('\nFile already processed, check the folder!')

    file_configs = [
        ('MCO_UTS', 'Payment Submethod', 'Expiry Date'),
        ('New Card Token', 'Payment Submethod (Mastercard/Visa/Amex)', 'Expiry Date MM/YY format')
    ]

    for file in os.listdir(folder_path):
        for prefix, payment_column, expiry_column in file_configs:
            if file.startswith(prefix):
                process_file(folder_path, file, payment_column, expiry_column)

    
