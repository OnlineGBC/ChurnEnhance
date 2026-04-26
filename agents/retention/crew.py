"""Retention Specialist crew — LangGraph subgraph wiring."""

from datetime import datetime
from agents.llm_config import get_llm
from agents.retention.churn_risk import score_churn_risk
from agents.retention.diagnosis import diagnose_churn
from agents.retention.intervention import select_interventions
from agents.knowledge.knowledge_store import KnowledgeStore
from agents.knowledge.feedback_loop import retention_to_market_access


def run_retention_crew(llm_model: str) -> dict:
    """Execute the full retention crew pipeline.

    1. Score churn risk (pre-filtered by SQL)
    2. Diagnose failure modes
    3. Select interventions
    4. Persist results to PostgreSQL
    5. Send feedback to market access crew
    """
    started_at = datetime.now()
    llm = get_llm(llm_model)

    # Step 1: Churn Risk Scoring
    churn_scores = score_churn_risk(llm, top_n=50)

    # Persist churn scores
    for score in churn_scores:
        try:
            KnowledgeStore.save_churn_score(
                customer_no=str(score.get("customer_no", "")),
                risk_score=float(score.get("risk_score", 0)),
                risk_level=score.get("risk_level", "low"),
                contributing_factors=score.get("contributing_factors", {}),
                recommended_action=score.get("recommended_action", ""),
                llm_model=llm_model,
            )
        except Exception:
            continue

    # Step 2: Diagnosis
    diagnoses = diagnose_churn(llm, churn_scores)

    for diag in diagnoses:
        try:
            KnowledgeStore.save_diagnosis(
                customer_no=str(diag.get("customer_no", "")),
                failure_mode=diag.get("failure_mode", ""),
                confidence=float(diag.get("confidence", 0)),
                evidence=diag.get("evidence", {}),
                suggested_interventions=diag.get("suggested_interventions", []),
                llm_model=llm_model,
            )
        except Exception:
            continue

    # Step 3: Intervention Selection
    interventions = select_interventions(llm, diagnoses)

    for intv in interventions:
        try:
            KnowledgeStore.save_intervention(
                customer_no=str(intv.get("customer_no", "")),
                intervention_type=intv.get("intervention_type", ""),
                priority=intv.get("priority", "medium"),
                message_template=intv.get("message_template", ""),
                assigned_to=intv.get("assigned_to", ""),
                llm_model=llm_model,
            )
        except Exception:
            continue

    # Step 4: Cross-crew feedback
    try:
        retention_to_market_access()
    except Exception:
        pass

    # Step 5: Log agent run
    KnowledgeStore.save_agent_run(
        crew="retention",
        llm_model=llm_model,
        status="completed",
        input_summary=f"Analyzed {len(churn_scores)} customers",
        output_summary=f"{len(churn_scores)} scores, {len(diagnoses)} diagnoses, {len(interventions)} interventions",
        tokens_used=0,
        started_at=started_at,
    )

    return {
        "churn_scores": len(churn_scores),
        "diagnoses": len(diagnoses),
        "interventions": len(interventions),
    }
