import pandas as pd
import streamlit as st 
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from .dictionaries import *
import numpy as np

############################################################
##GRAPHICS FOR CURRENT MONTH
############################################################

def grafico_de_gastos_diarios(df_mes_atual):
    #gráfico de gastos diários (somente novas compras)
    df_to_gp_daily_expenses = df_mes_atual.loc[df_mes_atual['Parcela_Atual'].str.contains("1 de",case=False)]

    gastos_diaris_gp = df_to_gp_daily_expenses.groupby(['Data']).agg({'Valor_parcela' : 'sum'}).reset_index()
    gastos_diaris_gp = gastos_diaris_gp.sort_values("Data")

    fig = px.bar(
        gastos_diaris_gp,
        x="Data",
        y="Valor_parcela",
        labels={"Data": "Data", "Valor_parcela": "Valor (R$)"},
        title="Gastos Diários (Somente Novas Compras - 1° Parcela)",
    )

    fig.update_traces(
        texttemplate='R$ %{y:,.2f}',
        textposition='outside'
    )
    fig.update_yaxes(
        tickprefix="R$ ",
        separatethousands=True
    )

    # --- Estética profissional ---
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14, color="#2E2E2E"),
        title=dict(x=0.5, font=dict(size=20)),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(showgrid=False, title="Data"),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.1)", title="Valor (R$)"),
    )

    fig.update_traces(
        marker_color="#4CAF50",   # verde elegante
        marker_line_color="#2E7D32",
        marker_line_width=1.5,
    )

    return st.plotly_chart(fig,width='stretch')

##################################################################################################################

def grafico_de_fornecedores(df_mes_atual):
    expenses_by_suplier_gp = df_mes_atual.groupby(['Fornecedor']).agg({'Valor_parcela' : 'sum'}).reset_index()
    expenses_by_suplier_gp = expenses_by_suplier_gp.sort_values(by='Valor_parcela',ascending=False)
    expenses_by_suplier_gp = expenses_by_suplier_gp.head(10)
    fig = px.pie(
    expenses_by_suplier_gp,
    names="Fornecedor",
    values="Valor_parcela",
    title="Distribuição de Gastos por Fornecedor (TOP 10)",
    hole=0.4,  # pizza "donut" elegante — tire se quiser pizza fechada
    )

    # Deixar mais elegante
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>",
    )

    fig.update_layout(
        title_font_size=22,
        showlegend=True,
        legend_title_text="Fornecedores",
    )

    return st.plotly_chart(fig,width='stretch')

##################################################################################################################

def grafico_de_categorias(df_mes_atual):
    expenses_by_category_gp = df_mes_atual.groupby(['Categoria']).agg({'Valor_parcela' : 'sum'}).reset_index()
    fig = px.pie(
    expenses_by_category_gp,
    names="Categoria",
    values="Valor_parcela",
    title="Distribuição de Gastos por Categoria",
    hole=0.4,  # donut mais bonito visualmente
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>",
    )

    fig.update_layout(
        title_font_size=22,
        showlegend=True,
        legend_title_text="Categorias",
    )

    return st.plotly_chart(fig,width='stretch')

##################################################################################################################

def grafico_de_formas_de_pagamento(df_mes_atual):
    expenses_by_payment_method_gp = df_mes_atual.groupby(['Forma_de_Pagamento']).agg({'Valor_parcela' : 'sum'}).reset_index()
    expenses_by_payment_method_gp = expenses_by_payment_method_gp.sort_values(by=['Valor_parcela'],ascending=False)


    fig = px.bar(
        expenses_by_payment_method_gp,
        x="Forma_de_Pagamento",
        y="Valor_parcela",
        text="Valor_parcela"
    )

    # Texto nas barras como moeda BR
    fig.update_traces(
        texttemplate='R$ %{y:,.2f}',
        textposition='outside',
        marker_color="#4CAF50",        # verde elegante
        marker_line_color="#2E7D32",
        marker_line_width=1.5,
    )

    # Eixo Y como moeda
    fig.update_yaxes(
        tickprefix="R$ ",
        separatethousands=True,
        title="Valor (R$)",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.1)",
    )

    # Eixo X
    fig.update_xaxes(
        title="Forma de Pagamento",
        showgrid=False,
    )

    # Layout geral
    fig.update_layout(
        title=dict(
            text="Gasto por Forma de Pagamento",
            x=0.5,
            font=dict(size=20),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14, color="#2E2E2E"),
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        margin=dict(l=10, r=10, t=50, b=10),
    )

    return st.plotly_chart(fig,width='stretch')

