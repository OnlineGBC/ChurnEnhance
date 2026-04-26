"""Data access layer for agents — queries PostgreSQL via SQLAlchemy."""

import pandas as pd
from sqlalchemy import text
from models.database import get_db_session, engine


class DataAccessLayer:
    """Provides structured data queries for agent tools."""

    @staticmethod
    def get_high_risk_customers(limit: int = 200) -> pd.DataFrame:
        """Get customers sorted by inactivity (pre-filter for LLM)."""
        query = """
            SELECT c.customer_no, c.customer_name, c.industry, c.sales_region,
                   c.st_state, c.st_city, c.consumables_segment, c.capital_segment,
                   c.npi_tercile, c.account_age_months, c.csat_score,
                   c.customer_profile, c.last_transaction_date,
                   c.sales_inactivity_days, c.churn_flag,
                   COALESCE(SUM(t.amount), 0) as total_revenue,
                   COUNT(t.id) as transaction_count,
                   COALESCE(SUM(t.gross_margin), 0) as total_margin
            FROM customers c
            LEFT JOIN transactions t ON c.customer_no = t.customer_no
            WHERE c.sales_inactivity_days IS NOT NULL
            GROUP BY c.customer_no, c.customer_name, c.industry, c.sales_region,
                     c.st_state, c.st_city, c.consumables_segment, c.capital_segment,
                     c.npi_tercile, c.account_age_months, c.csat_score,
                     c.customer_profile, c.last_transaction_date,
                     c.sales_inactivity_days, c.churn_flag
            ORDER BY c.sales_inactivity_days DESC
            LIMIT :limit
        """
        return pd.read_sql(text(query), engine, params={"limit": limit})

    @staticmethod
    def get_customer_detail(customer_no: str) -> dict:
        """Get full customer info with transaction summary."""
        db = get_db_session()
        try:
            result = db.execute(text("""
                SELECT c.*,
                       COALESCE(SUM(t.amount), 0) as total_revenue,
                       COUNT(t.id) as transaction_count,
                       COALESCE(SUM(t.gross_margin), 0) as total_margin,
                       COUNT(DISTINCT t.product) as product_count,
                       COUNT(DISTINCT t.product_gbu) as gbu_count
                FROM customers c
                LEFT JOIN transactions t ON c.customer_no = t.customer_no
                WHERE c.customer_no = :cno
                GROUP BY c.customer_no
            """), {"cno": str(customer_no)}).fetchone()
            return dict(result._mapping) if result else {}
        finally:
            db.close()

    @staticmethod
    def get_customer_transactions(customer_no: str) -> pd.DataFrame:
        """Get all transactions for a customer."""
        query = """
            SELECT * FROM transactions
            WHERE customer_no = :cno
            ORDER BY transaction_date DESC
        """
        return pd.read_sql(text(query), engine, params={"cno": str(customer_no)})

    @staticmethod
    def get_revenue_by_segment() -> pd.DataFrame:
        """Get revenue aggregated by industry/segment."""
        query = """
            SELECT c.industry, c.consumables_segment, c.capital_segment,
                   c.sales_region,
                   COUNT(DISTINCT c.customer_no) as customer_count,
                   COALESCE(SUM(t.amount), 0) as total_revenue,
                   COALESCE(SUM(t.gross_margin), 0) as total_margin,
                   AVG(c.sales_inactivity_days) as avg_inactivity,
                   SUM(CASE WHEN c.churn_flag = 'Red' THEN 1 ELSE 0 END) as red_count
            FROM customers c
            LEFT JOIN transactions t ON c.customer_no = t.customer_no
            GROUP BY c.industry, c.consumables_segment, c.capital_segment, c.sales_region
            ORDER BY total_revenue DESC
        """
        return pd.read_sql(text(query), engine)

    @staticmethod
    def get_product_performance() -> pd.DataFrame:
        """Get product-level performance metrics."""
        query = """
            SELECT t.product_gbu, t.product,
                   COUNT(DISTINCT t.customer_no) as customer_count,
                   SUM(t.amount) as total_revenue,
                   SUM(t.gross_margin) as total_margin,
                   AVG(t.amount) as avg_order_value
            FROM transactions t
            GROUP BY t.product_gbu, t.product
            ORDER BY total_revenue DESC
        """
        return pd.read_sql(text(query), engine)

    @staticmethod
    def get_region_performance() -> pd.DataFrame:
        """Get region-level performance."""
        query = """
            SELECT c.sales_region,
                   COUNT(DISTINCT c.customer_no) as customer_count,
                   SUM(t.amount) as total_revenue,
                   SUM(t.gross_margin) as total_margin,
                   AVG(c.sales_inactivity_days) as avg_inactivity,
                   SUM(CASE WHEN c.churn_flag = 'Red' THEN 1 ELSE 0 END) as red_count,
                   SUM(CASE WHEN c.churn_flag = 'Yellow' THEN 1 ELSE 0 END) as yellow_count
            FROM customers c
            LEFT JOIN transactions t ON c.customer_no = t.customer_no
            GROUP BY c.sales_region
            ORDER BY total_revenue DESC
        """
        return pd.read_sql(text(query), engine)

    @staticmethod
    def get_churned_customer_archetypes() -> pd.DataFrame:
        """Get archetypes of churned customers for ICP exclusion."""
        query = """
            SELECT c.industry, c.sales_region, c.consumables_segment,
                   c.capital_segment, c.npi_tercile,
                   AVG(c.account_age_months) as avg_age,
                   AVG(c.csat_score) as avg_csat,
                   COUNT(*) as count
            FROM customers c
            WHERE c.churn_flag = 'Red'
            GROUP BY c.industry, c.sales_region, c.consumables_segment,
                     c.capital_segment, c.npi_tercile
            HAVING COUNT(*) >= 3
            ORDER BY count DESC
        """
        return pd.read_sql(text(query), engine)
