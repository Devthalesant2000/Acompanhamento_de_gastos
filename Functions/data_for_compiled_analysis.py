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

