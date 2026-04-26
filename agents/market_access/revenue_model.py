"""Revenue/profitability modeling agent."""

import json
from agents.knowledge.data_access import DataAccessLayer
from agents.market_access.prompts import REVENUE_MODEL_PROMPT


def model_revenue(llm) -> dict:
    """Project revenue by segment with retention-rate adjustments."""
    segment_df = DataAccessLayer.get_revenue_by_segment()

    data_summary = f"SEGMENT PERFORMANCE DATA:\n{segment_df.to_string(index=False, max_rows=30)}"

    prompt_text = f"{REVENUE_MODEL_PROMPT}\n\n{data_summary}"
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
