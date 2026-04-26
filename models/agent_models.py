from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from models.database import Base


class ChurnScore(Base):
    __tablename__ = "churn_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_no = Column(String, ForeignKey("customers.customer_no"))
    risk_score = Column(Float)
    risk_level = Column(String)
    contributing_factors = Column(JSONB)
    recommended_action = Column(Text)
    llm_model = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_no = Column(String, ForeignKey("customers.customer_no"))
    failure_mode = Column(String)
    confidence = Column(Float)
    evidence = Column(JSONB)
    suggested_interventions = Column(JSONB)
    llm_model = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_no = Column(String, ForeignKey("customers.customer_no"))
    intervention_type = Column(String)
    priority = Column(String)
    message_template = Column(Text)
    assigned_to = Column(String)
    status = Column(String, default="pending")
    outcome = Column(String)
    llm_model = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)


class ICPProfile(Base):
    __tablename__ = "icp_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_name = Column(String)
    industry = Column(String)
    revenue_min = Column(Float)
    revenue_max = Column(Float)
    product_gbu = Column(String)
    geography = Column(String)
    npi_density = Column(String)
    ltv_estimate = Column(Float)
    acquisition_priority = Column(String)
    llm_model = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String)
    score = Column(Float)
    rationale = Column(Text)
    estimated_ltv = Column(Float)
    recommended_channel = Column(String)
    llm_model = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class FeedbackLoop(Base):
    __tablename__ = "feedback_loop"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_crew = Column(String)
    target_crew = Column(String)
    insight_type = Column(String)
    insight_data = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crew = Column(String)
    llm_model = Column(String)
    status = Column(String)
    input_summary = Column(Text)
    output_summary = Column(Text)
    tokens_used = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
