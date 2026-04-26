"""Market Intelligence agent — revenue concentration and opportunities."""

import json
from agents.knowledge.data_access import DataAccessLayer
from agents.market_access.prompts import MARKET_INTEL_PROMPT


def analyze_market_intel(llm) -> dict:
    """Analyze market intelligence: concentration, opportunities, gaps."""
    segment_df = DataAccessLayer.get_revenue_by_segment()
    region_df = DataAccessLayer.get_region_performance()
    product_df = DataAccessLayer.get_product_performance()

    data_summary = (
        f"SEGMENT DATA:\n{segment_df.to_string(index=False, max_rows=30)}\n\n"
        f"REGION DATA:\n{region_df.to_string(index=False)}\n\n"
        f"PRODUCT DATA:\n{product_df.to_string(index=False, max_rows=20)}"
    )

    prompt_text = f"{MARKET_INTEL_PROMPT}\n\n{data_summary}"
    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        return {}
