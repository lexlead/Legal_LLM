from typing import TypedDict


class GraphState(TypedDict):
    question: str
    generation: str
    documents: list[str]
