"""Churn Risk scoring agent — pre-filters with SQL, LLM scores top-N."""

import json
from agents.knowledge.data_access import DataAccessLayer
from agents.retention.prompts import CHURN_RISK_PROMPT


def score_churn_risk(llm, top_n: int = 50) -> list:
    """Score churn risk for the highest-risk customers.

    Pre-filters using SQL to get top customers by inactivity,
    then uses LLM to assign nuanced risk scores.
    """
    df = DataAccessLayer.get_high_risk_customers(limit=top_n)
    if df.empty:
        return []

    customer_data = df.to_dict(orient="records")
    # Format data concisely for LLM
    summaries = []
    for c in customer_data:
        summaries.append(
            f"Customer {c['customer_no']}: {c.get('customer_name', 'N/A')}, "
            f"Industry={c.get('industry', 'N/A')}, Region={c.get('sales_region', 'N/A')}, "
            f"InactivityDays={c.get('sales_inactivity_days', 'N/A')}, "
            f"Revenue=${c.get('total_revenue', 0):.0f}, "
            f"Transactions={c.get('transaction_count', 0)}, "
            f"CSAT={c.get('csat_score', 'N/A')}, "
            f"AccountAge={c.get('account_age_months', 'N/A')}mo, "
            f"Flag={c.get('churn_flag', 'N/A')}"
        )

    prompt_text = f"{CHURN_RISK_PROMPT}\n\nAnalyze these {len(summaries)} customers:\n" + "\n".join(summaries)

    response = llm.invoke(prompt_text)
    content = response.content.strip()

    # Parse JSON from response
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        scores = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON array
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            scores = json.loads(content[start:end])
        else:
            scores = []

    return scores
