# ProductFlag.py

"""
ProductFlag.py provides Streamlit UI functionality for analyzing customer
“product inactivity” (i.e. identifying “lost” customers based on a
rolling-month threshold, excluding any invalid customers).

Functions provided:
- show_product_flag: renders the Product Inactivity tab, taking:
    • df_full: the full transactions history DataFrame
    • df_valid: the filtered “valid customers” DataFrame
    • df_valid_cust_prod: placeholder DataFrame of valid customer+product combos
    • noop: a no-op callback (for download buttons, if needed)

This module is called by file_cleansing.py and does not call other scripts
except for the dateutil.relativedelta helper.
"""

import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta

def show_product_flag(
    df_full: pd.DataFrame,
    df_valid: pd.DataFrame,
    df_valid_cust_prod: pd.DataFrame,
    noop
):
    """
    Display the Product Inactivity section, identifying 'lost' customers
    based on a rolling-month threshold, excluding any invalid customers.
    """

    # Section header
    st.markdown(
        '<h2 style="color:#FAF3E0">📦 Product Inactivity</h2>',
        unsafe_allow_html=True
    )

    # 1) Pick the date column
    if "TA_Date" in df_full.columns:
        date_col = "TA_Date"
    elif "transactiondate" in df_full.columns:
        date_col = "transactiondate"
    else:
        st.warning(
            "Missing date column ('TA_Date' or 'transactiondate') for product inactivity."
        )
        return

    # 2) How many months back to consider “lost”?
    selected_lost_months = st.number_input(
        "Lost threshold (months)", min_value=1, value=3, step=1
    )

    # 3) Drop any IDs that weren’t “valid customers”
    valid_ids = set(df_valid["customer_no"])
    df_full = df_full[df_full["st_customer_no"].isin(valid_ids)].copy()

    # 4) Ensure our date column is datetime
    df_full.loc[:, date_col] = pd.to_datetime(df_full[date_col], errors="coerce")

    # 5) Find the start of the “current” month
    max_date = df_full[date_col].max()
    if pd.isna(max_date):
        st.warning("No transaction dates found.")
        return
    current_month_start = max_date.replace(day=1)

    # 6) Compute cutoff date
    lost_cutoff = current_month_start - relativedelta(months=selected_lost_months)

    # 7) Identify past vs. recent customers
    past_customers = set(
        df_full.loc[df_full[date_col] < current_month_start, "st_customer_no"].unique()
    )
    recent_customers = set(
        df_full.loc[df_full[date_col] >= lost_cutoff, "st_customer_no"].unique()
    )

    # 8) Those in past but not recent are “lost”
    lost_customers = past_customers - recent_customers
    lost_count = len(lost_customers)

    # 9) Display the count
    st.metric("Lost Customers Count", lost_count)

    # noop remains available for any future CSV download buttons
