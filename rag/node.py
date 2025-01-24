from typing import Literal

from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from rag.state import GraphState


class RetrieveDocumentsNode(BaseModel):
    retriever: BaseRetriever

    def __call__(self, state: GraphState):
        question = state["question"]
        documents = self.retriever.invoke(question)
        return {"documents": documents, "question": question}


class GenerateNode(BaseModel):
    rag_chain: Runnable

    def __call__(self, state: GraphState):
        question = state["question"]
        documents = state["documents"]
        generation = self.rag_chain.invoke({"context": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}


class DocumentsGradingNode(BaseModel):
    retrieval_grader: Runnable

    def __call__(self, state: GraphState):
        question = state["question"]
        documents = state["documents"]

        filtered_docs = []
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade == "yes":
                filtered_docs.append(d)
            else:
                continue
        return {"documents": filtered_docs, "question": question}


class QuestionRewritingNode(BaseModel):
    question_rewriter: Runnable

    def __call__(self, state: GraphState):
        question = state["question"]
        documents = state["documents"]
        better_question = self.question_rewriter.invoke({"question": question})
        return {"documents": documents, "question": better_question}


class WebSearchNode:
    web_search_tool: Runnable

    def __call__(self, state: GraphState):
        question = state["question"]
        docs = self.web_search_tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
        web_results = Document(page_content=web_results)
        return {"documents": web_results, "question": question}


class QuestionRoutingNode(BaseModel):
    question_router: Runnable

    def __call__(self, state: GraphState) -> Literal["web_search", "vectorstore"]:
        question = state["question"]
        source = self.question_router.invoke({"question": question})
        if source.datasource == "web_search":
            return "web_search"
        elif source.datasource == "vectorstore":
            return "vectorstore"


def decide_to_generate(state: GraphState):
    filtered_documents = state["documents"]
    return "transform_query" if not filtered_documents else "generate"


class HallucinationGradingNode(BaseModel):
    hallucination_grader: Runnable
    answer_grader: Runnable

    def __call__(self, state: GraphState):
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader.invoke({"documents": documents, "generation": generation})
        grade = score.binary_score

        if grade == "yes":
            score = self.answer_grader.invoke({"question": question, "generation": generation})
            grade = score.binary_score
            if grade == "yes":
                return "useful"
            else:
                return "not useful"
        else:
            return "not supported"
