import streamlit as st
from db import Database
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class Wallet:
    def __init__(self, db: Database):
        self.period = {
            '5 dias': 5,
            '15 dias': 15,
            '1 mês': 30,
            '3 meses': 90,
            '6 meses': 180,
            '1 ano': 365,
        }
        self.db = db
        self.prices = pd.DataFrame()
        self.max_index = 0
        self.min_index = 0
        self.max = 0
        self.min = 0
        self.data = ""
        self.date = ""
        self.ticker_list = []
        self.ticker_queue = []
        self.last_elem_popped = ""
        self.end_date = datetime.now()
        self.checked = False
        self.show_volume = False
        self.show_max = False
        self.show_min = False
        self.color_min = "#FF7F7F"
        self.color_max = "green"
        self.sd_bar_h = ""
        self.sd_bar_mkdown = ""
        self.fig = ""


    def setup_chart(self):
        # Criando o gráfico
        self.fig = go.Figure()

        # Adicionando linha principal de preços
        self.fig.add_trace(
            go.Scatter(
                x=self.date,
                y=self.prices,
                mode='lines+markers',
                name='Preço de Fechamento',
                marker=dict(size=6, color="rgb(255,0,0)"),
                line=dict(width=2, color="rgba(255,0,0,0.85)"),
                hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br>" +
                            "<b>Preço:</b> R$ %{y:.2f}<br>" +
                            "<extra></extra>"
            )
        )
        if self.show_min:
            self.fig.add_trace(
                go.Scatter(
                    x=[self.min_index],
                    y=[self.min],
                    mode='markers',
                    name='Valor Mínimo',
                    marker=dict(
                        size=10,
                        symbol='triangle-down',
                        color=self.color_min
                    ),
                    hovertemplate="<b>Mínima do Período</b><br>" +
                                "Data: %{x|%d/%m/%Y}<br>" +
                                "Preço: R$ %{y:.2f}<br>" +
                                "<extra></extra>"
                )
            )
        # Adicionando ponto de máxima se selecionado
        if self.show_max:
            self.fig.add_trace(
                go.Scatter(
                    x=[self.max_index],
                    y=[self.max],
                    mode='markers',
                    name='Valor Máximo',
                    marker=dict(
                        size=10,
                        symbol='triangle-up',
                        color=self.color_max
                    ),
                    hovertemplate="<b>Máxima do Período</b><br>" +
                                "Data: %{x|%d/%m/%Y}<br>" +
                                "Preço: R$ %{y:.2f}<br>" +
                                "<extra></extra>"
                )
            )

        # Adicionando volume se selecionado
        if self.show_volume:
            self.fig.add_trace(
                go.Bar(
                    x=self.date,
                    y=self.data['Volume'],
                    name='Volume',
                    yaxis='y2',
                    marker=dict(color='rgba(255,0,0,0.3)'),
                    hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br>" +
                                "<b>Volume:</b> %{y:,.0f}<br>" +
                                "<extra></extra>"
                )
            )

        self.fig.update_layout(
            title=f'Histórico - {self.ticker_queue[0]}',
            title_x=0.7,
            font=dict(family="Arial", size=16),
            plot_bgcolor='rgb(14,17,23)',
            paper_bgcolor='rgb(14,17,23)',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor='LightGray',
                title='Data',
                rangeslider=dict(visible=True)
            ),
            yaxis=dict(
                title='Preço (R$)',
                showgrid=True,
                gridcolor='LightGray',
                zeroline=False,
                showline=False
            ),
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right',
                showgrid=False,
                visible=self.show_volume
            ),
            margin=dict(l=40, r=60, t=60, b=40),
            hoverlabel=dict(
                bgcolor="rgba(14,17,23, 0.8)",
                font_size=12,
                font_family="Arial"
            ),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(14,17,23, 0.5)"
            )
        )


        st.plotly_chart(self.fig, use_container_width=True, config={"displayModeBar": False})
    def append(self, ticker):
        self.ticker_list.append(ticker)
        self.ticker_queue.append(ticker)
        self.checked = True

    def setup_wallet(self):
        if "username" not in st.session_state or not st.session_state.username:
            st.error("Usuário não logado. Por favor, faça login.")
            return

        self.sd_bar_h = st.sidebar.header('Configurações do Gráfico')
        self.sd_bar_mkdown = st.sidebar.markdown('Selecione o ativo:')

        st.success(f"Usuário logado: {st.session_state.username}")

        stocks_in_wallet = self.db.get_all_stocks_in_wallet(st.session_state.username)
        if stocks_in_wallet:
            for title, ticker in stocks_in_wallet:
                if st.sidebar.checkbox(title, value=True):
                    self.append(ticker)

        for title, ticker in self.db.get_all_companies_n_tickers():
            if ticker not in self.ticker_list:
                if st.sidebar.checkbox(title):
                    self.append(ticker)

        updt_stocklist = []

        selecionou_periodo = False
        periodo = self.db.getPeriod(st.session_state.username)

        if "selected_period" not in st.session_state:
            st.session_state.selected_period = None
        if "days" not in st.session_state:
            st.session_state.days = None

        if not periodo:
            selected_period = st.sidebar.selectbox('Selecione o Período:', list(self.period.keys()))
            days = self.period[selected_period]
        else:
            if "entrou" not in st.session_state or st.session_state.entrou == 0:
                if periodo[0] == 30:
                    periodo_dict = {'1 mês': 30,
                                    '5 dias': 5,
                                    '15 dias': 15,
                                    '3 meses': 90,
                                    '6 meses': 180,
                                    '1 ano': 365}
                elif periodo[0] == 365:
                    periodo_dict = {'1 ano': 365,
                                    '5 dias': 5,
                                    '15 dias': 15,
                                    '1 mês': 30,
                                    '3 meses': 90,
                                    '6 meses': 180}
                elif periodo[0] == 5:
                    periodo_dict = {'5 dias': 5,
                                    '1 mês': 30,
                                    '15 dias': 15,
                                    '3 meses': 90,
                                    '6 meses': 180,
                                    '1 ano': 365}
                elif periodo[0] == 15:
                    periodo_dict = {'15 dias': 15,
                                    '5 dias': 5,
                                    '1 mês': 30,
                                    '3 meses': 90,
                                    '6 meses': 180,
                                    '1 ano': 365}
                elif periodo[0] == 90:
                    periodo_dict = {'3 meses': 90,
                                    '5 dias': 5,
                                    '15 dias': 15,
                                    '1 mês': 30,
                                    '6 meses': 180,
                                    '1 ano': 365}
                elif periodo[0] == 180:
                    periodo_dict = {'6 meses': 180,
                                    '5 dias': 5,
                                    '15 dias': 15,
                                    '1 mês': 30,
                                    '3 meses': 90,
                                    '1 ano': 365}

                # Define o período inicial com base no banco de dados
                st.session_state.selected_period = list(periodo_dict.keys())[0]
                st.session_state.days = periodo_dict[st.session_state.selected_period]
                selecionou_periodo = True
            if st.session_state.entrou == 0:
                selected_period = st.sidebar.selectbox('Selecione o Período:', list(periodo_dict.keys()), index=list(periodo_dict.keys()).index(st.session_state.selected_period))
                days = periodo_dict[selected_period]
                selecionou_periodo = True
            else:
                selected_period = st.sidebar.selectbox('Selecione o Período:', list(self.period.keys()))
                days = self.period[selected_period]
                selecionou_periodo = True
            st.session_state.entrou = 1
            st.session_state.selected_period = selected_period
            st.session_state.days = days

        st.sidebar.subheader('Opções de Visualização')
        self.show_volume = st.sidebar.checkbox('Mostrar Volume', value=True)
        self.show_max = st.sidebar.checkbox('Mostrar Máxima', value=True)
        self.show_min = st.sidebar.checkbox('Mostrar Mínima', value=True)


        self.end_date = datetime.now()
        if st.session_state.days:
            start_date = self.end_date - timedelta(days=st.session_state.days)
        if not selecionou_periodo:
            start_date = self.end_date - timedelta(days=5)
        if not self.ticker_list:
            self.checked = False
            st.info("Sua carteira está vazia.")

        try:
            self.stock_list = []
            for tickers in self.ticker_list:
                try:
                    ticker_info = yf.Ticker(tickers).info
                    if not ticker_info:
                        st.warning(f"Ticker {tickers} não encontrado ou inválido.")
                        continue

                    self.data = yf.Ticker(tickers).history(start=start_date, end=self.end_date)
                    if isinstance(self.data, pd.DataFrame) and not self.data.empty and 'Close' in self.data.columns:
                        self.data["Ticker"] = tickers
                        self.stock_list.append(self.data)
                    else:
                        st.warning(f"Dados para {tickers} não foram encontrados ou estão incompletos.")
                except Exception as e:
                    st.error(f"Erro ao obter dados de {tickers}: {str(e)}")

            if st.sidebar.button('Salvar configuração da carteira'):
                if not self.stock_list:
                    st.sidebar.error('Carteira vazia.')
                else:
                    i = 0
                    for ticker in self.ticker_list:
                        try:
                            ticker_info = yf.Ticker(ticker).info
                            if not ticker_info:
                                st.warning(f"Ticker {ticker} não encontrado ou inválido.")
                                continue

                            data = yf.Ticker(ticker).history(start=start_date, end=self.end_date)
                            if isinstance(data, pd.DataFrame) and not data.empty and 'Close' in data.columns:
                                updt_stocklist.append(data)
                            else:
                                st.warning(f"Dados para {ticker} não foram encontrados ou estão incompletos.")
                        except Exception as e:
                            st.error(f"Erro ao obter dados de {ticker}: {str(e)}")

                    for i, data in enumerate(updt_stocklist):
                        precos = data['Close']
                        max_value = precos.max()
                        min_value = precos.min()
                        if i == len(updt_stocklist) - 1:
                            self.db.setFinished(True)
                        self.db.update(st.session_state.username, st.session_state.pwd, self.ticker_list[i], min_value, max_value, days, len(self.ticker_list))
                    st.sidebar.success('Persistência efetuada com sucesso.')

            if not self.stock_list and self.checked == True:
                st.error("Não foi possível obter dados para este ativo.")

            else:
                j = 0
                for self.data in self.stock_list:
                    if isinstance(self.data, pd.DataFrame) and not self.data.empty and 'Close' in self.data.columns:
                        if j == len(self.stock_list):
                            j = 0
                        self.prices = self.data['Close']
                        self.date = self.data.index
                        current_ticker = self.data['Ticker'].iloc[j]
                        max_last_login = "N/A"
                        min_last_login = "N/A"
                        j += 1
                        if isinstance(self.prices, pd.Series) and not self.prices.empty:
                            self.max = self.prices.max()
                            self.min = self.prices.min()
                            self.max_index = self.prices.idxmax()
                            self.min_index = self.prices.idxmin()
                        else:
                            st.error(f"Erro: Dados de preços não disponíveis para {tickers}.")

                        max_result = self.db.getMax(st.session_state.username, current_ticker)

                        if max_result and len(max_result) > 0:
                            max_last_login = f"R$ {float(max_result[0]):.2f}"

                        min_result = self.db.getMin(st.session_state.username, current_ticker)
                        if min_result and len(min_result) > 0:
                            min_last_login = f"R$ {float(min_result[0]):.2f}"

                        self.setup_chart()


                        col1, col2 = st.columns(2)

                        if self.ticker_queue:
                            self.last_elem_popped = self.ticker_queue.pop(0)
                        else:
                            st.warning("A fila de tickers está vazia!")

                        with col1:
                            max_value_fmt = f"R$ {float(self.max):.2f}"
                            min_value_fmt = f"R$ {float(self.min):.2f}"
                            preco_atual_fmt = f"R$ {float(self.prices.iloc[-1]):.2f}"
                            variacao_fmt = f"{((float(self.prices.iloc[-1])/float(self.prices.iloc[0]) - 1) * 100):.2f}%"
                            data_maxima = self.max_index.strftime('%d/%m/%Y')
                            data_min    = self.min_index.strftime('%d/%m/%Y')

                            st.markdown(f"""
                            - **Preço Máximo:** {max_value_fmt}
                            - **Valor Máximo do último acesso:** {max_last_login}
                            - **Data do Máximo:** {data_maxima}
                            - **Preço Mínimo:** {min_value_fmt}
                            - **Valor Mínimo do último acesso:** {min_last_login}
                            - **Data do Mínimo:** {data_min}
                            """)

                        with col2:
                            volume_medio = f"{self.data['Volume'].mean():,.0f}"
                            volume_total = f"{self.data['Volume'].sum():,.0f}"
                            st.markdown(f"""
                            - **Preço Atual:** {preco_atual_fmt}
                            - **Variação no Período:** {variacao_fmt}
                            - **Volume Médio:** {volume_medio}
                            - **Volume Total:** {volume_total}
                            """)
                    else:
                        st.error(f"Erro: Dados inválidos para {tickers}.")

        except Exception as e:
            st.error(f"Um erro ocorreu durante o carregamento dos dados: {str(e)}")
            st.info("Por favor tente novamente mais tarde.")

