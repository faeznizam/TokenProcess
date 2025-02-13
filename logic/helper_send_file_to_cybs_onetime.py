import pandas as pd
import re
import datetime
import os

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



def process_data_table(folder_path, file, payment_submethod_column, expiry_column):
    # flow for processing data in the table using all functions created

    file_path = os.path.join(folder_path, file)
    original_df = pd.read_excel(file_path)
    df = original_df
    df = convert_to_expiry_format(df, expiry_column)
    df = drop_columns(df)
    df = create_expiry_month(df, expiry_column)
    df = create_expiry_year(df, expiry_column)
    df = convert_payment_submethod(df, payment_submethod_column)
    

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
    
    return new_df, original_df






if __name__ == "__main__":
    process_data_table()