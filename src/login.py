import streamlit as st
from db import Database
from auth_menu import AuthenticationMenu
from state import State

class Login(AuthenticationMenu):
  def __init__(self, state: State, db: Database) -> None:
    self.state = state
    self.db = db
    self.title = ""
    self.username = ""
    self.password = ""
    self.button = ""

  def auth(self) -> None:
      self.title = st.title("Login")
      self.username = st.text_input("Usuário", placeholder="Usuário", label_visibility="hidden")
      self.password = st.text_input("Senha", placeholder="Senha", type="password", label_visibility="hidden")

      if "username" not in st.session_state:
          st.session_state.username = ""
      if "pwd" not in st.session_state:
          st.session_state.pwd = ""
      if "entrou" not in st.session_state:
          st.session_state.entrou = 0

      self.button = st.button("Entrar")
      if self.button:
          if self.db.check_user_n_pwd(self.username, self.password):
              st.success("Login bem-sucedido!")
              self.state.set_logged_in(True)
              self.state.set_login_failed(False)

              st.session_state.username = self.username
              st.session_state.pwd = self.password
              st.session_state.entrou = 0
              st.rerun()
          else:
              self.state.set_login_failed(True)

      if self.state.has_login_failed():
          st.error("Usuário ou senha incorretos, por favor tente novamente.")

  def logout(self) -> None:
      self.state.set_logged_in(False)
      st.session_state.username = ""
      st.session_state.pwd = ""
      st.session_state.entrou = 0
      st.rerun()