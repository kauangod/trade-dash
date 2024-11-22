import streamlit as st
from login import Login
from state import State
def main():
  state = State()
  login_instance = Login(state)

  login_page = st.Page(login_instance.auth)
  logout_page = st.Page(login_instance.logout, title="Log out")
  dsh_b = st.Page("wallet.py", title="Wallet", default=True)
  test = st.Page("test.py", title="Test")

  if state.is_logged_in():
    pg = st.navigation(
      {
        "Account": [logout_page],
        "Tools": [dsh_b, test]
      }
    )
  else:
    pg = st.navigation([login_page])
  pg.run()

if __name__ == "__main__":
  main()