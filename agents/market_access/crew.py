"""Market Access crew — full pipeline execution."""

from datetime import datetime
from agents.llm_config import get_llm
from agents.market_access.market_intel import analyze_market_intel
from agents.market_access.icp import build_icp_profiles
from agents.market_access.lead_scoring import score_leads
from agents.market_access.revenue_model import model_revenue
from agents.market_access.campaign import plan_campaigns
from agents.knowledge.knowledge_store import KnowledgeStore
from agents.knowledge.feedback_loop import market_access_to_retention


def run_market_access_crew(llm_model: str) -> dict:
    """Execute the full market access crew pipeline.

    1. Market intelligence analysis
    2. Build ICP profiles
    3. Score leads/segments
    4. Model revenue projections
    5. Plan campaigns
    6. Persist results and send feedback
    """
    started_at = datetime.now()
    llm = get_llm(llm_model)

    # Step 1: Market Intelligence
    market_intel = analyze_market_intel(llm)

    # Step 2: ICP Profiles
    icp_profiles = build_icp_profiles(llm, market_intel)

    for profile in icp_profiles:
        try:
            KnowledgeStore.save_icp_profile(profile, llm_model)
        except Exception:
            continue

    # Step 3: Lead Scoring
    lead_scores = score_leads(llm, icp_profiles)

    for score in lead_scores:
        try:
            KnowledgeStore.save_lead_score(score, llm_model)
        except Exception:
            continue

    # Step 4: Revenue Model
    revenue_projection = model_revenue(llm)

    # Step 5: Campaigns
    campaigns = plan_campaigns(llm, icp_profiles, lead_scores)

    # Step 6: Cross-crew feedback
    try:
        market_access_to_retention()
    except Exception:
        pass

    # Log agent run
    KnowledgeStore.save_agent_run(
        crew="market_access",
        llm_model=llm_model,
        status="completed",
        input_summary="Full market access analysis",
        output_summary=(
            f"{len(icp_profiles)} ICP profiles, {len(lead_scores)} lead scores, "
            f"{len(campaigns)} campaigns"
        ),
        tokens_used=0,
        started_at=started_at,
    )

    return {
        "market_intel": market_intel,
        "icp_profiles": len(icp_profiles),
        "lead_scores": len(lead_scores),
        "revenue_projection": revenue_projection,
        "campaigns": len(campaigns),
    }
