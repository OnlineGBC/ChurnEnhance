# SalesFlag.py

import streamlit as st
import pandas as pd
from SalesChurn import flag_churn

def show_sales_flag(df_valid: pd.DataFrame, noop):
    """
    Display the Sales Inactivity / Churn Flags section.
    """
    # Custom class so we can style this header exactly
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

    # Make a copy and ensure datetime
    df_valid = df_valid.copy()
    df_valid.loc[:, "transactiondate"] = pd.to_datetime(
        df_valid["transactiondate"], errors="coerce"
    )
    today = pd.Timestamp.today()

    # Compute inactivity days and strip time
    df_valid.loc[:, "sales_inactivity"] = (
        today - df_valid["transactiondate"]
    ).apply(lambda x: x.days if pd.notnull(x) else None)
    # Convert transactiondate to date-only
    df_valid.loc[:, "transactiondate"] = df_valid["transactiondate"].apply(
        lambda d: d.date() if pd.notnull(d) else None
    )

    # Compute churn segments
    df_last, df_yellow, df_red = flag_churn(
        df_valid, today, st.session_state.yellow, st.session_state.red
    )

    # Yellow-flagged customers
    st.markdown(
        f'<h3 style="color:#FAF3E0">🟨 Inactivity ≥ {st.session_state.yellow} and < {st.session_state.red} days</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download YellowFlagCustomers.csv",
        data=df_yellow.to_csv(index=False).encode("utf-8"),
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
        data=df_red.to_csv(index=False).encode("utf-8"),
        file_name="RedFlagCustomers.csv",
        mime="text/csv",
        on_click=noop
    )

    st.markdown(
        '<p style="color:#FAF3E0; font-size:1.2em;">Flagged customer files generated.</p>',
        unsafe_allow_html=True
    )
