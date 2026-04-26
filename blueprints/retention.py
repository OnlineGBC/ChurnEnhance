from flask import Blueprint, render_template
from sqlalchemy import desc
from models.database import get_db_session
from models.customer import Customer, Transaction
from models.agent_models import ChurnScore, Diagnosis, Intervention
from config.settings import Config

retention_bp = Blueprint("retention", __name__)


@retention_bp.route("/")
def dashboard():
    db = get_db_session()
    try:
        churn_scores = db.query(ChurnScore).order_by(desc(ChurnScore.risk_score)).limit(100).all()
        diagnoses = db.query(Diagnosis).order_by(desc(Diagnosis.created_at)).limit(20).all()
        interventions = db.query(Intervention).order_by(desc(Intervention.created_at)).limit(50).all()

        return render_template("retention/dashboard.html",
                               churn_scores=churn_scores,
                               diagnoses=diagnoses,
                               interventions=interventions,
                               config=Config)
    finally:
        db.close()


@retention_bp.route("/<customer_no>")
def customer_detail(customer_no):
    db = get_db_session()
    try:
        customer = db.query(Customer).filter_by(customer_no=str(customer_no)).first()
        if not customer:
            return render_template("retention/customer_detail.html",
                                   customer=None, config=Config), 404

        transactions = (db.query(Transaction)
                        .filter_by(customer_no=str(customer_no))
                        .order_by(desc(Transaction.transaction_date))
                        .limit(50).all())

        latest_score = (db.query(ChurnScore)
                        .filter_by(customer_no=str(customer_no))
                        .order_by(desc(ChurnScore.created_at))
                        .first())

        latest_diagnosis = (db.query(Diagnosis)
                            .filter_by(customer_no=str(customer_no))
                            .order_by(desc(Diagnosis.created_at))
                            .first())

        return render_template("retention/customer_detail.html",
                               customer=customer,
                               transactions=transactions,
                               latest_score=latest_score,
                               latest_diagnosis=latest_diagnosis,
                               config=Config)
    finally:
        db.close()
