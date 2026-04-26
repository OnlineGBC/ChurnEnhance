"""Campaign activation agent — outreach strategy and territory assignment."""

import json
from agents.market_access.prompts import CAMPAIGN_PROMPT


def plan_campaigns(llm, icp_profiles: list, lead_scores: list) -> list:
    """Design campaign strategies based on ICP profiles and lead scores."""
    data_summary = (
        f"ICP PROFILES:\n{json.dumps(icp_profiles, indent=2)}\n\n"
        f"LEAD SCORES:\n{json.dumps(lead_scores, indent=2)}"
    )

    prompt_text = f"{CAMPAIGN_PROMPT}\n\n{data_summary}"
    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        campaigns = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            campaigns = json.loads(content[start:end])
        else:
            campaigns = []

    return campaigns
