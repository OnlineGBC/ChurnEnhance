"""Diagnosis agent — identifies failure modes for high-risk customers."""

import json
from agents.retention.prompts import DIAGNOSIS_PROMPT


def diagnose_churn(llm, churn_scores: list) -> list:
    """Diagnose failure modes for customers with high churn risk.

    Takes churn scores and returns diagnoses with failure modes.
    """
    high_risk = [s for s in churn_scores if s.get("risk_level") in ("high", "medium")]
    if not high_risk:
        return []

    # Limit to top 30 for cost management
    high_risk = high_risk[:30]

    summaries = []
    for s in high_risk:
        factors = s.get("contributing_factors", {})
        factor_str = ", ".join(f"{k}={v}" for k, v in factors.items()) if factors else "N/A"
        summaries.append(
            f"Customer {s['customer_no']}: RiskScore={s['risk_score']:.2f}, "
            f"Level={s['risk_level']}, Factors=[{factor_str}]"
        )

    prompt_text = f"{DIAGNOSIS_PROMPT}\n\nDiagnose these {len(summaries)} at-risk customers:\n" + "\n".join(summaries)

    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        diagnoses = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            diagnoses = json.loads(content[start:end])
        else:
            diagnoses = []

    return diagnoses
