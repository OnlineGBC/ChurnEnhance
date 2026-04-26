from flask import Blueprint, jsonify, session
from config.settings import Config

api_bp = Blueprint("api", __name__)


@api_bp.route("/retention/run", methods=["POST"])
def run_retention():
    llm_model = session.get("llm_model", Config.DEFAULT_LLM)
    try:
        from agents.retention.crew import run_retention_crew
        result = run_retention_crew(llm_model)
        return jsonify({"status": "completed", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@api_bp.route("/market-access/run", methods=["POST"])
def run_market_access():
    llm_model = session.get("llm_model", Config.DEFAULT_LLM)
    try:
        from agents.market_access.crew import run_market_access_crew
        result = run_market_access_crew(llm_model)
        return jsonify({"status": "completed", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


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
