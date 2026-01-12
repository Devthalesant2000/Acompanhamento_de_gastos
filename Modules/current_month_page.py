import pandas as pd
import streamlit as st 
from Functions.theme import *
from Functions.get_data_from_sheets import *
from Functions.data_for_current_month import *
from Functions.graphics import *
from datetime import date

# Informações de Acesso API
spreadsheet_id = '1q0xLDFXhV_k7QNePUdA43KqFxvxyeI8AzyqZfdES42w'
sheet_name_get = 'respostas_forms'
sheet_fornecedores = 'fornecedores_db'

st.title(f"Acompanhamento do Mês Atual - {mes_ano_atual}")
# Pegando Dataframe
df_despesas = get_sheet_as_df(spreadsheet_id, sheet_name_get)

if df_despesas.empty:
    st.info("Comece preenchedo pelo menos um lançamento para esse centro de custos!")
    st.info("Ainda não há dados a serem mostrados.")
    st.stop()

#Tratar data recebidas
df_despesas["Data"] = pd.to_datetime(
                      df_despesas["Data"],
                      origin="1899-12-30",
                      unit="D"
                      )

df_despesas = df_despesas.sort_values(by=['Data'],ascending=True)
# Informações de data 
hoje = date.today()
mes_atual = hoje.month
ano_atual = hoje.year
mes_atual_str = str(mes_atual).zfill(2)
ano_atual_str = str(ano_atual)
mes_ano_atual = f"{mes_atual_str}/{ano_atual_str}"

# Tratando o df de despesas (apenas mês atual)
df_mes_atual = treating_df_for_current_month(df_despesas)

# -------------------------------------------------------------------
# Função genérica para renderizar o dashboard de um tipo (PF / PJ)
# -------------------------------------------------------------------
def render_dashboard_por_tipo(df_mes_atual_tipo: pd.DataFrame, titulo: str):
    st.header(titulo)

    if df_mes_atual_tipo.empty:
        st.info("Não há lançamentos para este tipo de centro de custo no mês atual.")
        return

    (
        valor_transacao_mes,
        valor_total_a_pagar_mes,
        valor_parcelas_antigas,
        valor_parcelas_novas,
        media_de_parcelas_mes,
    ) = top_metrics_for_current_month(df_mes_atual_tipo)

    # PRIMEIRA LINHA: Métricas principais
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💰 Valor Transacionado",
            value=valor_transacao_mes,
            help="Valor total das transações realizadas no mês",
        )

    with col2:
        st.metric(
            label="📅 Total a Pagar no Mês",
            value=valor_total_a_pagar_mes,
            help="Soma de parcelas antigas e novas do mês",
        )

    with col3:
        st.metric(
            label="📊 Média de Parcelamento",
            value=media_de_parcelas_mes,
            help="Média de parcelas das transações do mês",
        )

    st.divider()

    # SEGUNDA LINHA: Detalhamento das parcelas
    col4, col5 = st.columns(2)

    with col4:
        st.metric(
            label="📋 Parcelas Antigas",
            value=valor_parcelas_antigas,
            help="Valor referente a parcelas de meses anteriores",
        )

    with col5:
        st.metric(
            label="🛒 Novas Compras",
            value=valor_parcelas_novas,
            help="Valor de novas transações no mês",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # 🔔 Informativo antes dos gráficos
    st.markdown(
        """
        <div style="
            background-color:#e8f5e9;
            border:1px solid #c8e6c9;
            padding:12px 16px;
            border-radius:10px;
            margin-bottom: 10px;
        ">
            <strong>Importante:</strong> todos os gráficos abaixo consideram o 
            <strong>valor da parcela (<code>Valor_parcela</code>)</strong>, ou seja, 
            o que será efetivamente pago neste mês — e não o valor total da compra.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # GRÁFICOS
    ## Gráfico de gastos diários (somente novas compras)
    grafico_de_gastos_diarios(df_mes_atual_tipo)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        # Gráfico de gastos por fornecedor
        grafico_de_fornecedores(df_mes_atual_tipo)

    with col_g2:
        # Gráfico de gastos por categoria
        grafico_de_categorias(df_mes_atual_tipo)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Gráfico de barras - valor por forma de pagamento
    grafico_de_formas_de_pagamento(df_mes_atual_tipo)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    st.subheader("Base de Dados Considerada")
    st.dataframe(df_mes_atual_tipo)

# -------------------------------------------------------------------
# Começa a página
# -------------------------------------------------------------------

tab1, tab2 = st.tabs(["Pessoa Física", "Pessoa Jurídica"])

with tab1:
    df_mes_atual_PF = df_mes_atual.loc[df_mes_atual["Centro_de_Custo"] == "Pessoa Física"]
    render_dashboard_por_tipo(df_mes_atual_PF, "Pessoa Física")

with tab2:
    df_mes_atual_PJ = df_mes_atual.loc[df_mes_atual["Centro_de_Custo"] == "Pessoa Jurídica"]
    render_dashboard_por_tipo(df_mes_atual_PJ, "Pessoa Jurídica")
