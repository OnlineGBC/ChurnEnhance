# CustomerChurn AI — Multi-Agent Churn/Access System

## Overview

CustomerChurn AI is a multi-agent system for Laborie Medical Technologies that predicts customer churn, diagnoses causes, recommends retention interventions, builds ideal customer profiles, and identifies market expansion opportunities.

The system is built on **Flask + Tailwind CSS** (migrated from Streamlit v1) with **PostgreSQL** persistence and **LangGraph**-based AI agents powered by user-selectable LLMs.

---

## Why Multi-Agent — Not Just AI

A common question: *"Isn't this just an app that calls an AI model?"* No. Here's the difference, and why it matters.

### What "Just AI" Looks Like

A typical AI application makes a single call to a language model: you give it data, it gives you an answer. One prompt in, one response out. No memory, no multi-step reasoning, no coordination between components. Think of asking ChatGPT a question — that's "just AI."

### What Makes an Agent Different

An **agent** is an AI system that:

1. **Receives a goal**, not just a question
2. **Decides what steps to take** to achieve that goal
3. **Uses tools** to interact with the outside world (databases, APIs, files)
4. **Observes the results** of its actions
5. **Decides what to do next** based on those results

The simplest way to put it: **a regular LLM is a brain in a jar. An agent is a brain with hands.** It can reach out, grab information, do things, and adjust its approach based on what happens.

### How CustomerChurn AI Is Agentic

#### 1. Multiple Specialized Agents Working as a Team ("Crews")

Instead of one AI doing everything, there are **two crews** of agents, each with a specific job:

- **Retention Specialist Crew** — Figures out which customers are leaving and what to do about it
- **Market Access Crew** — Finds new growth opportunities to replace lost revenue

Think of it like departments in a company. Sales and Marketing are separate teams, but they share information with each other.

#### 2. Multi-Step Reasoning Pipelines

Each crew runs a **chain of steps** where each step's output feeds into the next. This is fundamentally different from a single AI call.

**Retention Crew — 3-Step Reasoning Chain:**

| Step | What It Does | Human Analogy |
|------|-------------|---------------|
| **Churn Risk Scoring** | Examines 50 customers' data and assigns each a 0–1 risk score with contributing factors | A doctor reading lab results |
| **Diagnosis** | Takes the high-risk scores and determines *why* — product fit? pricing? service quality? competitive displacement? | The doctor diagnosing the disease |
| **Intervention Selection** | Based on the diagnosis, picks the right action — sales outreach? executive engagement? loyalty program? Assigns it to the right team member | The doctor writing a prescription |

Each step is a separate LLM call that **reasons about the previous step's output**. Step 3 cannot happen without Step 2, which cannot happen without Step 1. That sequential reasoning chain is what makes it agentic — the AI is "thinking through" a problem in stages, not just answering once.

**Market Access Crew — 5-Step Reasoning Chain:**

| Step | What It Does |
|------|-------------|
| **Market Intelligence** | Analyzes revenue concentration, under-penetrated regions, and product gaps |
| **ICP Profile Building** | Builds Ideal Customer Profiles, actively *excluding* patterns from churned customers |
| **Lead Scoring** | Scores each market segment for expansion opportunity (0–1) with recommended sales channels |
| **Revenue Modeling** | Projects 12-month revenue by segment with retention-rate adjustments |
| **Campaign Planning** | Designs outreach strategies with territory assignments and ROI estimates |

#### 3. Cross-Crew Feedback Loops

This is the most agentic part of the system. **The two crews communicate with each other:**

- **Retention → Market Access**: "Here are the patterns of customers who churned (industry, size, region)." The Market Access crew then uses this to **exclude** those bad patterns when building Ideal Customer Profiles. It learns from the other crew's findings.

- **Market Access → Retention**: "Here are our top-performing segments and their revenue benchmarks." The Retention crew uses this to prioritize which at-risk customers are most worth saving.

This is like two departments in a company having a weekly sync meeting — each team adjusts its strategy based on what the other learned. The feedback is stored persistently and used in subsequent runs.

