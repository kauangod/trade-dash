import streamlit as st
from auth_menu import AuthenticationMenu
from state import State

class SignUp(AuthenticationMenu):
    def __init__ (self, state: State):
        self.state = state
        self.title = ""
        self.username = ""
        self.password = ""
        self.button = ""
    def auth(self) -> None:
        self.title = st.title('Sign up')
        self.username = st.text_input("Username",placeholder="Username", label_visibility="hidden")
        self.password = st.text_input("Password",placeholder="Password", type="password", label_visibility="hidden")
        self.button = st.button("Sign up")
        if self.button:
            if self.username != "" and self.password != "":
                self.state.set_logged_in(False)
                self.state.set_login_failed(False)
                st.success("Sign-up sucessful")
