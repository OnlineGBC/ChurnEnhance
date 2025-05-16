import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta  # <– can remove relativedelta import now

def show_product_flag(
    df_full: pd.DataFrame,
    df_valid: pd.DataFrame,
    df_valid_cust_prod: pd.DataFrame,
    noop
):
    """
    Display the Product Inactivity section, identifying 'lost' customers
    based on your existing day‐based inactivity thresholds.
    """

    # Custom styled header
    st.markdown(
        '<h2 style="color:#FAF3E0">📦 Product Inactivity</h2>',
        unsafe_allow_html=True
    )

    # 1) Pick date column
    if "TA_Date" in df_full.columns:
        date_col = "TA_Date"
    elif "transactiondate" in df_full.columns:
        date_col = "transactiondate"
    else:
        st.warning("Missing date column ('TA_Date' or 'transactiondate') for product inactivity.")
        return

    # 2) Pull your existing day‐based thresholds
    yellow_flag = st.session_state.get("yellow")
    red_flag    = st.session_state.get("red")
    if yellow_flag is None or red_flag is None:
        st.warning("Please set Yellow/Red flags in the sidebar and click 'Apply Thresholds' first.")
        return

    st.write(f"Using inactivity thresholds: **Yellow ≥ {yellow_flag} days**, **Red > {red_flag} days**")

    # 3) Filter only valid‐customer history
    valid_ids = set(df_valid["customer_no_dupes"])
    df_full  = df_full[df_full["st_customer_no"].isin(valid_ids)].copy()

    # 4) Ensure datetime
    df_full.loc[:, date_col] = pd.to_datetime(df_full[date_col], errors="coerce")

    # 5) Last transaction per customer
    idx_max = df_full.groupby("st_customer_no")[date_col].idxmax()
    df_last = df_full.loc[idx_max].copy()

    # 6) Compute days inactive
    today = pd.Timestamp.today()
    df_last.loc[:, "days_inactive"] = (
        today - df_last[date_col]
    ).apply(lambda x: x.days if pd.notnull(x) else None)

    # 7) Lost customers = days_inactive > red_flag
    lost = df_last[df_last["days_inactive"] > red_flag]
    lost_count = lost.shape[0]

    # 8) Display lost count
    st.metric(f"Customers with > {red_flag} days since last purchase", lost_count)

    # 9) Optional: show full rows
    if st.checkbox("Show lost customer details"):
        st.dataframe(lost.reset_index(drop=True))