#### 4. An Orchestrator That Routes Decisions

The Chat interface does not just call one AI model. It has a **router agent** that:

1. Reads your natural language question
2. **Decides** which action to take — is this about a specific customer? churn risk? market opportunities? a general overview?
3. Extracts relevant parameters (customer numbers, segment names) from your question
4. Pulls the right data from PostgreSQL based on that decision
5. Generates a contextual answer using that data

The router is making a **judgment call** about intent and routing — that's agency, not just text generation.

#### 5. Tool Use — Agents That Take Actions

The agents have **tools** — functions they can call to interact with the real world:

| Tool | What It Does |
|------|-------------|
| `get_high_risk_customers()` | Queries PostgreSQL for customers sorted by inactivity |
| `get_customer_detail()` | Pulls a customer's full profile with transaction summary |
| `get_region_performance()` | Aggregates regional metrics including churn counts |
| `get_churned_archetypes()` | Finds patterns in lost customers for ICP exclusion |
| `get_revenue_by_segment()` | Aggregates revenue data by industry segment |
| `get_product_performance()` | Analyzes product-level sales metrics |

An agent with tools is fundamentally different from a bare language model. It can **take actions** to gather information it needs, not just process what you hand it.

#### 6. Persistent Memory Across Runs

Every agent output — risk scores, diagnoses, interventions, ICP profiles, lead scores, feedback insights — gets **saved to PostgreSQL**. When crews run again or a user asks a chat question, the system builds on previous results. It has institutional memory, not just session context.

### Summary: AI vs. Multi-Agent

| Trait | Just AI | CustomerChurn AI (Multi-Agent) |
|-------|---------|-------------------------------|
| **Steps** | One question → one answer | Multi-step pipelines: Score → Diagnose → Intervene |
| **Agents** | One model | Two specialized crews + a routing orchestrator |
| **Communication** | None | Crews send feedback to each other bidirectionally |
| **Tools** | None | Agents query databases, pull customer data, aggregate metrics |
| **Decisions** | User decides what to ask | Router agent decides which crew/action to invoke |
| **Memory** | Stateless per call | All outputs persist in PostgreSQL across runs |
| **Reasoning** | Single inference | Sequential multi-step reasoning chains (3–5 steps per crew) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Web App                         │
│                  (port 8503)                             │
│  ┌─────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐ │
│  │Dashboard│ │Sales/Prod │ │Retention  │ │Market    │  │
│  │  Index  │ │  Flags    │ │ Dashboard │ │Access    │  │
│  └─────────┘ └───────────┘ └─────┬─────┘ └────┬─────┘  │
│                                  │             │        │
│  ┌───────────────────────────────┴─────────────┘        │
│  │            API Layer (blueprints/api.py)              │
│  └───────────────────────┬──────────────────┘           │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                   Agent Orchestrator                     │
│              (agents/orchestrator.py)                    │
│                          │                              │
│          ┌───────────────┴───────────────┐              │
│          ▼                               ▼              │
│  ┌───────────────┐            ┌──────────────────┐     │
│  │  Retention    │  feedback  │  Market Access    │     │
│  │  Specialist   │◄──────────►│  Crew            │     │
│  │  Crew         │   loop     │                  │     │
│  ├───────────────┤            ├──────────────────┤     │
│  │• Churn Risk   │            │• Market Intel    │     │
│  │• Diagnosis    │            │• ICP Builder     │     │
│  │• Intervention │            │• Lead Scoring    │     │
│  │• Outcome Track│            │• Revenue Model   │     │
│  └───────┬───────┘            │• Campaign Planner│     │
│          │                    └────────┬─────────┘     │
│          └────────────┬─���─────────────┘                 │
│                       ▼                                 │
│            ┌──────────────────┐                         │
│            │  Knowledge Layer │                         │
│            │• Data Access     │                         │
│            │• Knowledge Store │                         │
│            │• Feedback Loop   │                         │
│            └────────┬─────────┘                         │
└─────────────────────┼───────────────────────────────────┘
                      │
              ┌───────▼────────┐
              │  PostgreSQL    │
              │  customerchurn │
              │  (9 tables)    │
              └────────────────┘
