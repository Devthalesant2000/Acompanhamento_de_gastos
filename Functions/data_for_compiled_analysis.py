import pandas as pd 
import streamlit as st
from datetime import datetime, date
from datetime import date

# Informações de data 
hoje = date.today()
mes_atual = hoje.month
ano_atual = hoje.year
mes_atual_str = str(mes_atual)
ano_atual_str = str(ano_atual)
mes_ano_atual = mes_atual_str + "/" +  ano_atual_str

def format_brl(valor):
    """Formata número no padrão brasileiro: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_kpis_atual(df_despesas,ano_atual,mes_atual,ano_analise):
    

    df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] == ano_atual]

    df_despesas_a_pagar = df_despesas_ano_analisado.copy()
    df_despesas_a_pagar = df_despesas_a_pagar.loc[df_despesas_a_pagar['Mês'] >= mes_atual]

    df_despesas_ano_analisado = df_despesas_ano_analisado.loc[df_despesas['Mês'] != mes_atual]

    #Definindo métricas principais:
    #Valor total transacionado
    df_valor_total_transacionado = df_despesas_ano_analisado.drop_duplicates(subset="ID_Compra",keep='first')
    valor_total_transacionado = format_brl(round(df_valor_total_transacionado['Valor_Total'].sum(),0))
    #Valor total pago
    valor_total_pago = format_brl(round(df_despesas_ano_analisado['Valor_parcela'].sum(),0))

    #Pendente a pagar esse ano (valores das parcelas remanescentes de outras compras anteriores)
    valor_a_pagar = format_brl(round(df_despesas_a_pagar['Valor_parcela'].sum(),0))

    # Parcela média do ano:
    parcela_media = f"{round(df_valor_total_transacionado['Parcelas'].mean())} parcelas"
    valor_medio_por_lancamento = format_brl(round(df_valor_total_transacionado['Valor_Total'].mean(),0))


    return valor_total_transacionado, valor_total_pago, valor_a_pagar,parcela_media, valor_medio_por_lancamento


def gerar_maior_gasto(df_despesas,ano_analise,mes_atual,mes_dict):
    df_metricas_micro = df_despesas.loc[df_despesas['Ano'] == ano_analise]
    df_metricas_micro = df_metricas_micro.loc[df_despesas['Mês'] < mes_atual]
    df_metricas_micro['Mês_str'] = df_metricas_micro['Mês'].map(mes_dict)

    maior_valor_de_transacao_df = df_metricas_micro.sort_values(by=["Valor_Total"],ascending=False)
    linha_top = maior_valor_de_transacao_df.iloc[0]

    data_mvt = linha_top["Data"]
    fornecedor_mvt = linha_top["Fornecedor"]
    categoria_mvt = linha_top["Categoria"]
    valor_mvt = linha_top["Valor_Total"]
    parcelamento_mvt = int(linha_top["Parcelas"])

    return data_mvt,fornecedor_mvt,categoria_mvt,valor_mvt,parcelamento_mvt


def calcular_kpis_ano(
    df_despesas: pd.DataFrame,
    ano_analise: int,
    mes_limite: int
):
    hoje = date.today()
    ano_atual = hoje.year
    mes_atual = hoje.month

    # -----------------------------
    # TOTAL PAGO (parcelas do ano)
    # -----------------------------
    df_ano = df_despesas.loc[
        (df_despesas["Ano"] == ano_analise) &
        (df_despesas["Mês"] < mes_limite)
    ]

    total_pago = df_ano["Valor_parcela"].sum()

    # Ano futuro → nada foi pago ainda
    if ano_analise > ano_atual:
        total_pago = 0

    # -----------------------------
    # VALOR TRANSACIONADO
    # (somente compras iniciadas no ano)
    # -----------------------------
    primeira_parcela = (
        df_despesas
        .sort_values(["ID_Compra", "Ano", "Mês"])
        .groupby("ID_Compra", as_index=False)
        .first()
    )

    compras_do_ano = primeira_parcela.loc[
        primeira_parcela["Ano"] == ano_analise
    ]

    valor_transacionado = compras_do_ano["Valor_Total"].sum()

    # Ano futuro → impossível transacionar
    if ano_analise > ano_atual:
        valor_transacionado = 0

    # -----------------------------
    # VALOR A PAGAR
    # -----------------------------
    if ano_analise == ano_atual:
        # Parcelas futuras do próprio ano
        df_a_pagar = df_despesas.loc[
            (df_despesas["Ano"] == ano_analise) &
            (df_despesas["Mês"] >= mes_atual)
        ]
        valor_a_pagar = df_a_pagar["Valor_parcela"].sum()

    elif ano_analise > ano_atual:
        # TODAS as parcelas que vencem no ano futuro
        valor_a_pagar = df_despesas.loc[
            df_despesas["Ano"] == ano_analise
        ]["Valor_parcela"].sum()

    else:
        # Ano passado → nada a pagar
        valor_a_pagar = 0

    # -----------------------------
    # MÉDIAS
    # -----------------------------
    if valor_transacionado > 0:
        parcela_media = f"{round(compras_do_ano['Parcelas'].mean())} parcelas"
        ticket_medio = compras_do_ano["Valor_Total"].mean()
    else:
        parcela_media = "—"
        ticket_medio = 0

    return (
        format_brl(valor_transacionado),
        format_brl(total_pago),
        format_brl(valor_a_pagar),
        parcela_media,
        format_brl(ticket_medio),
    )


def gerar_maior_gasto_ano(
    df_despesas: pd.DataFrame,
    ano_analise: int,
    mes_limite: int,
    mes_dict: dict
):
    df_ano = df_despesas.loc[
        (df_despesas["Ano"] == ano_analise) &
        (df_despesas["Mês"] < mes_limite)
    ].copy()

    if df_ano.empty:
        return None, None, None, None, None

    df_ano["Mês_str"] = df_ano["Mês"].map(mes_dict)

    linha_top = df_ano.sort_values(
        by="Valor_Total", ascending=False
    ).iloc[0]

    return (
        linha_top["Data"],
        linha_top["Fornecedor"],
        linha_top["Categoria"],
        linha_top["Valor_Total"],
        int(linha_top["Parcelas"])
    )




