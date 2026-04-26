from flask import Blueprint, render_template
from sqlalchemy import desc, func, text
from models.database import get_db_session
from models.customer import Customer, Transaction
from models.agent_models import ICPProfile, LeadScore
from config.settings import Config

market_access_bp = Blueprint("market_access", __name__)


@market_access_bp.route("/")
def dashboard():
    db = get_db_session()
    try:
        icp_profiles = db.query(ICPProfile).order_by(desc(ICPProfile.created_at)).all()
        lead_scores = db.query(LeadScore).order_by(desc(LeadScore.score)).all()

        return render_template("market_access/dashboard.html",
                               icp_profiles=icp_profiles,
                               lead_scores=lead_scores,
                               config=Config)
    finally:
        db.close()


@market_access_bp.route("/<segment>")
def segment_detail(segment):
    db = get_db_session()
    try:
        lead_score = db.query(LeadScore).filter_by(segment=segment).order_by(desc(LeadScore.created_at)).first()

        # Find customers in this segment (by industry or consumables_segment)
        customers_query = db.execute(text("""
            SELECT c.customer_no, c.customer_name, c.sales_region, c.churn_flag,
                   COALESCE(SUM(t.amount), 0) as total_revenue
            FROM customers c
            LEFT JOIN transactions t ON c.customer_no = t.customer_no
            WHERE c.industry = :segment OR c.consumables_segment = :segment
               OR c.capital_segment = :segment OR c.sales_region = :segment
            GROUP BY c.customer_no, c.customer_name, c.sales_region, c.churn_flag
            ORDER BY total_revenue DESC
            LIMIT 100
        """), {"segment": segment}).fetchall()

        customers = [dict(r._mapping) for r in customers_query]

        return render_template("market_access/segment_detail.html",
                               segment=segment,
                               lead_score=lead_score,
                               customers=customers,
                               config=Config)
    finally:
        db.close()
