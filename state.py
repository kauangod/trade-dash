import streamlit as st

class State:
    def __init__(self):
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "login_failed" not in st.session_state:
            st.session_state.login_failed = False

    def set_logged_in(self, value: bool):
        st.session_state.logged_in = value

    def is_logged_in(self) -> bool:
        return st.session_state.logged_in

    def set_login_failed(self, value: bool):
        st.session_state.login_failed = value

    def has_login_failed(self) -> bool:
        return st.session_state.login_failed
