from langchain.chat_models.base import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnablePassthrough


PROMPT = """
Answer the question based only on the context provided and also provide
summary about sources used and citations from this sources

Context: {context}

Question: {question}
"""


def get_google_search_results(inputs: dict) -> str:
    from langchain_community.utilities import SerpAPIWrapper
    wrapper = SerpAPIWrapper()
    return wrapper.run(inputs["question"])


def build_google_search_retriever() -> BaseRetriever:
    return


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_search_chain(llm: BaseChatModel, search_retriever: BaseRetriever):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", PROMPT)
        ]
    )
    return (
        {"context": RunnableLambda(get_google_search_results), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def retrieve_answer_from_google(chain: BaseChatModel, question: str):
    return chain.ainvoke({"question": question})
