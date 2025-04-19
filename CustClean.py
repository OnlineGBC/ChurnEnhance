# CustClean.py

import pandas as pd
import re

def extract_number(text: str) -> str:
    if pd.isna(text):
        return ""
    if "CONSOLIDATED" in text.upper():
        nums = re.findall(r'\d+', text)
        if nums:
            return nums[-1]
    return ""

def run_cust_clean(df: pd.DataFrame):
    """
    Preprocessing, matching and updating, extracting 'Cust Info Not Found',
    and extracting valid customers.
    Returns tuple: (full_df, df_not_found, df_valid).
    """
    df = df.copy()
    df['customer_no'] = df['customer_no'].astype(str)
    df['billto_customer_name'] = df['billto_customer_name'].astype(str)

    # Step 1: Preprocessing
    df['Extract_Number'] = ""
    df['customer_no_dupes'] = ""
    df['bill_to_custname_wo_dupes'] = ""

    for idx, row in df.iterrows():
        val = row['billto_customer_name']
        if 'CONSOLIDATED' in val.upper():
            df.at[idx, 'Extract_Number'] = extract_number(val)
        else:
            df.at[idx, 'customer_no_dupes'] = row['customer_no']
            df.at[idx, 'bill_to_custname_wo_dupes'] = val

    # Step 2: Matching and Updating
    for idx, row in df.iterrows():
        ext = str(row['Extract_Number']).strip()
        if ext:
            match = df[df['customer_no'] == ext]
            if not match.empty:
                first = match.iloc[0]
                df.at[idx, 'customer_no_dupes'] = first['customer_no']
                df.at[idx, 'bill_to_custname_wo_dupes'] = first['billto_customer_name']
            else:
                df.at[idx, 'customer_no_dupes'] = 'Cust Info Not Found'
                df.at[idx, 'bill_to_custname_wo_dupes'] = 'Cust Info Not Found'

    # Extract rows with 'Cust Info Not Found'
    df_not_found = df[
        (df['customer_no_dupes'] == 'Cust Info Not Found') |
        (df['bill_to_custname_wo_dupes'] == 'Cust Info Not Found')
    ]

    # Extract valid customers
    df_valid = df[
        (df['customer_no_dupes'] != 'Cust Info Not Found') &
        (df['bill_to_custname_wo_dupes'] != 'Cust Info Not Found')
    ]

    return df, df_not_found, df_valid