```

---

## Technology Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| Web Framework | Flask 3.x | App factory pattern, 6 blueprints |
| UI Styling | Tailwind CSS (CDN) | Gradient sidebar, card-shine hover effects, colored top borders, brand teal #709f9a |
| Interactivity | HTMX + Fetch API | Partial page updates, chat streaming |
| Database | PostgreSQL 14 | Local on VM, 9 tables |
| ORM | SQLAlchemy 2.x | Declarative models, session management |
| Agent Framework | LangGraph / LangChain | Crew-based agent pipelines |
| LLM Providers | OpenAI + Anthropic | User-selectable at runtime |
| Validation | Pydantic 2.x | Agent I/O schemas |
| Config | python-dotenv | API keys + DB config from .env |

---

## UI Design

The interface uses a polished design with the following visual elements:

- **Sidebar**: Gradient background (teal-dark → teal-deeper) with hover/active indicators using left border accents
- **Dashboard cards**: Colored top borders (teal for totals, red for red flags, amber for yellow flags, indigo for agent runs) with hover shadow transitions
- **Card-shine effect**: All panels use a custom `card-shine` class that adds subtle hover shadow elevation
- **Header bar**: Subtle gradient from white to off-white with green tint
- **Retention dashboard**: Unified full-width churn scores table with inline customer names, diagnoses, and confidence columns (no separate diagnoses panel)
- **Intervention queue**: Includes customer names alongside customer numbers
- **Color-coded badges**: Risk levels, flag status, and priorities use consistent semantic colors throughout
- **System branding**: "Multi-Agent Churn/Access System" in sidebar footer

---

## LLM Configuration

Users select the LLM model from a dropdown in the top navigation bar. The selection is stored in the Flask session.

| Dropdown Label | Provider | Model ID | Key |
|----------------|----------|----------|-----|
| OpenAI GPT-5.5 | OpenAI | `gpt-5.5` | `gpt-5.5` |
| Claude Sonnet | Anthropic | `claude-sonnet-4-6` | `claude-sonnet-4-6` |
| Claude Opus (more expensive) | Anthropic | `claude-opus-4-7` | `claude-opus-4-7` |

**Default model:** `claude-sonnet-4-6`

**LLM Parameters:**
- Temperature: 0.1
- Max Tokens: 16384

API keys are stored in `.env` and loaded via `python-dotenv`.

---

## PostgreSQL Database

**Connection Details:**
- Host: `localhost`
- Database: `customerchurn`
- User: `churnapp`
- Password: `churnapp123`
- URI: `postgresql://churnapp:churnapp123@localhost/customerchurn`

### Schema (9 Tables)

#### Core Data Tables

**customers** — 2,135 rows (loaded from enriched CSV)
| Column | Type | Description |
|--------|------|-------------|
| customer_no | VARCHAR (PK) | Customer identifier |
| customer_name | VARCHAR | Company name |
| industry | VARCHAR | e.g., "Healthcare - Hospital" |
| sales_region | VARCHAR | e.g., "Great Lakes" |
| st_state | VARCHAR | Ship-to state |
| st_city | VARCHAR | Ship-to city |
| consumables_segment | VARCHAR | USS consumables segment |
| capital_segment | VARCHAR | USS capital segment |
| npi_tercile | VARCHAR | NPI density tercile |
| account_age_months | INTEGER | Months since first transaction |
| csat_score | FLOAT | Customer satisfaction score |
| customer_profile | VARCHAR | "active" or other status |
| first_transaction_date | DATE | First purchase date |
| last_transaction_date | DATE | Most recent purchase date |
| sales_inactivity_days | INTEGER | Days since last transaction |
| churn_flag | VARCHAR | "Red", "Yellow", or NULL |

