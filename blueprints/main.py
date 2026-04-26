import os
import io
import pandas as pd
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, send_file
from sqlalchemy import func, text
from models.database import get_db_session
from models.customer import Customer, Transaction
from models.agent_models import AgentRun
from config.settings import Config

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    db = get_db_session()
    try:
        stats = {
            "customer_count": db.query(func.count(Customer.customer_no)).scalar() or 0,
            "red_count": db.query(func.count(Customer.customer_no)).filter(Customer.churn_flag == "Red").scalar() or 0,
            "yellow_count": db.query(func.count(Customer.customer_no)).filter(Customer.churn_flag == "Yellow").scalar() or 0,
            "agent_runs": db.query(func.count(AgentRun.id)).scalar() or 0,
        }

        recent_runs = db.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(10).all()

        churn_dist = db.execute(
            text("SELECT churn_flag as flag, COUNT(*) as count FROM customers GROUP BY churn_flag ORDER BY count DESC")
        ).fetchall()
        churn_distribution = [{"flag": r.flag, "count": r.count} for r in churn_dist]

        return render_template("index.html", stats=stats, recent_runs=recent_runs,
                               churn_distribution=churn_distribution, config=Config)
    finally:
        db.close()


@main_bp.route("/upload", methods=["GET", "POST"])
def upload():
    results = None
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith(".csv"):
            flash("Please upload a valid CSV file.", "error")
            return redirect(url_for("main.upload"))

        session["yellow_flag"] = int(request.form.get("yellow_flag", 30))
        session["red_flag"] = int(request.form.get("red_flag", 60))

        try:
            df = pd.read_csv(file, low_memory=False)
            from services.data_loader import load_uploaded_csv
            df_full, df_not_found, df_valid, df_valid_cust_prod = load_uploaded_csv(df)

            # Store in session for download
            session["upload_not_found"] = df_not_found.to_csv(index=False)

            results = {
                "valid_count": len(df_valid),
                "not_found_count": len(df_not_found),
            }
            flash(f"Processed {len(df_full)} rows: {len(df_valid)} valid, {len(df_not_found)} not found.", "success")
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "error")

    return render_template("upload.html", results=results, config=Config)


@main_bp.route("/reload-enriched", methods=["POST"])
def reload_enriched():
    try:
        from services.data_loader import load_enriched_csv
        cust_count, txn_count = load_enriched_csv()
        flash(f"Reloaded {cust_count} customers and {txn_count} transactions from enriched dataset.", "success")
    except Exception as e:
        flash(f"Error reloading data: {str(e)}", "error")
    return redirect(url_for("main.upload"))


@main_bp.route("/download/not-found")
def download_not_found():
    csv_data = session.get("upload_not_found")
    if not csv_data:
        flash("No data available for download.", "error")
        return redirect(url_for("main.upload"))
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="CustIdentifierNotFound.csv",
    )


@main_bp.route("/set-llm", methods=["POST"])
def set_llm():
    model = request.form.get("llm_model", Config.DEFAULT_LLM)
    if model in Config.LLM_CHOICES:
        session["llm_model"] = model
    return redirect(request.referrer or url_for("main.index"))
