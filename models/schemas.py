from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChurnScoreSchema(BaseModel):
    customer_no: str
    risk_score: float
    risk_level: str
    contributing_factors: dict
    recommended_action: str

    class Config:
        from_attributes = True


class DiagnosisSchema(BaseModel):
    customer_no: str
    failure_mode: str
    confidence: float
    evidence: dict
    suggested_interventions: list

    class Config:
        from_attributes = True


class InterventionSchema(BaseModel):
    customer_no: str
    intervention_type: str
    priority: str
    message_template: str
    assigned_to: Optional[str] = None

    class Config:
        from_attributes = True


class ICPProfileSchema(BaseModel):
    segment_name: str
    industry: Optional[str] = None
    revenue_min: Optional[float] = None
    revenue_max: Optional[float] = None
    product_gbu: Optional[str] = None
    geography: Optional[str] = None
    npi_density: Optional[str] = None
    ltv_estimate: Optional[float] = None
    acquisition_priority: Optional[str] = None

    class Config:
        from_attributes = True


class LeadScoreSchema(BaseModel):
    segment: str
    score: float
    rationale: str
    estimated_ltv: Optional[float] = None
    recommended_channel: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    customer_no: str
    customer_name: Optional[str] = None
    industry: Optional[str] = None
    sales_region: Optional[str] = None
    last_transaction_date: Optional[datetime] = None
    sales_inactivity_days: Optional[int] = None
    churn_flag: Optional[str] = None
    total_revenue: Optional[float] = None
    total_transactions: Optional[int] = None

    class Config:
        from_attributes = True


class AgentRequest(BaseModel):
    crew: str
    llm_model: str
    customer_no: Optional[str] = None
    segment: Optional[str] = None


class AgentResponse(BaseModel):
    status: str
    crew: str
    results: dict
    tokens_used: Optional[int] = None
