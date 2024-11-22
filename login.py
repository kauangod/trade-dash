import streamlit as st
from auth_menu import AuthenticationMenu
from state import State

class Login(AuthenticationMenu):
  def __init__(self, state: State) -> None:
    self.state = state

  def auth(self) -> None:
    st.title("Login")
    username = st.text_input("Username",placeholder="Username", label_visibility="hidden")
    password = st.text_input("Password",placeholder="Password", type="password", label_visibility="hidden")
    button = st.button("Log in")
    if button:
      if username == "admin" and password == "1234":
          st.success("Login successful!")
          self.state.set_logged_in(True)
          self.state.set_login_failed(False)
          st.rerun()
      else:
          self.state.set_login_failed(True)
    if self.state.has_login_failed():
      st.error("Incorrect username or password. Please try again.")

  def logout(self) -> None:
    self.state.set_logged_in(False)
    st.rerun()