**transactions** — 26,597 rows
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | Auto-increment ID |
| sales_ta_id | INTEGER | Sales transaction ID |
| customer_no | VARCHAR (FK) | References customers |
| product | VARCHAR | Product name |
| product_gbu | VARCHAR | Product business unit |
| product_main_grp | VARCHAR | Product main group |
| transaction_date | DATE | Transaction date |
| quantity | FLOAT | Quantity ordered |
| amount | FLOAT | Transaction amount ($) |
| gross_margin | FLOAT | Gross margin ($) |
| cost | FLOAT | Cost ($) |
| invoice_type | VARCHAR | "Invoice" or other |
| sales_region | VARCHAR | Sales region |
| sales_territory | VARCHAR | Sales territory |
| sales_rep | VARCHAR | Sales representative |

#### Agent Output Tables

**churn_scores** — AI-generated churn risk assessments
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| customer_no | VARCHAR (FK) | |
| risk_score | FLOAT | 0.0–1.0 |
| risk_level | VARCHAR | "low", "medium", "high" |
| contributing_factors | JSONB | Factor name → description |
| recommended_action | TEXT | Suggested next step |
| llm_model | VARCHAR | Model used to generate |
| created_at | TIMESTAMP | Auto-set |

**diagnoses** — Failure mode identification
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| customer_no | VARCHAR (FK) | |
| failure_mode | VARCHAR | e.g., "competitive displacement" |
| confidence | FLOAT | 0.0–1.0 |
| evidence | JSONB | Supporting data points |
| suggested_interventions | JSONB | Array of suggestions |
| llm_model | VARCHAR | |
| created_at | TIMESTAMP | |

**interventions** — Retention action queue
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| customer_no | VARCHAR (FK) | |
| intervention_type | VARCHAR | "sales_outreach", "pricing_review", etc. |
| priority | VARCHAR | "high", "medium", "low" |
| message_template | TEXT | Personalized outreach message |
| assigned_to | VARCHAR | "Sales Rep", "Account Manager", etc. |
| status | VARCHAR | "pending", "in_progress", "completed" |
| outcome | VARCHAR | Result after completion |
| llm_model | VARCHAR | |
| created_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |

**icp_profiles** — Ideal Customer Profiles
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| segment_name | VARCHAR | Profile name |
| industry | VARCHAR | Target industry |
| revenue_min | FLOAT | Min revenue range |
| revenue_max | FLOAT | Max revenue range |
| product_gbu | VARCHAR | Primary product category |
| geography | VARCHAR | Target region |
| npi_density | VARCHAR | "high", "medium", "low" |
| ltv_estimate | FLOAT | Estimated lifetime value |
| acquisition_priority | VARCHAR | "high", "medium", "low" |
| llm_model | VARCHAR | |
| created_at | TIMESTAMP | |

**lead_scores** — Segment opportunity scores
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| segment | VARCHAR | Segment name |
| score | FLOAT | 0.0–1.0 |
| rationale | TEXT | Scoring rationale |
| estimated_ltv | FLOAT | Projected LTV |
| recommended_channel | VARCHAR | "direct_sales", "distributor", etc. |
| llm_model | VARCHAR | |
| created_at | TIMESTAMP | |

**feedback_loop** — Cross-crew insights
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| source_crew | VARCHAR | "retention" or "market_access" |
| target_crew | VARCHAR | |
| insight_type | VARCHAR | e.g., "churned_archetypes" |
| insight_data | JSONB | Insight payload |
| created_at | TIMESTAMP | |

**agent_runs** — Execution log
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL (PK) | |
| crew | VARCHAR | "retention" or "market_access" |
| llm_model | VARCHAR | |
| status | VARCHAR | "completed", "running", "error" |
| input_summary | TEXT | What was analyzed |
| output_summary | TEXT | Results summary |
| tokens_used | INTEGER | LLM token consumption |
| started_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |

---

## Directory Structure

