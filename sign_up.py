import streamlit as st
from auth_menu import AuthenticationMenu
from state import State

class SignUp(AuthenticationMenu):
    def __init__ (self, state: State):
        self.state = state
    def auth(self) -> None:
        st.title('Sign up')
        username = st.text_input("Username",placeholder="Username", label_visibility="hidden")
        password = st.text_input("Password",placeholder="Password", type="password", label_visibility="hidden")
        button = st.button("Sign in")
        if button:
            if username != "" and password != "":
                self.state.set_logged_in(False)
                self.state.set_login_failed(False)
                st.success("Sign-up sucessful")
