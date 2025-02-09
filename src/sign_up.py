import streamlit as st
from db import Database
from auth_menu import AuthenticationMenu
from state import State

class SignUp(AuthenticationMenu):
    def __init__ (self, state: State, db: Database):
        self.state = state
        self.db = db
        self.title = ""
        self.username = ""
        self.password = ""
        self.button = ""
    def auth(self) -> None:
        self.title = st.title('Cadastre-se')
        self.username = st.text_input("Usuário",placeholder="Usuário", label_visibility="hidden")
        self.password = st.text_input("Senha",placeholder="Senha", type="password", label_visibility="hidden")
        self.button = st.button("Registrar")
        if self.button:
            if not self.db.check_user(self.username, self.password):
                self.state.set_logged_in(False)
                self.state.set_login_failed(False)
                st.success("Cadastro bem sucedido.")
            else:
                st.error("Nome de usuário já cadastrado.")