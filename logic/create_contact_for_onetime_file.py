from datetime import datetime
import pandas as pd
import logging
import shutil
import re
import os

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
    
    )

def check_for_existing_final_file(new_folder_path):
    for file in os.listdir(new_folder_path):
        if file.endswith('to create contact.xlsx'):
            logging.info(f'{file} already exists. Check the folder!')
            return True
    return False

def create_folder(folder_path):
    folder_name = "To create contact"
    new_folder_path = os.path.join(folder_path, folder_name)

    if os.path.exists(new_folder_path):
        logging.info(f"Folder '{folder_name}' already exists. Checking for existing file... ")

        if check_for_existing_final_file(new_folder_path):
            logging.info("Existing 'to create contact.xlsx' file found. Process Stop!")
            return None
        else:
            logging.info('No file in the folder, copying the file from main folder.')
            copy_files_into_folder(folder_path, new_folder_path, folder_name)
            return new_folder_path

    else:
        os.mkdir(new_folder_path)
        logging.info(f"Folder '{folder_name}' successfully created!")

        copy_files_into_folder(folder_path, new_folder_path, folder_name)

        return new_folder_path

    


def copy_files_into_folder(folder_path, new_folder_path, folder_name):

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            shutil.copy(file_path, new_folder_path)
            logging.info(f"{file_name} has been copied to '{folder_name}' folder.")
            


def get_current_date():
    return datetime.now().strftime('%y%m%d')


def convert_date_format_to_expiry_format(x):

    pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"

    if re.match(pattern, x):
        data = datetime.strptime(x, "%Y-%m-%d %H:%M:%S" )
        return data.strftime("%m/%y")
    else:
        return x


def process_file(file_path):

    df = pd.read_excel(file_path, dtype={
                                        'Donor Id' : str,
                                        'Post Code' : str, 
                                        'Card Number' : str, 
                                        'Expiry Date' : str
                                                })
    
    if 'DRTV Channel' not in df.columns:
        df['DRTV Channel'] = ''

    if 'Creative' not in df.columns:
        df['Creative'] = ''

    df['Donor Id'].fillna("", inplace=True)

    df['Truncated CC'] = df['Card Number'].apply(lambda x : f'{x[:2]}********{x[-4:]}')

    df['Expiry Date'] = df['Expiry Date'].apply(convert_date_format_to_expiry_format)

    # drop card number column
    df.drop(columns=['Card Number'], inplace=True)

    # add column
    df['External Pledge Reference Id'] = ''

    # rearrange column
    desired_order = [
        'Donor Id', 'Title', 'First Name', 'Last Name', 'Ethnic', 'Gender', 'Street', 'City', 'State', 
        'Post Code', 'Country', 'Home Phone', 'Work Phone', 'Mobile Phone', 'Email', 'Date of Birth', 
        'National Id', 'Last Pledge Amount', 'Last Pledge Date', 'Last Cash Amount',  'Last Cash Date', 
        'Pledge id', 'Pledge Date', 'Pledge Start Date', 'Pledge End Date', 'Donation Amount', 
        'Payment Method', 'Payment Submethod', 'Truncated CC', 'Expiry Date', 'Frequency', 
        'Cardholder Name', 'Gift Date','Bank Account Holder Name','Bank Account Number','Bank',
        'DRTV Time','Unique Id', 'Membership No','Action','Description','Campaign', 'Campaign Name',
        'External Pledge Reference Id','IPay88 Tokenized ID', 'DRTV Channel', 'Creative']
    
    df = df[desired_order]

    return df


def create_contact_for_onetime_file_main(folder_path):

    new_folder_path = create_folder(folder_path)

    if not new_folder_path:
        logging.info(f'Process stopped because final file already exists. Check the folder! : {folder_path}')
        return 
   

    
    uts_list = []
    utsbank_list = []


    for file in os.listdir(new_folder_path):
        if 'MCO_UTS_' in file and '_OT' in file and '.xlsx' in file:
            file_path = os.path.join(new_folder_path, file)
            df = process_file(file_path)
            uts_list.append(df)
        elif 'MCO_UTSBANK' in file and '_OT' in file and '.xlsx' in file:
            file_path2 = os.path.join(new_folder_path, file)
            df2 = process_file(file_path2)
            utsbank_list.append(df2)


    uts_df = pd.DataFrame()  
    utsbank_df = pd.DataFrame()
    
    # make sure list is not empty before concatenate
    if uts_list:
        uts_df = pd.concat(uts_list, ignore_index=True)
        uts_df_file_name = f'MCO_UTS_{get_current_date()} - to create contact.xlsx'
        uts_df.to_excel(os.path.join(new_folder_path, uts_df_file_name ), index=False)
        logging.info(f'{uts_df_file_name} file has been created!')


    if utsbank_list:
        utsbank_df = pd.concat(utsbank_list, ignore_index=True)
        utsbank_df_file_name = f'MCO_UTSBANK_Enrollment_{get_current_date()} - to create contact.xlsx'
        utsbank_df.to_excel(os.path.join(new_folder_path, utsbank_df_file_name ), index=False)
        logging.info(f'{utsbank_df_file_name} file has been created!')
        

    logging.info('Process Completed. Please drop the files into SFTP to create contact')
    
"""
if __name__ == "__main__":
    main()
"""