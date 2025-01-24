import streamlit as st


def fill_messages_from_session():
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def is_zip_file(byte_stream: bytes | bytearray) -> bool:
    zip_signature = b'\x50\x4B\x03\x04'
    return byte_stream[:4] == zip_signature