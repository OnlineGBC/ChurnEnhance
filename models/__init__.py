# Import all models so SQLAlchemy registers them in the same metadata
from models.customer import Customer, Transaction
from models.agent_models import (
    ChurnScore, Diagnosis, Intervention,
    ICPProfile, LeadScore, FeedbackLoop, AgentRun,
)
