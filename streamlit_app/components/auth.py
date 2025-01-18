from pathlib import Path

import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

CONFIG_PATH = Path(__file__).parent.parent / "resources" / "credentials.yml"
with open(CONFIG_PATH) as file:
    CONFIG = yaml.load(file, Loader=SafeLoader)


def authenticate():
    authenticator = Authenticate(
        CONFIG["credentials"],
        CONFIG["cookie"]["name"],
        CONFIG["cookie"]["key"],
        CONFIG["cookie"]["expiry_days"],
    )
    authenticator.login()
    if st.session_state['authentication_status']:
        first, *_, last = st.columns(5)
        with last:
            authenticator.logout("Logout", "main")
        with first:
            st.write(f"Welcome *{st.session_state['name']}*")
        return True
    elif not st.session_state['authentication_status']:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state['authentication_status'] is None:
        st.warning("Please enter your username and password")
        return False
