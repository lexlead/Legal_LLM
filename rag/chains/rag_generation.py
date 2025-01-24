from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_generation_chain():
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    return prompt | llm | StrOutputParser()
