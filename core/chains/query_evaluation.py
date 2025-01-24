from enum import Enum
from typing import Final

from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import Runnable
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


QUESTION_CATEGORY_DESCRIPTION: Final[str] = """
* issue-spotting: involves identifying potential legal issues in a scenario 
  or fact pattern. It focuses on recognizing problems or questions that need legal resolution.
* rule-recall: question asks to recall a specific legal rule or principle. 
  It’s testing memory of the law itself, without needing to apply it to a scenario.
* rule-application: question asks you to apply a known legal rule to a specific set 
  of facts or a scenario. It focuses on how the law works in practice.
* rule-conclusion: question asks you to derive a conclusion based on the application of 
  a legal rule to a scenario or set of facts.
* interpretation: The question involves interpreting a legal text, statute, or principle. 
  It requires you to understand and explain the meaning of legal language or concepts.
* rhetorical-understanding: question asks for analysis of the way an argument or position is framed, 
  or seeks to assess persuasive elements within a legal argument.
* out-of-scope: question does not relate to legal analysis or is unrelated to the provided 
  categories, making it irrelevant for classification in the legal context.
"""


class QuestionCategory(str, Enum):
    ISSUE_SPOTTING = "issue-spotting"
    RULE_RECALL = "rule-recall"
    RULE_APPLICATION = "rule-application"
    RULE_CONCLUSION = "rule-conclusion"
    INTERPRETATION = "interpretation"
    RHETORICAL_UNDERSTANDING = "rhetorical-understanding"
    OUT_OF_SCOPE = "out-of-scope"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionEvaluation(BaseModel):
    """User legal question/query evaluation"""
    category: QuestionCategory = Field(
        description=f"""
            Classify the following question into one of the categories: 
            {QUESTION_CATEGORY_DESCRIPTION}
            Provide the most appropriate category for the question.
        """
    )
    is_rag_useful: bool = Field(
        description= """
            Based on the following question or category, 
            determine if RAG (Retrieval-Augmented Generation) is useful. 
            If the question requires recalling external legal 
            information or citation, RAG is useful.
            If the question is focused on interpretation or understanding 
            without external references, RAG is not useful.
        """
    )
    difficulty_response: QuestionDifficulty = Field(
        description="""
            Classify the difficulty of the question based on its category:
            Based on the question and category, 
            classify the difficulty as **Easy**, **Medium**, or **Hard**.
        """
    )
    reasoning_about_difficulty: str = Field(
        description="""
            Reasoning about why this question difficult or not 
            taking into account complexity of low,
            existing precedents, stakeholder interests,
            fact pattern complexity, law evolving etc.
        """
    )
    is_illinois_law: bool = Field(
        description="""Check if this legal question related to Illinois laws."""
    )


PROMPT = """
As an input you have an user question in legal advisor application.
You have to look at this question carefully and analyze it.
Analysis consists of multiple steps:
1. Classify the following question into one of the categories
2. Is RAG usefully to answer this question?
3. Check if this question is difficult based on different aspects
4. Check if question related to Illinois state law

Question:
{question}
"""


def build_evaluate_question_chain(llm: BaseChatModel) -> Runnable:
    llm_with_tools = llm.bind_tools([QuestionEvaluation], tool_choice=QuestionEvaluation.__name__)
    template = ChatPromptTemplate.from_messages([HumanMessage(content=PROMPT)])
    return template | llm_with_tools | JsonOutputToolsParser()


async def evaluate_question(chain: Runnable, question: str) -> QuestionEvaluation:
    answer = (await chain.ainvoke({"question": question}))[0]["args"]
    return QuestionEvaluation.model_validate(answer)
