"""LangChain tools wrapping data queries for retention agents."""

from langchain_core.tools import tool
from agents.knowledge.data_access import DataAccessLayer


@tool
def get_high_risk_customers(limit: int = 200) -> str:
    """Get customers with highest sales inactivity, sorted by risk. Returns CSV-formatted data."""
    df = DataAccessLayer.get_high_risk_customers(limit)
    return df.to_string(index=False, max_rows=50)


@tool
def get_customer_detail(customer_no: str) -> str:
    """Get detailed information about a specific customer including transaction summary."""
    data = DataAccessLayer.get_customer_detail(customer_no)
    if not data:
        return f"No customer found with number {customer_no}"
    return "\n".join(f"{k}: {v}" for k, v in data.items())


@tool
def get_customer_transactions(customer_no: str) -> str:
    """Get recent transaction history for a specific customer."""
    df = DataAccessLayer.get_customer_transactions(customer_no)
    if df.empty:
        return f"No transactions found for customer {customer_no}"
    return df.to_string(index=False, max_rows=30)


@tool
def get_region_performance() -> str:
    """Get performance metrics by sales region including churn counts."""
    df = DataAccessLayer.get_region_performance()
    return df.to_string(index=False)


RETENTION_TOOLS = [
    get_high_risk_customers,
    get_customer_detail,
    get_customer_transactions,
    get_region_performance,
]
