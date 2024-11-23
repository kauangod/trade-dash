import streamlit as st
from login import Login
from state import State
from sign_up import SignUp
from wallet import Wallet
def main():
  state = State()
  login_instance = Login(state)
  sign_up_instance = SignUp(state)
  wallet_instance = Wallet()
  login_page = st.Page(login_instance.auth, title="Login Page", url_path="login", default=True)
  sign_up_page = st.Page(sign_up_instance.auth, title="Sign Up Page")
  logout_page = st.Page(login_instance.logout, title="Log out")
  dsh_b = st.Page(wallet_instance.setup_wallet, title="Wallet", default=True)
  test = st.Page("test.py", title="Test")

  if state.is_logged_in():
    pg = st.navigation(
      {
        "Account": [logout_page, sign_up_page],
        "Tools": [dsh_b, test]
      }
    )
  else:
    pg = st.navigation({"Account":[login_page, sign_up_page]})
  pg.run()

if __name__ == "__main__":
  main()