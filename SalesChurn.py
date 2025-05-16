# SalesChurn.py
import pandas as pd


def flag_churn(df_valid: pd.DataFrame, today: pd.Timestamp, yellow_flag: int, red_flag: int) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Compute last transaction per customer, sales_inactivity, and split into yellow/red.
    Returns: (df_last_txn, df_yellow, df_red)
    """
    # Identify last transaction per customer (group only by customer_no_dupes)
    idx_max = df_valid.groupby(['customer_no_dupes'])['transactiondate'].idxmax()
    df_last_txn = df_valid.loc[idx_max].copy()

    # Ensure transactiondate is datetime
    df_last_txn.loc[:, 'transactiondate'] = pd.to_datetime(df_last_txn['transactiondate'], errors='coerce')

    # Compute inactivity days
    df_last_txn.loc[:, 'sales_inactivity'] = df_last_txn['transactiondate'].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )

    # Split by thresholds (full rows)
    df_yellow = df_last_txn[(df_last_txn['sales_inactivity'] >= yellow_flag) &
                             (df_last_txn['sales_inactivity'] < red_flag)]
    df_red = df_last_txn[df_last_txn['sales_inactivity'] > red_flag]

    return df_last_txn, df_yellow, df_red