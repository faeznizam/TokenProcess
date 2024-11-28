import pandas as pd
import datetime
import os
import re

def create_template_table():
    table_template = {
        'paySubscriptionCreateService_run' : [], 	
        'ccAuthService_run' : [], 
        'billTo_firstName' : [],	
        'billTo_lastName' : [],	
        'billTo_email' : [],	
        'billTo_street1' : [],	
        'billTo_city' : [],	
        'billTo_state' : [],	
        'billTo_country' : [],	
        'billTo_postalCode' : [],	
        'card_accountNumber' : [],	
        'card_expirationMonth' : [],	
        'card_expirationYear' : [],	
        'card_cardType' : [],	
        'purchaseTotals_currency' : [],	
        'merchantReferenceCode' : [],	
        'purchaseTotals_grandTotalAmount' : [],	
        'recurringSubscriptionInfo_amount' : [],	
        'recurringSubscriptionInfo_frequency' : [],
        }
    
    return pd.DataFrame(table_template)

def copy_data_into_table(new_df, df):
    new_df['billTo_firstName'] = df['First Name']
    new_df['paySubscriptionCreateService_run'] = 'true'
    new_df['ccAuthService_run'] = 'true'
    new_df['billTo_lastName'] = df['Last Name']
    new_df['billTo_email'] = df['Email']	
    new_df['billTo_street1'] = df['Street']	
    new_df['billTo_city'] = 'Malaysia'
    new_df['billTo_state'] = 'MY'
    new_df['billTo_country'] = 'MY'
    new_df['billTo_postalCode'] = df['Post Code']	
    new_df['card_accountNumber'] = df['PAN 16/15 digits']	
    new_df['card_expirationMonth'] = df['Expiry Month']
    new_df['card_expirationYear'] = df['Expiry Year']
    new_df['card_cardType'] = df['Payment Submethod (Mastercard/Visa/Amex)']
    new_df['purchaseTotals_currency'] = 'MYR'
    new_df['merchantReferenceCode']	 = df['Pledge ID']
    new_df['purchaseTotals_grandTotalAmount'] = '0'
    new_df['recurringSubscriptionInfo_amount'] = '0'
    new_df['recurringSubscriptionInfo_frequency'] = 'on-demand'

    return new_df

def drop_columns(df):
    # to delete unrelated columns. 
    df = df.drop(columns=['Supporter ID', 'Issuing Bank',
       'CardHolder Name', 'Payment Method (DC/CC)',
       'Mobile Number','Current Payment Gateway', 
       'New PL/OT Case Number'])

    return df

def convert_payment_submethod(df):
    # to convert data, visa = 001, mastercard = 002, amex = 003

    df['Payment Submethod (Mastercard/Visa/Amex)'] = df['Payment Submethod (Mastercard/Visa/Amex)'].str.lower()
    
    df['Payment Submethod (Mastercard/Visa/Amex)'].replace('mastercard', '002', inplace=True)
    df['Payment Submethod (Mastercard/Visa/Amex)'].replace('master', '002', inplace=True)
    df['Payment Submethod (Mastercard/Visa/Amex)'].replace('visa', '001', inplace=True)
    df['Payment Submethod (Mastercard/Visa/Amex)'].replace('amex', '003', inplace=True)
     
    return df

def convert_to_expiry_format(df, column_name):
    # build pattern with re
    date_format_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def convert_date(value):
        # check if data match the pattern then convert to desired format
        if date_format_regex.match(value):
            # Convert "yyyy-mm-dd" to "MM/YY"
            date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
            return date_obj.strftime("%m/%y")
        else:
            return value

    df[column_name] = df[column_name].astype(str).apply(convert_date)
    
    return df

def create_expiry_month(df):
    # Define regex patterns for extracting the month part
    pattern1 = r'\d{4}-(\d{2})-\d{2} \d{2}:\d{2}:\d{2}'  # Extracts the month from DD-MM-YYYY
    pattern2 = r'^(0[1-9]|1[0-2])/\d{2}$'  # Matches MM/YY
    
    # Use str.extract() to get the month for DD-MM-YYYY format
    df['Expiry Month'] = df['Expiry Date MM/YY format'].str.extract(pattern1, expand=False)
    
    # Fill the missing values for the MM/YY format using str.extract()
    df['Expiry Month'] = df['Expiry Month'].fillna(
        df['Expiry Date MM/YY format'].str.extract(r'^(0[1-9]|1[0-2])', expand=False)
    )
    
    # Set 'Invalid' for non-matching rows
    df['Expiry Month'] = df['Expiry Month'].fillna('')

    return df

def create_expiry_year(df):
    # Define regex patterns for extracting the year
    pattern1 = r'^(\d{4})-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'  # Extracts the year from DD-MM-YYYY
    pattern2 = r'^(0[1-9]|1[0-2])/(\d{2})$'  # Extracts the year from MM/YY

    # Extract the year for DD-MM-YYYY format
    df['Expiry Year'] = df['Expiry Date MM/YY format'].str.extract(pattern1, expand=False)

    # Extract and convert the year for MM/YY format
    df['Expiry Year'] = df['Expiry Year'].fillna(
        df['Expiry Date MM/YY format'].str.extract(pattern2, expand=False)[1].apply(lambda x: '20' + x if pd.notna(x) else x)
    )

    # Set 'Invalid' for non-matching rows
    df['Expiry Year'] = df['Expiry Year'].fillna('')
    
    return df



def main():
    folder_path = r'C:\Users\mfmohammad\OneDrive - UNICEF\Documents\Codes\task_batch_tokenization\test_data'

    for file in os.listdir(folder_path):
        if 'New Card Token' in file:
            file_path = os.path.join(folder_path, file)
            data = pd.read_excel(file_path)

            data = convert_to_expiry_format(data, 'Expiry Date MM/YY format')
            data = drop_columns(data)
            data = convert_payment_submethod(data)
            data = create_expiry_month(data)
            data = create_expiry_year(data)

            # create email column with empty data
            data['Email'] = ''
            # create street column with empty data
            data['Street'] = ''
            # create post code column with empty data
            data['Post Code'] = ''

            new_data = create_template_table()
            new_data = copy_data_into_table(new_data, data)
            
            

            print(new_data)

            "update"

if __name__ == '__main__':
    main()