"""Top-level orchestrator — routes queries to appropriate crew."""

import models  # noqa: F401 — register all ORM models for FK resolution
import json
from agents.llm_config import get_llm
from agents.knowledge.data_access import DataAccessLayer


ROUTER_PROMPT = """You are the CustomerChurn AI orchestrator for Laborie (a medical device company).
Route the user's question to the appropriate analysis.

Available actions:
1. "customer_detail" - Questions about a specific customer (needs customer_no)
2. "churn_risk" - Questions about churn risk, at-risk customers
3. "retention" - Questions about retention strategies, interventions
4. "market_intel" - Questions about market opportunities, segments, growth
5. "general" - General questions you can answer from the data

Extract any customer number mentioned (numeric ID).

Respond with JSON only:
{
    "action": "<one of the actions above>",
    "customer_no": "<customer number if mentioned, else null>",
    "segment": "<segment/region if mentioned, else null>"
}
"""


def run_chat_query(message: str, llm_model: str) -> str:
    """Route and answer a chat query using the appropriate crew."""
    llm = get_llm(llm_model)

    # Step 1: Route the query
    route_response = llm.invoke(f"{ROUTER_PROMPT}\n\nUser query: {message}")
    route_content = route_response.content.strip()

    if route_content.startswith("```"):
        route_content = route_content.split("```")[1]
        if route_content.startswith("json"):
            route_content = route_content[4:]

    try:
        route = json.loads(route_content)
    except json.JSONDecodeError:
        start = route_content.find("{")
        end = route_content.rfind("}") + 1
        if start >= 0 and end > start:
            route = json.loads(route_content[start:end])
        else:
            route = {"action": "general"}

    action = route.get("action", "general")
    customer_no = route.get("customer_no")
    segment = route.get("segment")

    # Step 2: Gather context based on route
    context = ""

    if action == "customer_detail" and customer_no:
        data = DataAccessLayer.get_customer_detail(customer_no)
        if data:
            context = f"Customer data:\n{json.dumps(data, indent=2, default=str)}"

            txn_df = DataAccessLayer.get_customer_transactions(customer_no)
            if not txn_df.empty:
                context += f"\n\nRecent transactions:\n{txn_df.head(20).to_string(index=False)}"
        else:
            context = f"No customer found with number {customer_no}."

    elif action in ("churn_risk", "retention"):
        df = DataAccessLayer.get_high_risk_customers(limit=20)
        context = f"Top at-risk customers:\n{df.to_string(index=False, max_rows=20)}"

        if customer_no:
            data = DataAccessLayer.get_customer_detail(customer_no)
            if data:
                context += f"\n\nSpecific customer {customer_no}:\n{json.dumps(data, indent=2, default=str)}"

    elif action == "market_intel":
        segment_df = DataAccessLayer.get_revenue_by_segment()
        region_df = DataAccessLayer.get_region_performance()
        context = (
            f"Segment performance:\n{segment_df.to_string(index=False, max_rows=20)}\n\n"
            f"Region performance:\n{region_df.to_string(index=False)}"
        )

    else:
        # General — provide overview
        df = DataAccessLayer.get_high_risk_customers(limit=10)
        region_df = DataAccessLayer.get_region_performance()
        context = (
            f"Top at-risk customers:\n{df.to_string(index=False, max_rows=10)}\n\n"
            f"Region overview:\n{region_df.to_string(index=False)}"
        )

    # Step 3: Generate response
    answer_prompt = f"""You are the CustomerChurn AI assistant for Laborie (medical device company).
Answer the user's question using the data provided. Be specific, cite numbers, and give actionable insights.
Format your response clearly with sections if needed.

DATA CONTEXT:
{context}

USER QUESTION: {message}"""

    answer_response = llm.invoke(answer_prompt)
    return answer_response.content