```
/home/azureuser/CustomerChurn/
│
├── app.py                          # Flask entry point (port 8503)
├── wsgi.py                         # WSGI entry for gunicorn
├── requirements.txt                # Python dependencies
├── .env                            # API keys + DB config (gitignored)
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # Flask config, DB URI, LLM choices
│
├── models/
│   ├── __init__.py
│   ├── database.py                 # SQLAlchemy engine, session, Base
│   ├── customer.py                 # Customer, Transaction ORM models
│   ├── agent_models.py             # ChurnScore, Diagnosis, etc. ORM models
│   └── schemas.py                  # Pydantic schemas for agent I/O
│
├── agents/
│   ├── __init__.py
│   ├── llm_config.py               # get_llm(choice) → ChatModel factory
│   ├── state.py                    # LangGraph AgentState TypedDict
│   ├── orchestrator.py             # Chat router + context builder
│   │
│   ├── retention/                  # Retention Specialist Crew
│   │   ├── __init__.py
│   │   ├── crew.py                 # run_retention_crew() pipeline
│   │   ├── churn_risk.py           # Churn risk scoring (SQL pre-filter → LLM)
│   │   ├── diagnosis.py            # Failure mode identification
│   │   ├── intervention.py         # Action selection + assignment
│   │   ├── outcome_tracker.py      # Intervention result tracking
│   │   ├── tools.py                # LangChain tools for data queries
│   │   └── prompts.py              # System prompts
│   │
│   ├── market_access/              # Market Access Crew
│   │   ├── __init__.py
│   │   ├── crew.py                 # run_market_access_crew() pipeline
│   │   ├── market_intel.py         # Revenue concentration + opportunities
│   │   ├── icp.py                  # Ideal Customer Profile builder
│   │   ├── lead_scoring.py         # Segment opportunity scoring
│   │   ├── revenue_model.py        # LTV projections
│   │   ├── campaign.py             # Campaign strategy planner
│   │   ├── tools.py                # LangChain tools
│   │   └── prompts.py              # System prompts
│   │
│   └── knowledge/                  # Shared Knowledge Layer
│       ├── __init__.py
│       ├── data_access.py          # DataAccessLayer (SQL queries → pandas)
│       ├── knowledge_store.py      # Persist agent outputs to PostgreSQL
│       └── feedback_loop.py        # Cross-crew feedback logic
│
├── blueprints/
│   ├── __init__.py
│   ├── main.py                     # Dashboard, upload, data reload, LLM selector
│   ├── flags.py                    # Sales/product inactivity flags
│   ├── retention.py                # Retention dashboard + customer detail
│   ├── market_access.py            # Market access dashboard + segment detail
│   ├── chat.py                     # Chat interface routes
│   └── api.py                      # JSON API endpoints for agent execution
│
├── services/
│   ├── __init__.py
│   ├── customer_cleaning.py        # Ported from CustClean.py
│   ├── churn_flagging.py           # Ported from SalesChurn.py
│   └── data_loader.py              # CSV → PostgreSQL loader
│
├── templates/
│   ├── base.html                   # Layout: sidebar nav, top bar, Tailwind
│   ├── index.html                  # Dashboard
│   ├── upload.html                 # CSV upload + data cleaning
│   ├── sales_flags.html            # Sales inactivity flags
│   ├── product_flags.html          # Product inactivity flags
│   ├── chat.html                   # Agent chat interface
│   ├── retention/
│   │   ├── dashboard.html          # Churn scores (inline diagnosis + customer names), interventions
│   │   └── customer_detail.html    # Single customer deep-dive
│   └── market_access/
│       ├── dashboard.html          # ICP profiles, segment scores
│       └── segment_detail.html     # Single segment deep-dive
│
├── static/
│   ├── css/tailwind.css            # Tailwind placeholder (CDN used)
│   ├── js/app.js                   # General client-side utilities
│   ├── js/chat.js                  # Chat UI fetch logic
│   └── img/Laborie.png             # Company logo
│
├── files/
│   ├── CustomerChurn_Enriched_Master.csv  # Enriched dataset (102 cols, 26,597 rows)
│   └── uploads/                    # User CSV uploads (gitignored)
│
└── legacy/                         # Original Streamlit v1 files (preserved)
    ├── file_cleansing.py
    ├── CustClean.py
    ├── SalesFlag.py
    ├── SalesChurn.py
    └── ProductFlag.py
```

