import pandas as pd
from sqlalchemy import text
from models.database import engine, get_db_session


def load_enriched_csv(csv_path: str = "files/CustomerChurn_Enriched_Master.csv"):
    """Load the enriched master CSV into PostgreSQL customers + transactions tables."""
    df = pd.read_csv(csv_path, low_memory=False)

    # Parse date columns
    date_cols = ["transaction_date", "TA_Date", "first_transaction_date", "last_transaction_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # --- Load customers table ---
    customer_cols_map = {
        "customer_no": "customer_no",
        "customer_name": "customer_name",
        "industry": "industry",
        "sales_region": "sales_region",
        "st_state": "st_state",
        "st_city": "st_city",
        "USS_consumables_segment": "consumables_segment",
        "USS_capital_segment": "capital_segment",
        "USS_NPIs_tercile": "npi_tercile",
        "account_age_months": "account_age_months",
        "csat_score": "csat_score",
        "customer_profile": "customer_profile",
        "first_transaction_date": "first_transaction_date",
        "last_transaction_date": "last_transaction_date",
        "sales_inactivity_days": "sales_inactivity_days",
        "churn_flag": "churn_flag",
    }

    # Deduplicate: one row per customer (take last occurrence which has latest data)
    df_customers = df.sort_values("transaction_date").drop_duplicates(
        subset=["customer_no"], keep="last"
    )
    df_cust = df_customers[[c for c in customer_cols_map.keys() if c in df.columns]].rename(
        columns=customer_cols_map
    )
    df_cust["customer_no"] = df_cust["customer_no"].astype(str)

    # --- Load transactions table ---
    txn_cols_map = {
        "SalesTA_ID": "sales_ta_id",
        "customer_no": "customer_no",
        "product": "product",
        "product_GBU": "product_gbu",
        "product_main_grp": "product_main_grp",
        "transaction_date": "transaction_date",
        "FP_qty": "quantity",
        "amnt": "amount",
        "GM": "gross_margin",
        "cost": "cost",
        "invoice_type": "invoice_type",
        "sales_region": "sales_region",
        "sales_territory": "sales_territory",
        "SalesRep": "sales_rep",
    }

    df_txn = df[[c for c in txn_cols_map.keys() if c in df.columns]].rename(
        columns=txn_cols_map
    )
    df_txn["customer_no"] = df_txn["customer_no"].astype(str)

    # Clear existing data in FK-safe order (agent outputs reference customers).
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM interventions"))
        conn.execute(text("DELETE FROM diagnoses"))
        conn.execute(text("DELETE FROM churn_scores"))
        conn.execute(text("DELETE FROM transactions"))
        conn.execute(text("DELETE FROM customers"))

    df_cust.to_sql("customers", engine, if_exists="append", index=False, method="multi",
                    chunksize=500)
    df_txn.to_sql("transactions", engine, if_exists="append", index=False, method="multi",
                   chunksize=1000)

    return len(df_cust), len(df_txn)


def load_uploaded_csv(df: pd.DataFrame):
    """Load a user-uploaded CSV through the cleaning pipeline and into the DB.
    Returns (customers_count, transactions_count)."""
    from services.customer_cleaning import run_cust_clean
    from services.churn_flagging import flag_churn

    df_full, df_not_found, df_valid, df_valid_cust_prod = run_cust_clean(df)
    return df_full, df_not_found, df_valid, df_valid_cust_prod


if __name__ == "__main__":
    cust_count, txn_count = load_enriched_csv()
    print(f"Loaded {cust_count} customers and {txn_count} transactions")
