"""Retention Specialist crew — LangGraph subgraph wiring."""

import models  # noqa: F401 — register all ORM models for FK resolution
import logging
from datetime import datetime
from agents.llm_config import get_llm
from agents.retention.churn_risk import score_churn_risk
from agents.retention.diagnosis import diagnose_churn
from agents.retention.intervention import select_interventions
from agents.knowledge.knowledge_store import KnowledgeStore
from agents.knowledge.feedback_loop import retention_to_market_access

logger = logging.getLogger(__name__)


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
    logger.info(f"Churn risk scoring returned {len(churn_scores)} scores")

    # Persist churn scores
    scores_saved = 0
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
            scores_saved += 1
        except Exception as e:
            logger.error(f"Failed to save churn score for {score.get('customer_no')}: {e}")
            continue

    # Step 2: Diagnosis
    diagnoses = diagnose_churn(llm, churn_scores)
    logger.info(f"Diagnosis returned {len(diagnoses)} diagnoses")

    diag_saved = 0
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
            diag_saved += 1
        except Exception as e:
            logger.error(f"Failed to save diagnosis for {diag.get('customer_no')}: {e}")
            continue

    # Step 3: Intervention Selection
    interventions = select_interventions(llm, diagnoses)
    logger.info(f"Intervention selection returned {len(interventions)} interventions")

    intv_saved = 0
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
            intv_saved += 1
        except Exception as e:
            logger.error(f"Failed to save intervention for {intv.get('customer_no')}: {e}")
            continue

    # Step 4: Cross-crew feedback
    try:
        retention_to_market_access()
    except Exception as e:
        logger.error(f"Feedback loop error: {e}")

    # Step 5: Log agent run
    try:
        KnowledgeStore.save_agent_run(
            crew="retention",
            llm_model=llm_model,
            status="completed",
            input_summary=f"Analyzed {len(churn_scores)} customers",
            output_summary=f"{scores_saved} scores, {diag_saved} diagnoses, {intv_saved} interventions saved",
            tokens_used=0,
            started_at=started_at,
        )
    except Exception as e:
        logger.error(f"Failed to save agent run: {e}")

    return {
        "churn_scores": scores_saved,
        "diagnoses": diag_saved,
        "interventions": intv_saved,
    }
