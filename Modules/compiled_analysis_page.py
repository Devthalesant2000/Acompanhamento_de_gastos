import pandas as pd
import streamlit as st 
from Functions.theme import *
from Functions.get_data_from_sheets import *
from Functions.data_for_current_month import *
from Functions.data_for_compiled_analysis import *
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

    tab1,tab2 = st.tabs(["Pessoa Física", "Pessoa Jurídica"])
    
    with tab1:
        aba = "Pessoa Física"
        df_despesas = df_despesas.loc[df_despesas['Centro_de_Custo'] == aba]
        #Como será um "YTD", tirarei o mês correte da análise a não ser que seja de um ano que não seja o atual:
  
        if ano_analise == ano_atual:
            valor_total_transacionado, valor_total_pago, valor_a_pagar,parcela_media, valor_medio_por_lancamento = calcular_kpis_atual(df_despesas,ano_atual,mes_atual,ano_analise)
            # PRIMEIRA LINHA: Métricas principais
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="💰 Valor Transacionado",
                    value=valor_total_transacionado,
                    help="Valor total das transações realizadas no Ano",
                )

            with col2:
                st.metric(
                    label="📅 Total a Pago no Ano",
                    value=valor_total_pago,
                    help="Soma do valor pago Mês a Mês no Ano",
                )

            with col3:
                st.metric(
                    label="💰➡️ Valor pendente de Pagamento",
                    value=valor_a_pagar,
                    help="Soma dos Valores a pagar nos próximos meses do Ano",
                )

            st.divider()

            # SEGUNDA LINHA: Detalhamento das parcelas
            col4, col5 = st.columns(2)

            with col4:
                st.metric(
                    label="💳 média de Parcelamento",
                    value=parcela_media,
                    help="Média de Parcelas no Ano",
                )

            with col5:
                st.metric(
                    label="🛒 Valor Médio das compras",
                    value=valor_medio_por_lancamento,
                    help="Média dos Valores das Transações Feitas no Ano",
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()



        elif ano_analise > ano_atual:
            df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] > ano_atual]
            st.dataframe(df_despesas_ano_analisado)

        else:
            df_despesas_ano_analisado = df_despesas.loc[df_despesas['Ano'] < ano_atual]
            st.dataframe(df_despesas_ano_analisado)









    







