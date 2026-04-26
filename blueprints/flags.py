import io
import pandas as pd
from flask import Blueprint, render_template, request, session, send_file
from sqlalchemy import func, text
from models.database import get_db_session
from models.customer import Customer, Transaction
from config.settings import Config

flags_bp = Blueprint("flags", __name__)


def _get_thresholds():
    yellow = int(session.get("yellow_flag", 30))
    red = int(session.get("red_flag", 60))
    return yellow, red


@flags_bp.route("/sales", methods=["GET", "POST"])
def sales_flags():
    if request.method == "POST":
        session["yellow_flag"] = int(request.form.get("yellow_flag", 30))
        session["red_flag"] = int(request.form.get("red_flag", 60))

    yellow_flag, red_flag = _get_thresholds()
    db = get_db_session()
    try:
        all_customers = db.query(Customer).order_by(Customer.sales_inactivity_days.desc().nullslast()).all()

        yellow_flags = [c for c in all_customers
                        if c.sales_inactivity_days is not None
                        and c.sales_inactivity_days >= yellow_flag
                        and c.sales_inactivity_days < red_flag]
        red_flags = [c for c in all_customers
                     if c.sales_inactivity_days is not None
                     and c.sales_inactivity_days > red_flag]

        return render_template("sales_flags.html",
                               yellow_flag=yellow_flag, red_flag=red_flag,
                               all_customers=all_customers,
                               yellow_flags=yellow_flags, red_flags=red_flags,
                               total_count=len(all_customers),
                               yellow_count=len(yellow_flags),
                               red_count=len(red_flags),
                               config=Config)
    finally:
        db.close()


@flags_bp.route("/sales/download/<flag_type>")
def download_sales_flag(flag_type):
    yellow_flag, red_flag = _get_thresholds()
    db = get_db_session()
    try:
        all_customers = db.query(Customer).all()
        if flag_type == "yellow":
            flagged = [c for c in all_customers
                       if c.sales_inactivity_days is not None
                       and c.sales_inactivity_days >= yellow_flag
                       and c.sales_inactivity_days < red_flag]
            filename = "YellowFlagCustomers.csv"
        else:
            flagged = [c for c in all_customers
                       if c.sales_inactivity_days is not None
                       and c.sales_inactivity_days > red_flag]
            filename = "RedFlagCustomers.csv"

        rows = [{
            "customer_no": c.customer_no,
            "customer_name": c.customer_name,
            "sales_region": c.sales_region,
            "last_transaction_date": c.last_transaction_date,
            "sales_inactivity_days": c.sales_inactivity_days,
            "churn_flag": c.churn_flag,
        } for c in flagged]
        df = pd.DataFrame(rows)
        csv_bytes = df.to_csv(index=False).encode()
        return send_file(io.BytesIO(csv_bytes), mimetype="text/csv",
                         as_attachment=True, download_name=filename)
    finally:
        db.close()


@flags_bp.route("/product", methods=["GET", "POST"])
def product_flags():
    if request.method == "POST":
        session["yellow_flag"] = int(request.form.get("yellow_flag", 30))
        session["red_flag"] = int(request.form.get("red_flag", 60))

    yellow_flag, red_flag = _get_thresholds()
    db = get_db_session()
    try:
        # Get last transaction per customer-product combo
        results = db.execute(text("""
            SELECT t.customer_no, c.customer_name, t.product, t.product_gbu,
                   MAX(t.transaction_date) as last_txn,
                   CURRENT_DATE - MAX(t.transaction_date) as inactivity_days
            FROM transactions t
            JOIN customers c ON t.customer_no = c.customer_no
            GROUP BY t.customer_no, c.customer_name, t.product, t.product_gbu
            ORDER BY inactivity_days DESC NULLS LAST
        """)).fetchall()

        all_items = [r._mapping for r in results]
        yellow_flags = [r for r in all_items
                        if r["inactivity_days"] is not None
                        and r["inactivity_days"] >= yellow_flag
                        and r["inactivity_days"] < red_flag]
        red_flags = [r for r in all_items
                     if r["inactivity_days"] is not None
                     and r["inactivity_days"] >= red_flag]

        return render_template("product_flags.html",
                               yellow_flag=yellow_flag, red_flag=red_flag,
                               yellow_flags=yellow_flags, red_flags=red_flags,
                               total_count=len(all_items),
                               yellow_count=len(yellow_flags),
                               red_count=len(red_flags),
                               config=Config)
    finally:
        db.close()


@flags_bp.route("/product/download/<flag_type>")
def download_product_flag(flag_type):
    yellow_flag, red_flag = _get_thresholds()
    db = get_db_session()
    try:
        results = db.execute(text("""
            SELECT t.customer_no, c.customer_name, t.product, t.product_gbu,
                   MAX(t.transaction_date) as last_txn,
                   CURRENT_DATE - MAX(t.transaction_date) as inactivity_days
            FROM transactions t
            JOIN customers c ON t.customer_no = c.customer_no
            GROUP BY t.customer_no, c.customer_name, t.product, t.product_gbu
        """)).fetchall()

        all_items = [dict(r._mapping) for r in results]
        if flag_type == "yellow":
            flagged = [r for r in all_items if r["inactivity_days"] is not None
                       and r["inactivity_days"] >= yellow_flag and r["inactivity_days"] < red_flag]
            filename = "ProductYellowFlagCustomers.csv"
        else:
            flagged = [r for r in all_items if r["inactivity_days"] is not None
                       and r["inactivity_days"] >= red_flag]
            filename = "ProductRedFlagCustomers.csv"

        df = pd.DataFrame(flagged)
        csv_bytes = df.to_csv(index=False).encode()
        return send_file(io.BytesIO(csv_bytes), mimetype="text/csv",
                         as_attachment=True, download_name=filename)
    finally:
        db.close()
