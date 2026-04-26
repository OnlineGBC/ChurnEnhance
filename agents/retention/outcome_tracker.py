"""Outcome tracking agent — logs intervention results for future reference."""

from datetime import datetime
from models.database import get_db_session
from models.agent_models import Intervention


def update_intervention_outcome(intervention_id: int, outcome: str):
    """Update the outcome of a completed intervention."""
    db = get_db_session()
    try:
        intv = db.query(Intervention).filter_by(id=intervention_id).first()
        if intv:
            intv.outcome = outcome
            intv.status = "completed"
            intv.completed_at = datetime.now()
            db.commit()
            return True
        return False
    finally:
        db.close()


def get_intervention_success_rate() -> dict:
    """Calculate intervention success rates by type."""
    db = get_db_session()
    try:
        interventions = db.query(Intervention).filter(
            Intervention.status == "completed"
        ).all()

        if not interventions:
            return {"total": 0, "by_type": {}}

        by_type = {}
        for intv in interventions:
            t = intv.intervention_type
            if t not in by_type:
                by_type[t] = {"total": 0, "successful": 0}
            by_type[t]["total"] += 1
            if intv.outcome and "success" in intv.outcome.lower():
                by_type[t]["successful"] += 1

        return {
            "total": len(interventions),
            "by_type": {k: {**v, "rate": v["successful"] / v["total"] if v["total"] > 0 else 0}
                        for k, v in by_type.items()},
        }
    finally:
        db.close()
