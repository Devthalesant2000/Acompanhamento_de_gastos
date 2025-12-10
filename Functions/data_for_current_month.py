import pandas as pd 
import streamlit as st
from datetime import datetime, date

# Informações de data 
hoje = date.today()
mes_atual = hoje.month
ano_atual = hoje.year
mes_atual_str = str(mes_atual)
ano_atual_str = str(ano_atual)
mes_ano_atual = mes_atual_str + "/" +  ano_atual_str

def treating_df_for_current_month(df):
    df_mes_atual = df
    
    df_mes_atual["Parcela_Atual"] = df_mes_atual["Parcela_Atual"].astype(str)

    df_mes_atual['Mês_ano'] = df_mes_atual['Data'].dt.strftime("%m/%Y")
    df_mes_atual = df_mes_atual.loc[df_mes_atual['Mês_ano'] == mes_ano_atual]

    df_mes_atual["Data"] = df_mes_atual["Data"].dt.strftime("%d/%m/%Y")

    return df_mes_atual

def top_metrics_for_current_month(df):
    df_mes_atual = df

    # ----- MÉTRICAS MACRO -----

    valor_transacao_mes = round(df_mes_atual["Valor_Total"].sum(), 2)
    valor_total_a_pagar_mes = round(df_mes_atual["Valor_parcela"].sum(), 2)

    # ----- PARCELAS -----
    df_mes_atual_parcelamento = df_mes_atual[
        df_mes_atual['Parcela_Atual'].str.contains('1 de', case=False)
    ]
    df_mes_anteriores_parcelamento = df_mes_atual[
        ~df_mes_atual['Parcela_Atual'].str.contains('1 de', case=False)
    ]

    valor_parcelas_antigas = round(df_mes_anteriores_parcelamento['Valor_parcela'].sum(), 2)
    valor_parcelas_novas = round(df_mes_atual_parcelamento['Valor_parcela'].sum(), 2)

    media_de_parcelas_mes = df_mes_atual_parcelamento['Parcelas'].mean()
    media_de_parcelas_mes = int(round(media_de_parcelas_mes, 0)) if not pd.isna(media_de_parcelas_mes) else 0

    # ----- FORMATANDO -----
    return (
        format_brl(valor_transacao_mes),
        format_brl(valor_total_a_pagar_mes),
        format_brl(valor_parcelas_antigas),
        format_brl(valor_parcelas_novas),
        f"{media_de_parcelas_mes} parcelas",
    )

def format_brl(valor):
    """Formata número no padrão brasileiro: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")