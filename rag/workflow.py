from langgraph.graph import END, StateGraph, START

from rag.chains.answer_grading import build_answer_grading_chain
from rag.chains.document_grading import build_grading_chain
from rag.chains.hallucination_grading import build_hallucination_grading_chain
from rag.chains.query_routing import build_routing_chain
from rag.chains.question_rewriting import build_rewriting_chain
from rag.chains.rag_generation import build_rag_generation_chain
from rag.node import (
    QuestionRewritingNode,
    DocumentsGradingNode,
    WebSearchNode,
    RetrieveDocumentsNode,
    GenerateNode,
    QuestionRoutingNode,
    decide_to_generate,
    HallucinationGradingNode
)
from rag.state import GraphState


def build_langgraph_workflow()  -> StateGraph:
    question_rewriter = build_rewriting_chain()
    retrieval_grader = build_grading_chain()
    rag_chain = build_rag_generation_chain()
    routing_chain = build_routing_chain()
    hallucination_grading_chain = build_hallucination_grading_chain()
    answer_grading_chain = build_answer_grading_chain()

    workflow = StateGraph(GraphState)
    workflow.add_node("web_search", WebSearchNode())
    workflow.add_node("retrieve", RetrieveDocumentsNode(retriever=None))
    workflow.add_node("grade_documents", DocumentsGradingNode(retrieval_grader=retrieval_grader))  # grade documents
    workflow.add_node("generate", GenerateNode(rag_chain=rag_chain))
    workflow.add_node("transform_query", QuestionRewritingNode(question_rewriter=question_rewriter))
    workflow.add_conditional_edges(
        START,
        QuestionRoutingNode(question_router=routing_chain),
        {"web_search": "web_search", "vectorstore": "retrieve"},
    )
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {"transform_query": "transform_query", "generate": "generate"},
    )
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_conditional_edges(
        "generate",
        HallucinationGradingNode(
            hallucination_grader=hallucination_grading_chain,
            answer_grader=answer_grading_chain
        ),
        {"not supported": "generate", "useful": END, "not useful": "transform_query"},
    )
    return workflow
