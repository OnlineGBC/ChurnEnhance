"""Intervention selection agent — maps diagnoses to actions."""

import json
from agents.retention.prompts import INTERVENTION_PROMPT


def select_interventions(llm, diagnoses: list) -> list:
    """Select interventions based on diagnoses.

    Maps failure modes to specific actions with priority and assignment.
    """
    if not diagnoses:
        return []

    summaries = []
    for d in diagnoses[:30]:
        interventions_str = ", ".join(d.get("suggested_interventions", []))
        summaries.append(
            f"Customer {d['customer_no']}: FailureMode={d['failure_mode']}, "
            f"Confidence={d.get('confidence', 0):.2f}, "
            f"Suggestions=[{interventions_str}]"
        )

    prompt_text = f"{INTERVENTION_PROMPT}\n\nSelect interventions for these diagnoses:\n" + "\n".join(summaries)

    response = llm.invoke(prompt_text)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        interventions = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            interventions = json.loads(content[start:end])
        else:
            interventions = []

    return interventions
