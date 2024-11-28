# import module
from .helper_for_send_file import process_data_table, convert_to_expiry_format
from .helper_for_send_file2 import batch_counter, get_current_date, main_template, file_creation

import os
import pandas as pd


def check_file_has_been_processed(folder_path):
    """ To check if file has been processed or not by checking prefix in the file name.
        It will return True or False """
    for file in os.listdir(folder_path):
        if 'To_CYB' in file:
            return True
    return False





def send_file_process_flow(folder_path):
    """
    What does this function do?
    1. Check if file has been process and if required file exist in the folder.
    2. Run process_data_table function to process the file.
    3. Get batch number.
    4. Get current date.
    5. Create template format
    6. Create .csv file
    """

    is_file_has_been_processed = check_file_has_been_processed(folder_path)
    

    if is_file_has_been_processed:
        return '\nFile already processed, check the folder!'
    
    
    
    
    for file in os.listdir(folder_path):
        if file.startswith('MCO_UTS'):
            batch_number = batch_counter(folder_path) # get batch number
            
            current_date = get_current_date()

            df, original_df = process_data_table(folder_path, file, 'Payment Submethod', 'Expiry Date')

            header_data, field_names, footer_data, empty_row = main_template(folder_path, df, batch_number) # reformat file

            file_creation(header_data,field_names, empty_row, footer_data, df, folder_path, batch_number) # create file with new format

            original_df.to_excel(os.path.join(folder_path, f'{file[:-5]}_{current_date}{batch_number}.xlsx'), index=False) # save original file with batch number in name
            
            print("Process completed. Check folder for files with prefix 'To_CYB'.")

        elif file.startswith('New Card Token'):
            batch_number = batch_counter(folder_path) # get batch number

            current_date = get_current_date()

            df2, original_df2 = process_data_table(folder_path, file, 'Payment Submethod (Mastercard/Visa/Amex)', 'Expiry Date MM/YY format')
            
            header_data, field_names, footer_data, empty_row = main_template(folder_path, df2, batch_number) # reformat file

            file_creation(header_data,field_names, empty_row, footer_data, df2, folder_path, batch_number) # create file with new format

            original_df2.to_excel(os.path.join(folder_path, f'{file[:-5]}_{current_date}{batch_number}.xlsx'), index=False) # save original file with batch number in name
            
            print("Process completed. Check folder for files with prefix 'To_CYB'.")

    
"""
if __name__ == '__main__':
    send_file_main()

"""