from langchain_core.messages import HumanMessage
from langchain.chat_models.base import BaseChatModel
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, Runnable
from langchain.vectorstores import VectorStore
from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT: ChatPromptTemplate = ChatPromptTemplate.from_messages([
    HumanMessage(content="""
You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
Then, in a new line to list the reference, briefly tells 
the user the resource of the context, usually their titles are enough.

If you don't know the answer, just say that you don't know.
\nQuestion: {question} \nContext: {context} \nAnswer:"
    """)
])


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
