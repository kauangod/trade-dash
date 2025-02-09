import streamlit as st
from login import Login
from state import State
from sign_up import SignUp
from wallet import Wallet
from db import Database

def main():
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "pwd" not in st.session_state:
        st.session_state.pwd = ""
    if "entrou" not in st.session_state:
        st.session_state.entrou = 0
    db = Database()
    state = State()
    login_instance = Login(state, db)
    login_page = st.Page(login_instance.auth, title="Acesso", url_path="login", default=True)
    sign_up_instance = SignUp(state, db)
    sign_up_page = st.Page(sign_up_instance.auth, title="Registrar")
    logout_page = st.Page(login_instance.logout, title="Sair")
    wallet_instance = Wallet(db)
    dsh_b = st.Page(wallet_instance.setup_wallet, title="Carteira", default=True)

    if state.is_logged_in():
        pg = st.navigation(
            {
                "Conta": [logout_page, sign_up_page],
                "Ferramentas": [dsh_b]
            }
        )
    else:
        pg = st.navigation({"Conta": [login_page, sign_up_page]})
    pg.run()

if __name__ == "__main__":
  main()