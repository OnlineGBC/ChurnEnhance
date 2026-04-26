"""Lead scoring agent — scores segments for expansion opportunity."""

import json
from agents.knowledge.data_access import DataAccessLayer
from agents.market_access.prompts import LEAD_SCORING_PROMPT


def score_leads(llm, icp_profiles: list) -> list:
    """Score market segments based on ICP profiles and data."""
    segment_df = DataAccessLayer.get_revenue_by_segment()

    data_summary = (
        f"SEGMENT DATA:\n{segment_df.to_string(index=False, max_rows=30)}\n\n"
        f"ICP PROFILES:\n{json.dumps(icp_profiles, indent=2)}"
    )

    prompt_text = f"{LEAD_SCORING_PROMPT}\n\n{data_summary}"
    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        scores = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            scores = json.loads(content[start:end])
        else:
            scores = []

    return scores
