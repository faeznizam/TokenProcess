import os
import pandas as pd
import re
import datetime
from datetime import datetime
import csv



def create_template_table():
    table_template = {
        'ccAuthService_run' : [], 	
        'ccCaptureService_run' : [],
        'purchaseTotals_currency' : [],
        'merchantReferenceCode' : [],
        'purchaseTotals_grandTotalAmount' : [],
        'billTo_firstName' : [],
        'billTo_lastName' : [],
        'billTo_street1' : [],
        'billTo_city' : [],
        'billTo_postalCode' : [],
        'billTo_country' : [],
        'billTo_email' : [],
        'card_accountNumber' : [],
        'card_expirationMonth' : [],
        'card_expirationYear' : [],
        'card_cardtype' : [] 					
        }
    
    return pd.DataFrame(table_template)

def copy_data_into_table(new_df, df):

    new_df['billTo_firstName'] = df['First Name']
    new_df['ccAuthService_run'] = 'true'
    new_df['ccCaptureService_run'] = 'true'
    new_df['purchaseTotals_currency'] = 'MYR'
    new_df['merchantReferenceCode'] = df['Mobile Phone']
    new_df['purchaseTotals_grandTotalAmount'] = df['Donation Amount']
    new_df['billTo_lastName'] = df['Last Name']
    new_df['billTo_street1'] = df['Street']
    new_df['billTo_city'] = 'Malaysia'
    new_df['billTo_postalCode'] = df['Post Code']
    new_df['billTo_country'] = 'MY'
    new_df['billTo_email'] = df['Email']
    new_df['card_accountNumber'] = df['Card Number']
    new_df['card_expirationMonth'] = df['Expiry Month']
    new_df['card_expirationYear'] = df['Expiry Year']
    new_df['card_cardtype'] = df['Payment Submethod']

    return new_df

def process_street_data(df):
    # to limit 40 character only for this column
    df['Street'] = df['Street'].apply(lambda x : x[:40] if isinstance(x,str) else x)

    return df

def create_expiry_month(df, expiry_column):
    # MC0 - Expiry Date
    # New Card Token - Expiry Date MM/YY format
    # Define regex patterns for extracting the month part
    pattern1 = r'\d{4}-(\d{2})-\d{2} \d{2}:\d{2}:\d{2}'  # Extracts the month from DD-MM-YYYY
    pattern2 = r'^(0[1-9]|1[0-2])/\d{2}$'  # Matches MM/YY
    
    # Use str.extract() to get the month for DD-MM-YYYY format 
    df['Expiry Month'] = df[expiry_column].str.extract(pattern1, expand=False)
    
    # Fill the missing values for the MM/YY format using str.extract()
    df['Expiry Month'] = df['Expiry Month'].fillna(
        df[expiry_column].str.extract(r'^(0[1-9]|1[0-2])', expand=False)
    )
    
    # Set 'Invalid' for non-matching rows
    df['Expiry Month'] = df['Expiry Month'].fillna('Invalid')

    return df

def create_expiry_year(df, expiry_column):
    # Define regex patterns for extracting the year
    pattern1 = r'^(\d{4})-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'  # Extracts the year from DD-MM-YYYY
    pattern2 = r'^(0[1-9]|1[0-2])/(\d{2})$'  # Extracts the year from MM/YY

    # Extract the year for DD-MM-YYYY format
    df['Expiry Year'] = df[expiry_column].str.extract(pattern1, expand=False)

    # Extract and convert the year for MM/YY format
    df['Expiry Year'] = df['Expiry Year'].fillna(
        df[expiry_column].str.extract(pattern2, expand=False)[1].apply(lambda x: '20' + x if pd.notna(x) else x)
    )

    # Set 'Invalid' for non-matching rows
    df['Expiry Year'] = df['Expiry Year'].fillna('Invalid')
    
    return df

def convert_payment_submethod(df, payment_submethod_column):
    # to convert data, visa = 001, mastercard = 002, amex = 003
    # MCO - 'Payment Submethod'
    # NEW CARD TOKEN - 'Payment Submethod (Mastercard/Visa/Amex)'

    df[payment_submethod_column] = df[payment_submethod_column].str.lower()

    df[payment_submethod_column].replace('mastercard', '002', inplace=True)
    df[payment_submethod_column].replace('master', '002', inplace=True)
    df[payment_submethod_column].replace('visa', '001', inplace=True)
    df[payment_submethod_column].replace('amex', '003', inplace=True)
     
    return df

