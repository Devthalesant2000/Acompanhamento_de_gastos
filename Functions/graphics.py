import pandas as pd
import streamlit as st 
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from .dictionaries import *

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

    return st.plotly_chart(fig, use_container_width=True)

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

    return st.plotly_chart(fig, use_container_width=True)

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

    return st.plotly_chart(fig, use_container_width=True)

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

    return st.plotly_chart(fig, use_container_width=True)

############################################################
##GRAPHICS FOR COMPILED ANALYSIS
############################################################

def gerar_grafico_gastos_mensais(df_despesas,ano_atual,mes_atual,ano_analise):
    df_grafico_gastos_mensal = df_despesas.loc[df_despesas['Ano'] == ano_analise]
    df_grafico_gastos_mensal = df_grafico_gastos_mensal.loc[df_despesas['Mês'] < mes_atual]

    grafico_gastos_mensais_gp = df_grafico_gastos_mensal.groupby(['Mês']).agg({'Valor_parcela' : 'sum'}).reset_index()
    grafico_gastos_mensais_gp['Mês_str'] = grafico_gastos_mensais_gp['Mês'].map(mes_dict_abr)

    grafico_gastos_mensais_gp = grafico_gastos_mensais_gp[['Mês_str','Valor_parcela']]

    # ----- Média móvel (3 meses) -----
    grafico_gastos_mensais_gp["Media_movel"] = (
        grafico_gastos_mensais_gp["Valor_parcela"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    # ----- Cores: destaca o maior gasto -----
    max_val = grafico_gastos_mensais_gp["Valor_parcela"].max()
    bar_colors = [
        "#FF6666" if v == max_val else "#2E8B57"
        for v in grafico_gastos_mensais_gp["Valor_parcela"]
    ]

    fig = go.Figure()

    # Barras (valor mensal)
    fig.add_trace(go.Bar(
        x=grafico_gastos_mensais_gp["Mês_str"],
        y=grafico_gastos_mensais_gp["Valor_parcela"],
        name="Valor pago",
        marker_color=bar_colors,
        hovertemplate="<b>Mês:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>",
    ))

    # Linha (média móvel)
    fig.add_trace(go.Scatter(
        x=grafico_gastos_mensais_gp["Mês_str"],
        y=grafico_gastos_mensais_gp["Media_movel"],
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

    return st.plotly_chart(fig, use_container_width=True)


def graficos_adicionais(df_despesas,ano_analise,mes_atual,mes_dict):
    df_ytd = df_despesas.loc[df_despesas['Ano'] == ano_analise]
    df_ytd = df_ytd.loc[df_despesas['Mês'] < mes_atual]
    df_ytd["Mês_str"] = df_ytd['Mês'].map(mes_dict)
    
    lista_de_meses = df_ytd["Mês_str"].unique().tolist()
    mes_selecionado = st.selectbox("Selecione um mês:", lista_de_meses)

    # Filtrar
    df_mes_dinamico = df_ytd.loc[df_ytd["Mês_str"] == mes_selecionado]

    # Agrupamentos
    gp_pagamento = df_mes_dinamico.groupby("Forma_de_Pagamento")["Valor_parcela"].sum().reset_index()
    gp_categoria = df_mes_dinamico.groupby("Categoria")["Valor_parcela"].sum().reset_index()

    # FIG PAGAMENTO
    fig_pagamento = px.bar(
        gp_pagamento,
        x="Valor_parcela",
        y="Forma_de_Pagamento",
        orientation="h",
        title="Gastos por Forma de Pagamento",
        text="Valor_parcela"
    )
    fig_pagamento.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
    fig_pagamento.update_layout(xaxis_title="Valor (R$)", yaxis_title="")

    # FIG CATEGORIA
    fig_categoria = px.bar(
        gp_categoria,
        x="Valor_parcela",
        y="Categoria",
        orientation="h",
        title="Gastos por Categoria",
        text="Valor_parcela"
    )
    fig_categoria.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
    fig_categoria.update_layout(xaxis_title="Valor (R$)", yaxis_title="")

    return fig_pagamento, fig_categoria