---

## Routes

| Method | Route | Blueprint | Description |
|--------|-------|-----------|-------------|
| GET | `/` | main | Dashboard with stats + recent agent runs |
| GET/POST | `/upload` | main | CSV upload with threshold settings |
| POST | `/reload-enriched` | main | Reload enriched CSV into PostgreSQL |
| GET | `/download/not-found` | main | Download unmatched customers CSV |
| POST | `/set-llm` | main | Set LLM model in session |
| GET/POST | `/flags/sales` | flags | Sales inactivity flags (yellow/red) |
| GET | `/flags/sales/download/<type>` | flags | Download flagged customers CSV |
| GET/POST | `/flags/product` | flags | Product-level inactivity flags |
| GET | `/flags/product/download/<type>` | flags | Download product flag CSV |
| GET | `/retention/` | retention | Churn scores (with inline diagnosis + customer names), interventions |
| GET | `/retention/<customer_no>` | retention | Customer deep-dive |
| GET | `/market-access/` | market_access | ICP profiles, segment scores |
| GET | `/market-access/<segment>` | market_access | Segment deep-dive |
| GET | `/chat/` | chat | Chat interface |
| POST | `/chat/send` | chat | Send message to orchestrator |
| POST | `/api/retention/run` | api | Trigger retention crew |
| POST | `/api/market-access/run` | api | Trigger market access crew |
| GET | `/api/retention/scores` | api | Get churn scores (JSON) |
| GET | `/api/market-access/profiles` | api | Get ICP profiles (JSON) |

---

## Agent Crews

### Retention Specialist Crew

Triggered via `POST /api/retention/run` or the "Run Retention Analysis" button.

**Pipeline:**
1. **Churn Risk Scoring** (`churn_risk.py`) — SQL pre-filters top 50 customers by inactivity → LLM assigns risk scores (0–1), levels, contributing factors, and recommended actions
2. **Diagnosis** (`diagnosis.py`) — Takes high/medium risk customers → LLM identifies failure modes (product fit, competitive displacement, service quality, etc.) with confidence scores and evidence
3. **Intervention Selection** (`intervention.py`) — Maps diagnoses to actions: sales_outreach, pricing_review, product_demo, service_escalation, executive_engagement, training, loyalty_program
4. **Outcome Tracking** (`outcome_tracker.py`) — Logs intervention results for future reference
5. **Cross-Crew Feedback** — Sends churned customer archetypes to Market Access crew for ICP exclusion

### Market Access Crew

Triggered via `POST /api/market-access/run` or the "Run Market Analysis" button.

**Pipeline:**
1. **Market Intelligence** (`market_intel.py`) — Analyzes revenue concentration, under-penetrated regions, product category opportunities
2. **ICP Builder** (`icp.py`) — Builds ideal customer profiles using segment data, excludes churned archetypes from retention crew feedback
3. **Lead Scoring** (`lead_scoring.py`) — Scores segments for expansion: score (0–1), rationale, estimated LTV, recommended channel
4. **Revenue Model** (`revenue_model.py`) — Projects 12-month revenue by segment with retention-rate adjustments
5. **Campaign Planner** (`campaign.py`) — Designs outreach strategies: awareness, nurture, conversion, expansion with territory assignments
6. **Cross-Crew Feedback** — Sends top-performing segment benchmarks to Retention crew

### Chat Orchestrator

Triggered via `/chat` interface or `POST /chat/send`.

**Routing logic:** The orchestrator classifies the user's question into one of 5 actions:
- `customer_detail` — Specific customer questions (fetches customer data + transactions)
- `churn_risk` — At-risk customer questions (fetches top 20 high-risk customers)
- `retention` — Retention strategy questions
- `market_intel` — Market opportunity questions (fetches segment + region performance)
- `general` — General data questions (fetches overview data)

