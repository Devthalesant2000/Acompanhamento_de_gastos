import pandas as pd
import streamlit as st
from datetime import date

from Functions.theme import *
from Functions.get_data_from_sheets import get_sheet_as_df
from Functions.dictionaries import mes_dict, mes_dict_abr
from Functions.graphics import (
    gerar_grafico_gastos_mensais,
    graficos_mes_dinamico
)
from Functions.data_for_compiled_analysis import (
    calcular_kpis_ano,
    gerar_maior_gasto_ano
)

spreadsheet_id = "1q0xLDFXhV_k7QNePUdA43KqFxvxyeI8AzyqZfdES42w"
sheet_name_get = "respostas_forms"

st.set_page_config(page_title="Relatório Compilado", layout="wide")


@st.cache_data(ttl=600, show_spinner=False)
def carregar_e_tratar_df(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    df = get_sheet_as_df(spreadsheet_id, sheet_name)
    
    if df.empty:
        st.info("Comece Preenchedo pelo menos um lançamento para esse Centro De Custos!")
        st.info("Ainda Não Há Dados a Serem Mostrados.")
        st.stop()

    df["Data_dt"] = pd.to_datetime(
        df["Data"],
        origin="1899-12-30",
        unit="D",
        errors="coerce"
    )
    df = df.dropna(subset=["Data_dt"]).sort_values("Data_dt")

    df["Mês"] = df["Data_dt"].dt.month
    df["Ano"] = df["Data_dt"].dt.year
    df["Data"] = df["Data_dt"].dt.strftime("%d/%m/%Y")

    for col in ["Valor_parcela", "Valor_Total", "Parcelas"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def render_analise_compilada(df_base: pd.DataFrame, ano_analise: int, centro_custo: str):
    hoje = date.today()
    ano_atual = hoje.year
    mes_atual = hoje.month

    df_cc = df_base.loc[df_base["Centro_de_Custo"] == centro_custo].copy()
    # Regra de período:
    # - Ano atual: YTD (mantém sua lógica: exclui mês atual)
    # - Qualquer outro ano (passado OU futuro): ano completo
    mes_limite = mes_atual if ano_analise == ano_atual else 13

    df_periodo = df_cc.loc[
        (df_cc["Ano"] == ano_analise) &
        (df_cc["Mês"] < mes_limite)
    ].copy()

    if df_periodo.empty:
        st.info("Ainda Não há dados de um mês fechado para o Ano em questão.")
        st.info("Você terá dados para analisar nessa página à partir de Feveriro.")
        return

    # KPIs (função universal)
    (
        valor_total_transacionado,
        valor_total_pago,
        valor_a_pagar,
        parcela_media,
        valor_medio_por_lancamento,
    ) = calcular_kpis_ano(df_cc, ano_analise, mes_limite)

    # KPIs - Linha 1
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💰 Valor Transacionado", valor_total_transacionado)
    with c2:
        st.metric("📅 Total Pago", valor_total_pago)

    with c3:
        if ano_analise < ano_atual:
            st.metric(
                "💰➡️ Valor a Pagar (no ano)",
                "R$ 0,00",
                help="Ano encerrado: não há parcelas futuras a pagar."
            )

        elif ano_analise == ano_atual:
            st.metric(
                "💰➡️ Valor a Pagar (no ano)",
                valor_a_pagar,
                help="Parcelas restantes a pagar dentro do ano atual."
            )

        else:
            st.metric(
                "📌 Compromissos do Ano (parcelas)",
                valor_a_pagar,
                help="Parcelas que vencerão no ano futuro selecionado."
            )
    st.divider()

    # KPIs - Linha 2
    c4, c5 = st.columns(2)
    with c4:
        st.metric("💳 Média de Parcelamento", parcela_media)
    with c5:
        st.metric("🛒 Ticket Médio", valor_medio_por_lancamento)

    st.divider()

    # Gráfico mensal (universal)
    fig_mensal = gerar_grafico_gastos_mensais(df_cc, ano_analise, mes_limite, mes_dict_abr)
    if fig_mensal:
        st.plotly_chart(fig_mensal, width='stretch')
    else:
        st.info("Sem dados para gerar gráfico mensal.")

    # Maior gasto (universal)
    data_mvt, fornecedor_mvt, categoria_mvt, valor_mvt, parcelamento_mvt = gerar_maior_gasto_ano(
        df_cc, ano_analise, mes_limite, mes_dict
    )

    if data_mvt:
        with st.container(border=True):
            st.markdown("### 🏆 Maior gasto do período")
            st.markdown(
                f"""
                **Valor:** R$ {valor_mvt:,.2f}  
                **Fornecedor:** {fornecedor_mvt}  
                **Categoria:** {categoria_mvt}  
                **Data:** {data_mvt}  
                **Parcelas:** {parcelamento_mvt}x
                """.replace(",", "X").replace(".", ",").replace("X", ".")
            )

    st.divider()

    # Detalhe mensal
    df_periodo["Mês_str"] = df_periodo["Mês"].map(mes_dict)

    meses_ordenados = (
        df_periodo[["Mês", "Mês_str"]]
        .drop_duplicates()
        .sort_values("Mês")["Mês_str"]
        .tolist()
    )

    if not meses_ordenados:
        st.info("Sem meses disponíveis para detalhamento.")
        return

    mes_sel = st.selectbox(
        "Selecione um mês para análise detalhada:",
        meses_ordenados,
        key=f"mes_sel_{centro_custo}_{ano_analise}"
    )

    fig_pagamento, fig_categoria = graficos_mes_dinamico(df_periodo, mes_sel)

    colA, colB = st.columns(2)
    with colA:
        if fig_pagamento:
            st.plotly_chart(fig_pagamento, width='content')
        else:
            st.info("Sem dados para este mês (pagamento).")

    with colB:
        if fig_categoria:
            st.plotly_chart(fig_categoria, width='content')
        else:
            st.info("Sem dados para este mês (categoria).")


# ---------------- PAGE ----------------
st.title("📊 Relatório Compilado")

with st.spinner("Carregando dados..."):
    df_despesas = carregar_e_tratar_df(spreadsheet_id, sheet_name_get)

anos_disponiveis = (
    df_despesas["Ano"]
    .dropna()
    .unique()
    .astype(int)
    .tolist()
)
anos_disponiveis.sort(reverse=True)

ano_analise = st.selectbox(
    "Selecione o Ano da Análise:",
    anos_disponiveis,
    index=None,
    placeholder="Escolha um ano...",
    key="ano_analise_select"
)

if ano_analise is None:
    st.warning("Selecione um ano para iniciar a análise.")
else:
    tab1, tab2 = st.tabs(["Pessoa Física", "Pessoa Jurídica"])

    with tab1:
        render_analise_compilada(df_despesas, ano_analise, "Pessoa Física")

    with tab2:
        render_analise_compilada(df_despesas, ano_analise, "Pessoa Jurídica")
