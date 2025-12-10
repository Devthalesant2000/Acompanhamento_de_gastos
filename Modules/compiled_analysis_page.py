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

# Pegando Dataframe
df_despesas = get_sheet_as_df(spreadsheet_id, sheet_name_get)

#Tratar data recebidas
df_despesas["Data"] = pd.to_datetime(
                      df_despesas["Data"],
                      origin="1899-12-30",
                      unit="D"
                      )

df_despesas = df_despesas.sort_values(by=['Data'],ascending=True)

df_despesas['Mês'] = df_despesas['Data'].dt.month
df_despesas['Ano'] = df_despesas['Data'].dt.year
df_despesas["Data"] = df_despesas["Data"].dt.strftime("%d/%m/%Y")

# Informações de data 
hoje = date.today()
mes_atual = hoje.month
ano_atual = hoje.year
mes_atual_str = str(mes_atual).zfill(2)
ano_atual_str = str(ano_atual)
mes_ano_atual = f"{mes_atual_str}/{ano_atual_str}"

anos_disponiveis = df_despesas['Ano'].unique().tolist()

st.title("Relatório Compilado")

ano_analise = st.selectbox("Selecione o Ano da Análise:",anos_disponiveis,index=None)

if ano_analise == None:
    st.warning("Selecione Um Ano para Análise!")

else: 
    #Como será um "YTD", tirarei o mês correte da análise a não ser se for de um ano que não seja o atual:
    if ano_analise == ano_atual:

        df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] == ano_atual]

        df_despesas_a_pagar = df_despesas_ano_analisado.copy()
        df_despesas_a_pagar = df_despesas_a_pagar.loc[df_despesas_a_pagar['Mês'] >= mes_atual]

        df_despesas_ano_analisado = df_despesas_ano_analisado.loc[df_despesas['Mês'] != mes_atual]
        st.dataframe(df_despesas_ano_analisado)

        #Definindo métricas principais:
        #Valor total transacionado
        df_valor_total_transacionado = df_despesas_ano_analisado.drop_duplicates(subset="ID_Compra",keep='first')
        valor_total_transacionado = df_valor_total_transacionado['Valor_Total'].sum()
        #Valor total pago
        valor_total_pago = df_despesas_ano_analisado['Valor_parcela'].sum()

        #Pendente a pagar esse ano (valores das parcelas remanescentes de outras compras anteriores)
        valor_a_pagar = df_despesas_a_pagar['Valor_parcela'].sum()
        st.write(valor_a_pagar)





    elif ano_analise > ano_atual:
        df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] > ano_atual]
        st.dataframe(df_despesas_ano_analisado)

    else:
        df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] < ano_atual]
        st.dataframe(df_despesas_ano_analisado)






    







