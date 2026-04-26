from datetime import datetime, timedelta
from flask import Blueprint, jsonify, session
from config.settings import Config
from agents.knowledge.knowledge_store import KnowledgeStore

api_bp = Blueprint("api", __name__)

# A "running" row older than this is treated as dead (server crashed/restarted).
STALE_RUN_MINUTES = 10


@api_bp.route("/retention/run", methods=["POST"])
def run_retention():
    llm_model = session.get("llm_model", Config.DEFAULT_LLM)
    KnowledgeStore.reset_retention_outputs()
    run_id = KnowledgeStore.start_agent_run(
        crew="retention", llm_model=llm_model,
        input_summary="Top 50 customers by churn risk",
    )
    try:
        from agents.retention.crew import run_retention_crew
        result = run_retention_crew(llm_model)
        KnowledgeStore.complete_agent_run(
            run_id, status="completed",
            output_summary=(
                f"{result['churn_scores']} scores, {result['diagnoses']} diagnoses, "
                f"{result['interventions']} interventions"
            ),
        )
        return jsonify({"status": "completed", "result": result})
    except Exception as e:
        KnowledgeStore.complete_agent_run(run_id, status="failed", output_summary=str(e))
        return jsonify({"status": "error", "error": str(e)}), 500


@api_bp.route("/market-access/run", methods=["POST"])
def run_market_access():
    llm_model = session.get("llm_model", Config.DEFAULT_LLM)
    KnowledgeStore.reset_market_access_outputs()
    run_id = KnowledgeStore.start_agent_run(
        crew="market_access", llm_model=llm_model,
        input_summary="Full market access analysis",
    )
    try:
        from agents.market_access.crew import run_market_access_crew
        result = run_market_access_crew(llm_model)
        KnowledgeStore.complete_agent_run(
            run_id, status="completed",
            output_summary=(
                f"{result['icp_profiles']} ICP profiles, {result['lead_scores']} lead scores, "
                f"{result['campaigns']} campaigns"
            ),
        )
        return jsonify({"status": "completed", "result": result})
    except Exception as e:
        KnowledgeStore.complete_agent_run(run_id, status="failed", output_summary=str(e))
        return jsonify({"status": "error", "error": str(e)}), 500


@api_bp.route("/runs/active")
def get_active_runs():
    """Currently running agent_runs, excluding stale rows from crashed servers."""
    from models.database import get_db_session
    from models.agent_models import AgentRun
    cutoff = datetime.now() - timedelta(minutes=STALE_RUN_MINUTES)
    db = get_db_session()
    try:
        rows = (
            db.query(AgentRun)
            .filter(AgentRun.status == "running")
            .filter(AgentRun.completed_at.is_(None))
            .filter(AgentRun.started_at >= cutoff)
            .order_by(AgentRun.started_at.desc())
            .all()
        )
        return jsonify([{
            "id": r.id,
            "crew": r.crew,
            "llm_model": r.llm_model,
            "started_at": r.started_at.isoformat() if r.started_at else None,
        } for r in rows])
    finally:
        db.close()


@api_bp.route("/retention/scores")
def get_churn_scores():
    from models.database import get_db_session
    from models.agent_models import ChurnScore
    db = get_db_session()
    try:
        scores = db.query(ChurnScore).order_by(ChurnScore.risk_score.desc()).limit(100).all()
        return jsonify([{
            "customer_no": s.customer_no,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "contributing_factors": s.contributing_factors,
            "recommended_action": s.recommended_action,
        } for s in scores])
    finally:
        db.close()


@api_bp.route("/market-access/profiles")
def get_icp_profiles():
    from models.database import get_db_session
    from models.agent_models import ICPProfile
    db = get_db_session()
    try:
        profiles = db.query(ICPProfile).order_by(ICPProfile.created_at.desc()).all()
        return jsonify([{
            "segment_name": p.segment_name,
            "industry": p.industry,
            "product_gbu": p.product_gbu,
            "geography": p.geography,
            "ltv_estimate": p.ltv_estimate,
            "acquisition_priority": p.acquisition_priority,
        } for p in profiles])
    finally:
        db.close()