The router extracts customer numbers and segment names from the query, gathers relevant context from PostgreSQL, and generates a response.

---

## Cross-Crew Feedback Loop

The two crews share insights bidirectionally:

**Retention → Market Access:**
- Churned customer archetypes (industry, region, segment patterns with 3+ occurrences)
- Used to exclude high-churn profiles from ICP targeting

**Market Access → Retention:**
- Top 10 segments by revenue as performance benchmarks
- Used to set retention targets for at-risk customers

Feedback is stored in the `feedback_loop` table with source/target crew, insight type, and JSONB payload.

---

## Data Source

**Enriched Master Dataset:** `files/CustomerChurn_Enriched_Master.csv`
- 102 columns, 26,597 rows
- 2,135 unique customers
- Loaded into PostgreSQL via `services/data_loader.py`

**Column mapping (CSV → PostgreSQL):**
- `customer_no` → `customers.customer_no`
- `customer_name` → `customers.customer_name`
- `USS_consumables_segment` → `customers.consumables_segment`
- `USS_capital_segment` → `customers.capital_segment`
- `USS_NPIs_tercile` → `customers.npi_tercile`
- `SalesTA_ID` → `transactions.sales_ta_id`
- `product_GBU` → `transactions.product_gbu`
- `FP_qty` → `transactions.quantity`
- `amnt` → `transactions.amount`
- `GM` → `transactions.gross_margin`
- `SalesRep` → `transactions.sales_rep`

---

## Environment Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Virtual environment: `CustomerChurn.env`

### Installation

```bash
# Activate virtual environment
source CustomerChurn.env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### .env Configuration

```
FLASK_SECRET_KEY=<random-string>
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://churnapp:churnapp123@localhost/customerchurn
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
ENRICHED_CSV_PATH=files/CustomerChurn_Enriched_Master.csv
```

### Database Setup

```bash
# Create database and user (run as postgres)
sudo -u postgres psql -c "CREATE DATABASE customerchurn;"
sudo -u postgres psql -c "CREATE USER churnapp WITH PASSWORD 'churnapp123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE customerchurn TO churnapp;"
sudo -u postgres psql -c "ALTER DATABASE customerchurn OWNER TO churnapp;"
sudo -u postgres psql -d customerchurn -c "GRANT ALL ON SCHEMA public TO churnapp;"
```

### Load Data

```bash
python -m services.data_loader
# Output: Loaded 2135 customers and 26597 transactions
```

### Run the Application

```bash
python app.py
# Runs on http://localhost:8503
```

### Production (gunicorn)

```bash
gunicorn wsgi:app -b 0.0.0.0:8503
```

---

## Cost Management

- SQL pre-filtering reduces 2,135 customers to top 50 before LLM calls
- LLM temperature set to 0.1 for deterministic, concise outputs
- Max tokens capped at 16,384 per call
- Agent runs logged in `agent_runs` table with token counts
- Constrained outputs: LLM selects from fixed intervention types and priority levels

---

## Branch Strategy

- **`main`** — Production branch running Streamlit v1. Do not modify.
- **`development`** — All v2 (Flask + AI agents) work. This branch.

---

## Verification Checklist

1. PostgreSQL tables exist (9 tables) — `\dt` in psql
2. Data loaded: 2,135 customers, 26,597 transactions
3. Flask app starts on port 8503 — all pages render with Tailwind
4. Upload CSV via `/upload` — cleaning + flag logic works
5. Sales Flags (`/flags/sales`) — yellow/red thresholds applied correctly
6. Product Flags (`/flags/product`) — customer-product level flags
7. LLM dropdown switches model in session
8. "Run Retention Analysis" → churn scores, diagnoses, interventions populate
9. "Run Market Analysis" → ICP profiles, lead scores, campaigns populate
10. Chat: "Why is customer 1018992 at risk?" → coherent response
11. `agent_runs` table tracks execution metadata
12. `feedback_loop` table has cross-crew entries after both crews run
