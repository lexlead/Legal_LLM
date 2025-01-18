import dotenv

from core.constants import DOTENV_PATH
from streamlit_app.components.auth import authenticate

dotenv.load_dotenv(DOTENV_PATH)

import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from core.chains.google_search import build_search_chain, build_google_search_retriever
from core.chains.query_evaluation import build_evaluate_question_chain, QuestionEvaluation, QuestionDifficulty
from core.chains.raptor import build_rag_chain
from core.constants import CHROMA_VECTORS
from core.embdeddings import get_embeddings
from core.llms import get_openai_llm
from core.vectorstores.chroma import load_vector_store
from streamlit_app.components.chat import fill_messages_from_session, clear_chat_history

st.set_page_config(
    page_title="⚖️🏛️📜LexLead Law Advisor⚖️🎓🏛️",
    page_icon="𓍝",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def display_question_evaluation(instance):
    st.subheader("Query evaluation: ")
    st.markdown(f"**Category:** {instance.category}")
    st.markdown(f"**Is RAG Useful:** {instance.is_rag_useful}")
    st.markdown(f"**Difficulty Response:** {instance.difficulty_response}")
    st.markdown(f"**Reasoning:** {instance.reasoning_about_difficulty}")
    st.markdown(f"**Is Illinois Law:** {instance.is_illinois_law}")


def app():
    if not authenticate():
        return
    st.write("# ⚖️🏛️📜LexLead Law Advisor⚖️🎓🏛️")
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
    fill_messages_from_session()
    if prompt := st.chat_input(placeholder="How to fill a inheritance form?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant", avatar="⚖️"):
            cfg = RunnableConfig(callbacks=[StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)])
            answer = evaluate_question_chain.invoke({"question": prompt}, cfg)[0]["args"]
            evaluation = QuestionEvaluation.model_validate(answer)
            display_question_evaluation(evaluation)

            if evaluation.is_illinois_law and evaluation.is_rag_useful:
                result = rag_chain.invoke({"question": prompt}, cfg)
            elif evaluation.difficulty_response == QuestionDifficulty.EASY:
                result = llm.invoke([HumanMessage(content=prompt)])
            else:
                result = google_chain.invoke({"question": prompt}, cfg)
            st.write(result)
            message = {"role": "assistant", "content": result}
            st.session_state.messages.append(message)


if __name__ == "__main__":
    llm = get_openai_llm()
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings, str(CHROMA_VECTORS))
    google_chain = build_search_chain(llm, build_google_search_retriever())
    evaluate_question_chain = build_evaluate_question_chain(llm)
    rag_chain = build_rag_chain(llm, vector_store)
    app()
