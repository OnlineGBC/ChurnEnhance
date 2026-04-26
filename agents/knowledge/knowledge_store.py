"""Agent output persistence — save/load results to PostgreSQL."""

from datetime import datetime
from models.database import get_db_session
import models  # noqa: F401 — register all ORM models for FK resolution
from models.agent_models import ChurnScore, Diagnosis, Intervention, ICPProfile, LeadScore, AgentRun, FeedbackLoop


class KnowledgeStore:
    """Persists agent outputs to PostgreSQL."""

    @staticmethod
    def save_churn_score(customer_no: str, risk_score: float, risk_level: str,
                         contributing_factors: dict, recommended_action: str, llm_model: str):
        db = get_db_session()
        try:
            score = ChurnScore(
                customer_no=str(customer_no),
                risk_score=risk_score,
                risk_level=risk_level,
                contributing_factors=contributing_factors,
                recommended_action=recommended_action,
                llm_model=llm_model,
            )
            db.add(score)
            db.commit()
            return score.id
        finally:
            db.close()

    @staticmethod
    def save_diagnosis(customer_no: str, failure_mode: str, confidence: float,
                       evidence: dict, suggested_interventions: list, llm_model: str):
        db = get_db_session()
        try:
            diag = Diagnosis(
                customer_no=str(customer_no),
                failure_mode=failure_mode,
                confidence=confidence,
                evidence=evidence,
                suggested_interventions=suggested_interventions,
                llm_model=llm_model,
            )
            db.add(diag)
            db.commit()
            return diag.id
        finally:
            db.close()

    @staticmethod
    def save_intervention(customer_no: str, intervention_type: str, priority: str,
                          message_template: str, assigned_to: str, llm_model: str):
        db = get_db_session()
        try:
            intv = Intervention(
                customer_no=str(customer_no),
                intervention_type=intervention_type,
                priority=priority,
                message_template=message_template,
                assigned_to=assigned_to,
                llm_model=llm_model,
            )
            db.add(intv)
            db.commit()
            return intv.id
        finally:
            db.close()

    @staticmethod
    def save_icp_profile(data: dict, llm_model: str):
        db = get_db_session()
        try:
            profile = ICPProfile(
                segment_name=data.get("segment_name"),
                industry=data.get("industry"),
                revenue_min=data.get("revenue_min"),
                revenue_max=data.get("revenue_max"),
                product_gbu=data.get("product_gbu"),
                geography=data.get("geography"),
                npi_density=data.get("npi_density"),
                ltv_estimate=data.get("ltv_estimate"),
                acquisition_priority=data.get("acquisition_priority"),
                llm_model=llm_model,
            )
            db.add(profile)
            db.commit()
            return profile.id
        finally:
            db.close()

    @staticmethod
    def save_lead_score(data: dict, llm_model: str):
        db = get_db_session()
        try:
            score = LeadScore(
                segment=data.get("segment"),
                score=data.get("score"),
                rationale=data.get("rationale"),
                estimated_ltv=data.get("estimated_ltv"),
                recommended_channel=data.get("recommended_channel"),
                llm_model=llm_model,
            )
            db.add(score)
            db.commit()
            return score.id
        finally:
            db.close()

    @staticmethod
    def save_agent_run(crew: str, llm_model: str, status: str,
                       input_summary: str, output_summary: str,
                       tokens_used: int, started_at: datetime, completed_at: datetime = None):
        db = get_db_session()
        try:
            run = AgentRun(
                crew=crew,
                llm_model=llm_model,
                status=status,
                input_summary=input_summary,
                output_summary=output_summary,
                tokens_used=tokens_used,
                started_at=started_at,
                completed_at=completed_at or datetime.now(),
            )
            db.add(run)
            db.commit()
            return run.id
        finally:
            db.close()

    @staticmethod
    def save_feedback(source_crew: str, target_crew: str,
                      insight_type: str, insight_data: dict):
        db = get_db_session()
        try:
            fb = FeedbackLoop(
                source_crew=source_crew,
                target_crew=target_crew,
                insight_type=insight_type,
                insight_data=insight_data,
            )
            db.add(fb)
            db.commit()
            return fb.id
        finally:
            db.close()
