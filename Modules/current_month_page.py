import pandas as pd
import streamlit as st 
from Functions.theme import *
from Functions.get_data_from_sheets import *
from Functions.data_for_current_month import *
from datetime import datetime, date

# Informações de Acesso API
spreadsheet_id = '1q0xLDFXhV_k7QNePUdA43KqFxvxyeI8AzyqZfdES42w'
sheet_name_get = 'respostas_forms'
sheet_fornecedores = 'fornecedores_db'

#Pegando Dataframe
df_despesas = get_sheet_as_df(spreadsheet_id, sheet_name_get)

# Informações de data 
hoje = date.today()
mes_atual = hoje.month
ano_atual = hoje.year
mes_atual_str = str(mes_atual)
ano_atual_str = str(ano_atual)
mes_ano_atual = mes_atual_str + "/" +  ano_atual_str

#Tratando o df de despeas
df_mes_atual = treating_df_for_current_month(df_despesas)

# Começa a página
st.title("Acompanhamento do Mês Atual - Mês")

tab1, tab2 = st.tabs(["Pessoa Física","Pessoa Jurídica"])

with tab1:
    st.header("Oi PF")
    df_mes_atual_PF = df_mes_atual.loc[df_mes_atual['Centro_de_Custo'] == "Pessoa Física"]
    valor_transacao_mes, valor_total_a_pagar_mes,valor_parcelas_antigas, valor_parcelas_novas, media_de_parcelas_mes = top_metrics_for_current_month(df_mes_atual_PF)
    st.metric("Valor Transacionado no Mês",valor_transacao_mes,help="teste")
    st.metric("Valor a pagar/pago no Mês",valor_total_a_pagar_mes)
    st.metric("Valor das Parcelas Antigas",valor_parcelas_antigas)
    st.metric("Valor noas compras",valor_parcelas_novas)
    st.metric("Média de Parcelamento no mês",media_de_parcelas_mes)
with tab2:
    st.header("Oi PJ")
    df_mes_atual_PJ = df_mes_atual.loc[df_mes_atual['Centro_de_Custo'] == "Pessoa Jurídica"]
    valor_transacao_mes, valor_total_a_pagar_mes,valor_parcelas_antigas, valor_parcelas_novas, media_de_parcelas_mes = top_metrics_for_current_month(df_mes_atual_PJ)
    st.metric("Valor Transacionado no Mês",valor_transacao_mes,help="teste")
    st.metric("Valor a pagar/pago no Mês",valor_total_a_pagar_mes)
    st.metric("Valor das Parcelas Antigas",valor_parcelas_antigas)
    st.metric("Valor noas compras",valor_parcelas_novas)
    st.metric("Média de Parcelamento no mês",media_de_parcelas_mes)






st.dataframe(df_mes_atual)


