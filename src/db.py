import MySQLdb as mysql
import os
import streamlit as st
class Database:
    def __init__(self):
        try:
            self.pwd = os.environ.get("mysqlpwd")
            self.db = mysql.connect("localhost", "root", self.pwd, "stockdb")
            self.cursor = self.db.cursor()
            self.acoes_gravadas_usuario = []
            self.id_acoes_adicionadas = []
            self.acoes_para_remover = []
            self.loop_finished = False
        except mysql.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            print(f"Erro ao fechar o cursor: {e}")

        try:
            if self.db:
                self.db.close()
        except Exception as e:
            print(f"Erro ao fechar a conexão: {e}")

    def insert_into_wallet_has_stocks(self, id_wallet, id_stock, min_value, max_value, period):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM wallet_has_stocks WHERE id_wallet = %s AND id_stock = %s)", (id_wallet, id_stock))
        exists = self.cursor.fetchone()[0]

        if not exists:
            self.cursor.execute(
                "INSERT INTO wallet_has_stocks (id_wallet, id_stock, max_price, min_price, periodo_visualizacao) VALUES (%s, %s, %s, %s, %s)",
                (id_wallet, id_stock, min_value, max_value, period)
            )
            self.db.commit()
            return False
        else:
            return True

    def update(self, user, pwd, ticker, min_value, max_value, period, quantity):
        if self.check_user(user, pwd):
            user_id = self.select_user_id(user)
            if user_id:
                self.cursor.execute("UPDATE wallet SET quantidade_acoes = %s WHERE id_user = %s", (quantity, user_id[0]))
                wallet_id = self.select_wallet_id(user_id)
                if wallet_id:
                    stock_id = self.select_stocks_id(ticker)
                    if stock_id:
                        if self.insert_into_wallet_has_stocks(wallet_id, stock_id, min_value, max_value, period):
                            self.cursor.execute(
                                "UPDATE wallet_has_stocks SET max_price = %s, min_price = %s, periodo_visualizacao = %s WHERE id_wallet = %s AND id_stock = %s",
                                (max_value, min_value, period, wallet_id, stock_id)
                            )
                            self.db.commit()
                            self.cursor.execute("SELECT id_stock from stocks where ticker = %s", (ticker,))
                            self.id_acoes_adicionadas.append(self.cursor.fetchone()[0])

                            if self.loop_finished == True:
                                self.cursor.execute("SELECT id_stock from wallet_has_stocks where id_wallet = %s", (wallet_id,))
                                self.acoes_gravadas_usuario = [item[0] for item in self.cursor.fetchall()]
                                self.acoes_para_remover  = list(set(self.acoes_gravadas_usuario) - set(self.id_acoes_adicionadas))

                                if self.acoes_para_remover:
                                    for acao in self.acoes_para_remover:
                                        self.cursor.execute("DELETE from wallet_has_stocks where id_stock = %s and id_wallet = %s", (acao, wallet_id))
                                        self.db.commit()

    def insert(self, user, pwd):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pwd))
        self.cursor.execute("SELECT id_user FROM users WHERE username = %s", (user,))
        data = self.cursor.fetchone()
        if data:
            self.cursor.execute("INSERT INTO wallet (id_user, quantidade_acoes) VALUES (%s, %s)", (data[0], 0))
            self.db.commit()

    def check_user(self, user, pwd):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = %s)", (user,))
        exists = self.cursor.fetchone()[0]
        if not exists:
            self.insert(user, pwd)
            return False
        return True

    def select_user_id(self, user):
        self.cursor.execute("SELECT id_user FROM users WHERE username = %s", (user,))
        return self.cursor.fetchone()

    def select_wallet_id(self, user_id):
        self.cursor.execute("SELECT id_wallet FROM wallet WHERE id_user = %s", (user_id[0],))
        return self.cursor.fetchone()

    def select_stocks_id(self, ticker):
        self.cursor.execute("SELECT id_stock FROM stocks WHERE ticker = %s", (ticker,))
        return self.cursor.fetchone()

    def getPeriod(self, user):
        user_id = self.select_user_id(user)
        if user_id:
            wallet_id = self.select_wallet_id(user_id)
            if wallet_id:
                self.cursor.execute("SELECT periodo_visualizacao FROM wallet_has_stocks WHERE id_wallet = %s", (wallet_id,))
                return self.cursor.fetchone()
        return None

    def getMin(self, user, ticker):
        user_id = self.select_user_id(user)
        if user_id:
            wallet_id = self.select_wallet_id(user_id)
            if wallet_id:
                stock_id = self.select_stocks_id(ticker)
                if stock_id:
                    self.cursor.execute("SELECT min_price FROM wallet_has_stocks WHERE id_wallet = %s AND id_stock = %s", (wallet_id, stock_id))
                    return self.cursor.fetchone()
        return None

    def getMax(self, user, ticker):
        user_id = self.select_user_id(user)
        if user_id:
            wallet_id = self.select_wallet_id(user_id)
            if wallet_id:
                stock_id = self.select_stocks_id(ticker)
                if stock_id:
                    self.cursor.execute("SELECT max_price FROM wallet_has_stocks WHERE id_wallet = %s AND id_stock = %s", (wallet_id, stock_id))
                    return self.cursor.fetchone()
        return None

    def get_all_stocks_in_wallet(self, user):
        user_id = self.select_user_id(user)
        if user_id:
            wallet_id = self.select_wallet_id(user_id)
            if wallet_id:
                self.cursor.execute("SELECT company_name, ticker FROM wallet_has_stocks JOIN stocks USING (id_stock) JOIN company USING (id_company) WHERE id_wallet = %s", (wallet_id,))
                return self.cursor.fetchall()
        return []

    def get_all_companies_n_tickers(self):
        self.cursor.execute("SELECT company_name, ticker FROM company JOIN stocks USING (id_company)")
        return self.cursor.fetchall()

    def check_user_n_pwd(self, username, pwd):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = %s AND password = %s)", (username, pwd))
        return self.cursor.fetchone()[0] == 1

    def setFinished (self, value: bool):
        self.loop_finished = value