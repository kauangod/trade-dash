import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class Wallet:
    def __init__(self):
        self.stocks_dict = {
            'Petrobras': 'PETR4.SA',
            'Vale': 'VALE3.SA',
            'Itaú': 'ITUB4.SA',
            'Bradesco': 'BBDC4.SA',
            'Magazine Luiza': 'MGLU3.SA',
            'B3': 'B3SA3.SA'
        }
        self.period = {
            '5 dias': 5,
            '15 dias': 15,
            '1 mês': 30,
            '3 meses': 90,
            '6 meses': 180,
            '1 ano': 365,
        }
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

        # Exibe o gráfico no Streamlit
        st.plotly_chart(self.fig, use_container_width=True, config={"displayModeBar": False})

    def setup_wallet(self):
        self.sd_bar_h = st.sidebar.header('Configurações do Gráfico')
        self.sd_bar_mkdown = st.sidebar.markdown('Selecione o ativo:')

        for title, ticker in self.stocks_dict.items():
            if st.sidebar.checkbox(title):
                self.ticker_list.append(ticker)
                self.ticker_queue.append(ticker)
                self.checked = True

        if st.sidebar.button('Save configuration'):
            st.sidebar.success('Saved')

        selected_period = st.sidebar.selectbox('Selecione o Período:', list(self.period.keys()))
        days = self.period[selected_period]

        st.sidebar.subheader('Opções de Visualização')
        self.show_volume = st.sidebar.checkbox('Mostrar Volume', value=True)
        self.show_max = st.sidebar.checkbox('Mostrar Máxima', value=True)
        self.show_min = st.sidebar.checkbox('Mostrar Mínima', value=True)

        start_date = self.end_date - timedelta(days=days)

        if not self.ticker_list:
            self.checked = False
            st.info("Your wallet is empty.")

        try:
            self.stock_list = []
            for tickers in self.ticker_list:
               try:
                self.data = yf.Ticker(tickers).history(start=start_date, end=self.end_date)
                if not self.data.empty:
                    self.stock_list.append(self.data)
                else:
                    st.warning(f"Dados para {tickers} não foram encontrados.")
               except Exception as e:
                st.error(f"Erro ao obter dados de {tickers}: {str(e)}")

            if not self.stock_list and self.checked == True:
                st.error("Não foi possível obter dados para este ativo.")

            else:
                for self.data in self.stock_list:
                    self.prices = self.data['Close']
                    self.date = self.data.index # Acessando coluna do dataframe (index), está me retornando todas as datas dentro do período escolhido
                    self.max = self.prices.max()
                    self.min = self.prices.min()
                    self.max_index = self.prices.idxmax()
                    self.min_index = self.prices.idxmin()

                    self.setup_chart()

                    # Exibe informações adicionais
                    col1, col2 = st.columns(2)
                    self.last_elem_popped = self.ticker_queue.pop(0)
                    with col1:
                        max_value_fmt = f"R$ {float(self.max):.2f}"
                        min_value_fmt = f"R$ {float(self.min):.2f}"
                        preco_atual_fmt = f"R$ {float(self.prices.iloc[-1]):.2f}" # iloc é para eu acessar o índice númerico do preço não a coluna ('Close'), no caso o último (atual).
                        variacao_fmt = f"{((float(self.prices.iloc[-1])/float(self.prices.iloc[0]) - 1) * 100):.2f}%"
                        data_maxima = self.max_index.strftime('%d/%m/%Y')
                        data_min    = self.min_index.strftime('%d/%m/%Y')

                        st.markdown(f"""
                        - **Preço Máximo:** {max_value_fmt}
                        - **Data do Máximo:** {data_maxima}
                        - **Preço Mínimo:** {min_value_fmt}
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

        except Exception as e:
            st.error(f"An error ocurred while loading the data: {str(e)}")
            st.info("Please try again later or check if the asset code is correct.")

