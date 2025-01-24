from langchain_openai import ChatOpenAI
from langchain.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """
You a question re-writer that converts an input question 
to a better version that is optimized \n 
for vectorstore retrieval. Look at the input and 
try to reason about the underlying semantic intent / meaning.
"""


def build_rewriting_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )
    return re_write_prompt | llm | StrOutputParser()
