# SalesFlag.py

import streamlit as st
import pandas as pd
from SalesChurn import flag_churn
from typing import Any

def sorted_csv_by_inactivity(df: pd.DataFrame) -> bytes:
    """
    Takes a DataFrame with a 'sales_inactivity' column,
    sorts it descending, and returns the CSV as UTF-8 bytes.
    """
    df_sorted = df.sort_values(by="sales_inactivity", ascending=False)
    return df_sorted.to_csv(index=False).encode("utf-8")

def format_transactiondate(df: pd.DataFrame) -> pd.DataFrame:
    """Format 'transactiondate' as MM/DD/YYYY."""
    df = df.copy()
    df["transactiondate"] = pd.to_datetime(
        df["transactiondate"], errors="coerce"
    ).dt.strftime("%m/%d/%Y")
    return df

def show_sales_flag(df_valid: pd.DataFrame, noop: Any):
    """
    Display the Sales Inactivity / Churn Flags section.
    """
    st.markdown(
        '<h2 class="sales-flag">🚩 Flagging by Sales Inactivity</h2>',
        unsafe_allow_html=True
    )

    if "transactiondate" not in df_valid.columns:
        st.warning(
            "The valid customers data does not contain a 'transactiondate' column. "
            "Please include it to calculate sales inactivity."
        )
        return

    if not st.session_state.get("apply", False):
       st.info("Set your Yellow & Red flags in the sidebar, then click 'Apply Thresholds'.")
       return

    # Drop Excel-generated empty columns like "Unnamed:…"
    df_valid = df_valid.loc[:, ~df_valid.columns.str.startswith("Unnamed")]

    # Make a copy and ensure datetime
    df_valid = df_valid.copy()
    df_valid["transactiondate"] = pd.to_datetime(df_valid["transactiondate"], errors="coerce")
    today = pd.Timestamp.today()

    # Compute inactivity days
    df_valid["sales_inactivity"] = (today - df_valid["transactiondate"]).dt.days

    # Compute churn segments (leave formatting until after segments)
    df_last, df_yellow, df_red = flag_churn(
        df_valid, today, st.session_state.yellow, st.session_state.red
    )

    # Apply date formatting now
    df_yellow = format_transactiondate(df_yellow)
    df_red = format_transactiondate(df_red)

    # Yellow-flagged customers
    st.markdown(
        f'<h3 style="color:#FAF3E0">🟨 Inactivity ≥ {st.session_state.yellow} and < {st.session_state.red} days</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download YellowFlagCustomers.csv",
        data=sorted_csv_by_inactivity(df_yellow),
        file_name="YellowFlagCustomers.csv",
        mime="text/csv",
        on_click=noop
    )

    # Red-flagged customers
    st.markdown(
        f'<h3 style="color:#FAF3E0">🟥 Inactivity > {st.session_state.red} days</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download RedFlagCustomers.csv",
        data=sorted_csv_by_inactivity(df_red),
        file_name="RedFlagCustomers.csv",
        mime="text/csv",
        on_click=noop
    )

    st.markdown(
        '<p style="color:#FAF3E0; font-size:1.2em;">Flagged customer files generated.</p>',
        unsafe_allow_html=True
    )
