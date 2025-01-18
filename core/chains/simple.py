from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import HumanMessage


def generate_answer(llm_model: BaseChatModel, question: str) -> str:
    messages = [HumanMessage(question)]
    return llm_model.invoke(messages).content
