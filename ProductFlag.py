"""
ProductFlag.py provides Streamlit UI functionality for analyzing customer
“product inactivity” by applying the same yellow/red thresholds used in SalesFlag.

Functions provided:
- show_product_flag: renders the Product Inactivity tab, taking:
    • df_full: full transaction history DataFrame
    • df_valid: filtered “valid customers” DataFrame (with customer_no_dupes)
    • df_valid_cust_prod: unique customer+product combos (unused in this version)
    • noop: a no-op callback for download buttons

This module is called by file_cleansing.py.
"""

import streamlit as st
import pandas as pd

def show_product_flag(
    df_full: pd.DataFrame,
    df_valid: pd.DataFrame,
    df_valid_cust_prod: pd.DataFrame,
    noop
):
    """
    Display the Product Inactivity tab by:
      1) Filtering to valid customers,
      2) Grouping by customer_no_dupes + product,
      3) Finding each last transaction date (with full row data),
      4) Computing inactivity days,
      5) Splitting into yellow/red flag groups based on session thresholds,
      6) Offering downloads of the resulting CSVs.
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
        st.warning("Missing date column ('TA_Date' or 'transactiondate') for product inactivity.")
        return

    # 2) Keep only valid customers
    valid_ids = set(df_valid["customer_no_dupes"])
    df_full = df_full[df_full["customer_no_dupes"].isin(valid_ids)].copy()

    # 3) Ensure datetime and get today
    df_full.loc[:, date_col] = pd.to_datetime(df_full[date_col], errors="coerce")
    today = pd.Timestamp.today()

    # 4) Find last transaction per customer+product (keeping full rows)
    idx = df_full.groupby(["customer_no_dupes", "product"])[date_col].idxmax()
    df_last_prod = df_full.loc[idx].copy()

    # 5) Compute inactivity days safely
    df_last_prod["sales_inactivity"] = df_last_prod[date_col].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )

    # 6) Format transactiondate into MM/DD/YYYY
    df_last_prod["transactiondate"] = pd.to_datetime(
        df_last_prod["transactiondate"], errors="coerce"
    ).dt.strftime("%m/%d/%Y")

    # 7) Get thresholds from session state
    yellow_flag = st.session_state.get("yellow")
    red_flag = st.session_state.get("red")
    if yellow_flag is None or red_flag is None:
        st.info("Set your Yellow & Red flags in the sidebar, then click 'Apply Thresholds'.")
        return

    # 8) Split into yellow and red groups
    df_yellow = df_last_prod[
        (df_last_prod["sales_inactivity"] >= yellow_flag) &
        (df_last_prod["sales_inactivity"] < red_flag)
    ]
    df_red = df_last_prod[df_last_prod["sales_inactivity"] >= red_flag]

    # 9) Render download buttons
    st.markdown(
        f'<h3 style="color:#FAF3E0">🟨 Inactivity ≥ {yellow_flag} and < {red_flag} days</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download ProductYellowFlag.csv",
        data=df_yellow.to_csv(index=False).encode("utf-8"),
        file_name="ProductYellowFlagCustomers.csv",
        mime="text/csv",
        on_click=noop
    )

    st.markdown(
        f'<h3 style="color:#FAF3E0">🟥 Inactivity ≥ {red_flag} days</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download ProductRedFlag.csv",
        data=df_red.to_csv(index=False).encode("utf-8"),
        file_name="ProductRedFlagCustomers.csv",
        mime="text/csv",
        on_click=noop
    )
