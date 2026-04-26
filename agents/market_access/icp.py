"""Ideal Customer Profile agent — builds profiles of best customer types."""

import json
from agents.knowledge.data_access import DataAccessLayer
from agents.market_access.prompts import ICP_PROMPT


def build_icp_profiles(llm, market_intel: dict = None) -> list:
    """Build ideal customer profiles based on segment data and churn archetypes."""
    segment_df = DataAccessLayer.get_revenue_by_segment()
    archetypes_df = DataAccessLayer.get_churned_customer_archetypes()

    archetype_info = "No churned archetypes found."
    if not archetypes_df.empty:
        archetype_info = archetypes_df.to_string(index=False, max_rows=20)

    data_summary = (
        f"SEGMENT PERFORMANCE:\n{segment_df.to_string(index=False, max_rows=30)}\n\n"
        f"CHURNED CUSTOMER ARCHETYPES (exclude these profiles):\n{archetype_info}"
    )

    if market_intel:
        opportunities = market_intel.get("growth_opportunities", [])
        if opportunities:
            data_summary += f"\n\nGROWTH OPPORTUNITIES:\n{json.dumps(opportunities, indent=2)}"

    prompt_text = f"{ICP_PROMPT}\n\n{data_summary}"
    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        profiles = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            profiles = json.loads(content[start:end])
        else:
            profiles = []

    return profiles
