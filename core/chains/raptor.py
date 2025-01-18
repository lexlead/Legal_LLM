from langchain import hub
from langchain.chat_models.base import BaseChatModel
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, Runnable
from langchain.vectorstores import VectorStore
from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT: ChatPromptTemplate = hub.pull("ragprompt")


def build_rag_chain(
    llm_model: BaseChatModel,
    vectorstore: VectorStore
):
    return (
        {
            "context": vectorstore.as_retriever(search_kwargs={"k": 12}),
            "question": RunnablePassthrough()
        }
        | RAG_PROMPT
        | llm_model
        | StrOutputParser()
    )


def generate_answer(chain: Runnable, question: str) -> str:
    return chain.invoke({"question": question})
