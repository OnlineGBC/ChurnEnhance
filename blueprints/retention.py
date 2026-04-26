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
        # Join customer name into churn scores
        churn_scores = (db.query(ChurnScore, Customer.customer_name)
                        .outerjoin(Customer, ChurnScore.customer_no == Customer.customer_no)
                        .order_by(desc(ChurnScore.risk_score))
                        .limit(100).all())

        # Build diagnosis lookup keyed by customer_no
        diag_results = (db.query(Diagnosis, Customer.customer_name)
                        .outerjoin(Customer, Diagnosis.customer_no == Customer.customer_no)
                        .order_by(desc(Diagnosis.created_at))
                        .all())
        diagnoses_by_customer = {}
        for diag, cust_name in diag_results:
            if diag.customer_no not in diagnoses_by_customer:
                diagnoses_by_customer[diag.customer_no] = diag

        # Join customer name into interventions
        interventions = (db.query(Intervention, Customer.customer_name)
                         .outerjoin(Customer, Intervention.customer_no == Customer.customer_no)
                         .order_by(desc(Intervention.created_at))
                         .limit(50).all())

        return render_template("retention/dashboard.html",
                               churn_scores=churn_scores,
                               diagnoses_by_customer=diagnoses_by_customer,
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
