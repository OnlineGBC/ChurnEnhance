import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://churnapp:churnapp123@localhost/customerchurn"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENRICHED_CSV_PATH = os.getenv(
        "ENRICHED_CSV_PATH", "files/CustomerChurn_Enriched_Master.csv"
    )
    UPLOAD_FOLDER = "files/uploads"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload

    # LLM config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    LLM_CHOICES = {
        "gpt-5.5": {"provider": "openai", "model_id": "gpt-5.5", "label": "OpenAI GPT-5.5"},
        "claude-sonnet-4-6": {"provider": "anthropic", "model_id": "claude-sonnet-4-6", "label": "Claude Sonnet"},
        "claude-opus-4-7": {"provider": "anthropic", "model_id": "claude-opus-4-7", "label": "Claude Opus (more expensive)"},
    }
    DEFAULT_LLM = "claude-sonnet-4-6"