def drop_columns(df):
    # to delete unrelated columns. 

    
    df = df.drop(columns=['Donor Id','Title','Ethnic','Gender','City','State','Country','Home Phone','Work Phone',
                        'Date of Birth','Last Pledge Amount',
                        'Last Cash Amount','Last Pledge Date','Last Cash Date','Pledge id',
                        'Pledge Date','Pledge Start Date','Pledge End Date',
                        'Payment Method','Truncated CC',
                        'Frequency','Cardholder Name','Gift Date','Campaign',
                        'Campaign Name','Action','Bank Account Number','Bank Account Holder Name',
                        'Preferred Change Date','Description','DRTV Time','Bank','Unique Id',
                        'Membership No','IPay88 Tokenized ID'
                        ])
    
    return df

def convert_to_expiry_format(df, expiry_column):
    date_format_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def convert_date(value):
        if date_format_regex.match(value):
            # Convert "dd-mm-yyyy" to "MM/YY"
            date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
            return date_obj.strftime("%m/%y")
        else:
            return value

    df[expiry_column] = df[expiry_column].astype(str).apply(convert_date)
    
    return df

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
        'status_email': 'statusEmail=processing-mly@unicef.org',
        'target_api': 'targetAPIVersion=1.224'
    }

    empty_row = []

    field_names = [
        'ccAuthService_run', 'ccCaptureService_run', 'purchaseTotals_currency', 'merchantReferenceCode',
        'purchaseTotals_grandTotalAmount', 'billTo_firstName', 'billTo_lastName', 'billTo_street1',
        'billTo_city', 'billTo_postalCode', 'billTo_country', 'billTo_email', 'card_accountNumber',
        'card_expirationMonth', 'card_expirationYear', 'card_cardtype'
    ]

    footer_data = ['END', 'SUM=1']

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

     #Write to CSV
    first_row_data.to_csv(save_file_path, index=False, header=False, mode='w')  # Write header data
    second_row_data.to_csv(save_file_path, index=False, header=False, mode='a')  # Append field names
    third_row_data.to_csv(save_file_path, index=False, header=False, mode='a')  # Append field names
    data_rows.to_csv(save_file_path, index=False, header=False, mode='a', quoting=csv.QUOTE_NONNUMERIC)       # Append main data rows
    last_row_data.to_csv(save_file_path, index=False, header=False, mode='a')   # Append footer data





def main():
    folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\Do all code testing here'

    for file in os.listdir(folder_path):
        if 'MCO_UTS' in file and '.xlsx' in file:
            

            file_path = os.path.join(folder_path, file)

            df = pd.read_excel(file_path)

            df = convert_to_expiry_format(df, 'Expiry Date')
            df = drop_columns(df)
            df = create_expiry_month(df, 'Expiry Date')
            df = create_expiry_year(df, 'Expiry Date')
            df = convert_payment_submethod(df, 'Payment Submethod')
            
            if 'Email' not in df.columns:
                # create email column with empty data
                df['Email'] = ''
                # create street column with empty data
                df['Street'] = ''
                # create post code column with empty data
                df['Post Code'] = ''
            else:
                pass
            
            df = process_street_data(df)
            new_df = create_template_table()
            new_df = copy_data_into_table(new_df, df)
            new_df['ccAuthService_run'] = new_df['ccAuthService_run'].astype(str)
            new_df['ccCaptureService_run'] = new_df['ccCaptureService_run'].astype(str)

            


            batch_number = batch_counter(folder_path)
            current_date = get_current_date()

            header_data, field_names, footer_data, empty_row = main_template(folder_path, new_df, batch_number)
            
            file_creation(header_data, field_names, empty_row, footer_data, new_df, folder_path, batch_number)
            
            new_df.to_excel(os.path.join(folder_path, 'test.xlsx'), index=False)

            


print('Run completed')

if __name__ == "__main__":
    main()