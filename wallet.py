import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# Conteúdo do Streamlit
st.sidebar.header('Configurações do Gráfico')
# Seleção do ativo
acoes = {
    'Petrobras': 'PETR4.SA',
    'Vale': 'VALE3.SA',
    'Itaú': 'ITUB4.SA',
    'Bradesco': 'BBDC4.SA',
    'Magazine Luiza': 'MGLU3.SA',
    'B3': 'B3SA3.SA'
}
ativo_selecionado = st.sidebar.selectbox('Selecione o Ativo:', list(acoes.keys()))
ticker = acoes[ativo_selecionado]

# Seleção do período
periodos = {
    '5 dias': 5,
    '15 dias': 15,
    '1 mês': 30,
    '3 meses': 90,
    '6 meses': 180,
    '1 ano': 365,
    '5 anos': 1826,
    '10 anos': 3653
}
periodo_selecionado = st.sidebar.selectbox('Selecione o Período:', list(periodos.keys()))
dias = periodos[periodo_selecionado]

# Opções de visualização
st.sidebar.subheader('Opções de Visualização')
mostrar_volume = st.sidebar.checkbox('Mostrar Volume', value=True)
mostrar_maxima = st.sidebar.checkbox('Mostrar Máxima', value=True)



# Configuração do período de dados
data_fim = datetime.now()
data_inicio = data_fim - timedelta(days=dias)

# Download dos dados com tratamento de erro
try:
    acao = yf.Ticker(ticker)
    dados = acao.history(start=data_inicio, end=data_fim)

    if dados.empty:
        st.error("Não foi possível obter dados para este ativo.")
    else:
        # Preparando os dados
        precos = dados['Close']
        datas = dados.index
        max_valor = precos.max()
        max_index = precos.idxmax()

        # Criando o gráfico
        fig = go.Figure()

        # Adicionando linha principal de preços
        fig.add_trace(
            go.Scatter(
                x=datas,
                y=precos,
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
        if mostrar_maxima:
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
        if mostrar_volume:
            fig.add_trace(
                go.Bar(
                    x=datas,
                    y=dados['Volume'],
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
            title=f'Histórico de Preços - {ativo_selecionado} ({ticker})',
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
                visible=mostrar_volume
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
        st.plotly_chart(fig, use_container_width=True)

        # Exibe informações adicionais
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Informações do Ativo")
            max_valor_fmt = f"R$ {float(max_valor):.2f}"
            preco_atual_fmt = f"R$ {float(precos.iloc[-1]):.2f}"
            variacao_fmt = f"{((float(precos.iloc[-1])/float(precos.iloc[0]) - 1) * 100):.2f}%"
            data_maxima = max_index.strftime('%d/%m/%Y')

            st.markdown(f"""
            - **Preço Máximo:** {max_valor_fmt}
            - **Data do Máximo:** {data_maxima}
            - **Preço Atual:** {preco_atual_fmt}
            - **Variação no Período:** {variacao_fmt}
            """)

        with col2:
            st.markdown("### Volumes")
            volume_medio = f"{dados['Volume'].mean():,.0f}"
            volume_total = f"{dados['Volume'].sum():,.0f}"
            st.markdown(f"""
            - **Volume Médio:** {volume_medio}
            - **Volume Total:** {volume_total}
            """)

except Exception as e:
    st.error(f"Erro ao carregar os dados: {str(e)}")
    st.info("Tente novamente mais tarde ou verifique se o código do ativo está correto.")

# Adiciona informações extras na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre")
st.sidebar.info("""
Este é um dashboard interativo para análise de ações.
Selecione as opções desejadas no menu acima para personalizar sua análise.
""")
