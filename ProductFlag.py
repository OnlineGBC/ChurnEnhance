# ProductFlag.py

import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta

def show_product_flag(df_full: pd.DataFrame, df_valid: pd.DataFrame, noop):
    """
    Display the Product Inactivity section, identifying 'lost' customers
    based on a rolling-month threshold, excluding any invalid customers.
    """

    # Custom styled header for Product Inactivity
    st.markdown(
        '<h2 style="color:#FAF3E0">📦 Product Inactivity</h2>',
        unsafe_allow_html=True
    )

    # 1) Determine which date column to use
    if "TA_Date" in df_full.columns:
        date_col = "TA_Date"
    elif "transactiondate" in df_full.columns:
        date_col = "transactiondate"
    else:
        st.warning("Missing date column ('TA_Date' or 'transactiondate') for product inactivity.")
        return

    # 2) Threshold input
    selected_lost_months = st.number_input(
        "Lost threshold (months)", min_value=1, value=3, step=1
    )

    # 3) Filter out bad customer IDs
    valid_ids = set(df_valid["customer_no"])
    df_full = df_full[df_full["st_customer_no"].isin(valid_ids)].copy()

    # 4) Ensure we have datetime
    df_full.loc[:, date_col] = pd.to_datetime(df_full[date_col], errors="coerce")

    # 5) Determine current‐month start
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

    # 8) Lost customers = in past but not in recent
    lost_customers = past_customers - recent_customers
    lost_count = len(lost_customers)

    # 9) Display result
    st.metric("Lost Customers Count", lost_count)

    # 10) Optional details
    if st.checkbox("Show lost customer details"):
        df_lost = df_full[df_full["st_customer_no"].isin(lost_customers)]
        st.dataframe(df_lost)

    # noop remains available for any future download buttons
