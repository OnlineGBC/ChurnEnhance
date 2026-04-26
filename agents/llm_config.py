"""LLM factory: get_llm(choice) → BaseChatModel."""

from config.settings import Config


def get_llm(choice: str = None):
    """Return a LangChain chat model based on user selection."""
    if choice is None:
        choice = Config.DEFAULT_LLM

    model_info = Config.LLM_CHOICES.get(choice)
    if not model_info:
        raise ValueError(f"Unknown LLM choice: {choice}. Available: {list(Config.LLM_CHOICES.keys())}")

    provider = model_info["provider"]
    model_id = model_info["model_id"]

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_id,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.1,
            max_tokens=16384,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_id,
            api_key=Config.ANTHROPIC_API_KEY,
            temperature=0.1,
            max_tokens=16384,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
