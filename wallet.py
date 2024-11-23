import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
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
        self.ticker_list = []
        self.ativo_selecionado = 'B3SA3.SA'
        self.end_date = datetime.now()
        self.checked = False

    def setup_wallet(self):
        st.sidebar.header('Configurações do Gráfico')
        st.sidebar.markdown('Selecione o ativo:')

        for title, ticker in self.stocks_dict.items():
            if st.sidebar.checkbox(title):
                self.ticker_list.append(ticker)
                self.checked = True


        selected_period = st.sidebar.selectbox('Selecione o Período:', list(self.period.keys()))
        days = self.period[selected_period]

        st.sidebar.subheader('Opções de Visualização')
        show_volume = st.sidebar.checkbox('Mostrar Volume', value=True)
        show_max = st.sidebar.checkbox('Mostrar Máxima', value=True)

        start_date = self.end_date - timedelta(days=days)

        if not self.ticker_list:
            self.checked = False
            st.info("Your wallet is empty.")

        try:
            self.stock_list = []
            for tickers in self.ticker_list:
               try:
                data = yf.Ticker(tickers).history(start=start_date, end=self.end_date)
                if not data.empty:
                    self.stock_list.append(data)
                else:
                    st.warning(f"Dados para {tickers} não foram encontrados.")
               except Exception as e:
                st.error(f"Erro ao obter dados de {tickers}: {str(e)}")

            if not self.stock_list and self.checked == True:
                st.error("Não foi possível obter dados para este ativo.")

            else:
                for data in self.stock_list:
                    prices = data['Close']
                    date = data.index
                    max_valor = prices.max()
                    max_index = prices.idxmax()

                    # Criando o gráfico
                    fig = go.Figure()

                    # Adicionando linha principal de preços
                    fig.add_trace(
                        go.Scatter(
                            x=date,
                            y=prices,
                            mode='lines+markers',
                            name='Preço de Fechamento',
                            marker=dict(size=6, color="rgb(255,0,0)"),
                            line=dict(width=2, color="rgba(255,0,0,0.85)"),
                            hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br>" +
                                        "<b>Preço:</b> R$ %{y:.2f}<br>" +
                                        "<extra></extra>"
                        )
                    )

                    # Adicionando ponto de máxima se selecionado
                    if show_max:
                        fig.add_trace(
                            go.Scatter(
                                x=[max_index],
                                y=[max_valor],
                                mode='markers',
                                name='Valor Máximo',
                                marker=dict(
                                    size=10,
                                    symbol='star',
                                    color='green'
                                ),
                                hovertemplate="<b>Máxima do Período</b><br>" +
                                            "Data: %{x|%d/%m/%Y}<br>" +
                                            "Preço: R$ %{y:.2f}<br>" +
                                            "<extra></extra>"
                            )
                        )

                    # Adicionando volume se selecionado
                    if show_volume:
                        fig.add_trace(
                            go.Bar(
                                x=date,
                                y=data['Volume'],
                                name='Volume',
                                yaxis='y2',
                                marker=dict(color='rgba(255,0,0,0.3)'),
                                hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br>" +
                                            "<b>Volume:</b> %{y:,.0f}<br>" +
                                            "<extra></extra>"
                            )
                        )

                    # Estilização do layout
                    fig.update_layout(
                        title=f'Histórico de Preços - {self.ativo_selecionado} ({ticker})',
                        title_x=0.5,
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
                            visible=show_volume
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
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                    # Exibe informações adicionais
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### Informações do Ativo")
                        max_valor_fmt = f"R$ {float(max_valor):.2f}"
                        preco_atual_fmt = f"R$ {float(prices.iloc[-1]):.2f}"
                        variacao_fmt = f"{((float(prices.iloc[-1])/float(prices.iloc[0]) - 1) * 100):.2f}%"
                        data_maxima = max_index.strftime('%d/%m/%Y')

                        st.markdown(f"""
                        - **Preço Máximo:** {max_valor_fmt}
                        - **Data do Máximo:** {data_maxima}
                        - **Preço Atual:** {preco_atual_fmt}
                        - **Variação no Período:** {variacao_fmt}
                        """)

                    with col2:
                        st.markdown("### Volumes")
                        volume_medio = f"{data['Volume'].mean():,.0f}"
                        volume_total = f"{data['Volume'].sum():,.0f}"
                        st.markdown(f"""
                        - **Volume Médio:** {volume_medio}
                        - **Volume Total:** {volume_total}
                        """)

        except Exception as e:
            st.error(f"Erro ao carregar os dados: {str(e)}")
            st.info("Tente novamente mais tarde ou verifique se o código do ativo está correto.")

