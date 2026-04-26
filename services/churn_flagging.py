"""Churn flagging logic — ported from SalesChurn.py."""

import pandas as pd


def flag_churn(df_valid: pd.DataFrame, today: pd.Timestamp, yellow_flag: int, red_flag: int):
    """
    Compute last transaction per customer, sales_inactivity, and split into yellow/red.
    Returns: (df_last_txn, df_yellow, df_red)
    """
    idx_max = df_valid.groupby(['customer_no_dupes'])['transactiondate'].idxmax()
    df_last_txn = df_valid.loc[idx_max].copy()

    df_last_txn.loc[:, 'transactiondate'] = pd.to_datetime(
        df_last_txn['transactiondate'], errors='coerce'
    )

    df_last_txn.loc[:, 'sales_inactivity'] = df_last_txn['transactiondate'].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )

    df_yellow = df_last_txn[
        (df_last_txn['sales_inactivity'] >= yellow_flag) &
        (df_last_txn['sales_inactivity'] < red_flag)
    ]
    df_red = df_last_txn[df_last_txn['sales_inactivity'] > red_flag]

    return df_last_txn, df_yellow, df_red


def flag_product_churn(df_valid: pd.DataFrame, today: pd.Timestamp,
                       yellow_flag: int, red_flag: int, date_col: str = "transactiondate"):
    """
    Product-level churn flagging (per customer+product combination).
    Returns: (df_last_txn, df_yellow, df_red)
    """
    df_valid = df_valid.copy()
    df_valid[date_col] = pd.to_datetime(df_valid[date_col], errors='coerce')

    idx_max = df_valid.groupby(['customer_no_dupes', 'product'])[date_col].idxmax()
    df_last_txn = df_valid.loc[idx_max].copy()

    df_last_txn.loc[:, 'sales_inactivity'] = df_last_txn[date_col].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )

    df_yellow = df_last_txn[
        (df_last_txn['sales_inactivity'] >= yellow_flag) &
        (df_last_txn['sales_inactivity'] < red_flag)
    ]
    df_red = df_last_txn[df_last_txn['sales_inactivity'] >= red_flag]

    return df_last_txn, df_yellow, df_red
