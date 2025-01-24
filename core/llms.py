from langchain.chat_models.base import BaseChatModel


def get_openai_llm() -> BaseChatModel:
    from langchain_openai.chat_models import ChatOpenAI
    return ChatOpenAI(model_name="gpt-4o", temperature=0.05)


def get_gemini_llm() -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=5,
    )