# =========================================================
# Helpers
# =========================================================
def _ajustar_barh(fig):
    """
    Ajusta gráfico horizontal (barh) para não cortar texto,
    melhorar legibilidade e ordenar por total.
    """
    # pega os valores do eixo X (pode vir como array numpy/pandas)
    x_vals = []
    if fig.data and len(fig.data) > 0:
        x0 = fig.data[0].x  # mais seguro no plotly
        if x0 is not None:
            x_vals = list(x0)

    max_x = max(x_vals) if len(x_vals) > 0 else 0
    folga = max_x * 0.18 if max_x else 0

    fig.update_traces(
        cliponaxis=False,
        textposition="auto"
    )

    fig.update_layout(
        height=520,
        margin=dict(l=40, r=140, t=70, b=40),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig.update_yaxes(
        automargin=True,
        categoryorder="total ascending",
        tickfont=dict(size=12),
        showgrid=False
    )

    fig.update_xaxes(
        range=[0, max_x + folga] if max_x else None,
        tickformat="~s",
        showgrid=False
    )

    return fig


# =========================================================
# GRAPHICS FOR COMPILED ANALYSIS
# =========================================================
def gerar_grafico_gastos_mensais(
    df_despesas: pd.DataFrame,
    ano_analise: int,
    mes_limite: int,
    mes_dict_abr: dict
):
    """
    mes_limite:
        - ano atual → mes_atual (para YTD, exclui o mês atual se você passar mes_atual)
        - anos passados → 13 (ano completo)
    """
    df_ano = df_despesas.loc[
        (df_despesas["Ano"] == ano_analise) &
        (df_despesas["Mês"] < mes_limite)
    ].copy()

    if df_ano.empty:
        return None

    grafico_gp = (
        df_ano
        .groupby("Mês", as_index=False)
        .agg({"Valor_parcela": "sum"})
    )

    grafico_gp["Mês_str"] = grafico_gp["Mês"].map(mes_dict_abr)

    # Média móvel (3 meses)
    grafico_gp["Media_movel"] = (
        grafico_gp["Valor_parcela"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    # Cores (destaca maior gasto)
    max_val = grafico_gp["Valor_parcela"].max()
    bar_colors = [
        "#FF6666" if v == max_val else "#2E8B57"
        for v in grafico_gp["Valor_parcela"]
    ]

    fig = go.Figure()

    # Barras
    fig.add_trace(go.Bar(
        x=grafico_gp["Mês_str"],
        y=grafico_gp["Valor_parcela"],
        name="Valor pago",
        marker_color=bar_colors,
        hovertemplate="<b>Mês:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>",
    ))

    # Linha média móvel
    fig.add_trace(go.Scatter(
        x=grafico_gp["Mês_str"],
        y=grafico_gp["Media_movel"],
        name="Média móvel (3 meses)",
        mode="lines+markers",
        line=dict(color="orange", width=3),
        hovertemplate="<b>Mês:</b> %{x}<br><b>Média móvel:</b> R$ %{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        title="Gastos Mensais com Média Móvel",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        template="simple_white",
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
        yaxis=dict(tickprefix="R$ ", separatethousands=True),
    )

    return fig


def graficos_mes_dinamico(df_ytd: pd.DataFrame, mes_selecionado_dinamico: str):
    """
    Espera df_ytd já com a coluna 'Mês_str' preenchida (ex: df_ytd['Mês_str'] = df_ytd['Mês'].map(mes_dict)).
    Retorna (fig_pagamento, fig_categoria).
    """
    df_mes_dinamico = df_ytd.loc[
        df_ytd["Mês_str"] == mes_selecionado_dinamico
    ].copy()

    if df_mes_dinamico.empty:
        return None, None

    gp_pagamento = (
        df_mes_dinamico
        .groupby("Forma_de_Pagamento", as_index=False)["Valor_parcela"]
        .sum()
    )

    gp_categoria = (
        df_mes_dinamico
        .groupby("Categoria", as_index=False)["Valor_parcela"]
        .sum()
    )

    fig_pagamento = px.bar(
        gp_pagamento,
        x="Valor_parcela",
        y="Forma_de_Pagamento",
        orientation="h",
        title="Gastos por Forma de Pagamento",
        text="Valor_parcela",
        color_discrete_sequence=["#2E8B57"],
    )
    fig_pagamento.update_traces(texttemplate="R$ %{text:,.2f}")
    fig_pagamento.update_layout(xaxis_title="Valor (R$)", yaxis_title="")
    fig_pagamento = _ajustar_barh(fig_pagamento)

    fig_categoria = px.bar(
        gp_categoria,
        x="Valor_parcela",
        y="Categoria",
        orientation="h",
        title="Gastos por Categoria",
        text="Valor_parcela",
        color_discrete_sequence=["#2E8B57"],
    )
    fig_categoria.update_traces(texttemplate="R$ %{text:,.2f}")
    fig_categoria.update_layout(xaxis_title="Valor (R$)", yaxis_title="")
    fig_categoria = _ajustar_barh(fig_categoria)

    return fig_pagamento, fig_categoria