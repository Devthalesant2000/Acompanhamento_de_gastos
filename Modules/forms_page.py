import pandas as pd
import streamlit as st
from Functions.get_data_from_sheets import *

spreadsheet_id = '1q0xLDFXhV_k7QNePUdA43KqFxvxyeI8AzyqZfdES42w'
sheet_name_get = 'categorias'
sheet_name_push = 'respostas_forms'

df_categorias = get_sheet_as_df(spreadsheet_id, sheet_name_get)

st.header("Lançar gasto")

# 1) Centros de custo = nomes das colunas
centros_de_custo = list(df_categorias.columns)

# 👇 Fora do form, para atualizar reativamente
centro_de_custo = st.selectbox(
    "Centro de Custo",
    centros_de_custo,
    key="centro_de_custo",
)

# 2) Categorias dependentes do centro de custo escolhido
categorias_opcoes = (
    df_categorias[centro_de_custo]
    .dropna()
    .tolist()
)

with st.form("form_gasto"):
    data = st.date_input("Data")

    categoria = st.selectbox(
        "Categoria",
        categorias_opcoes,
        key="categoria",
    )

    valor_total = st.number_input("Valor Total", min_value=0.0, step=1.0)

    forma_pagamento = st.selectbox(
        "Forma de Pagamento",
        ["Crédito", "Débito", "Pix", "Dinheiro", "Boleto"],
    )

    parcelas = st.number_input("Parcelas", min_value=1, step=1, value=1)

    submit = st.form_submit_button("Salvar")

if submit:
    data_str = data.strftime("%d/%m/%Y")

    df_nova_linha = pd.DataFrame([{
        "Data": data_str,
        "Centro_de_Custo": centro_de_custo,
        "Categoria": categoria,
        "Valor_Total": valor_total,
        "Forma_de_Pagamento": forma_pagamento,
        "Parcelas": parcelas,
    }])

    append_resposta_forms(spreadsheet_id, df_nova_linha, sheet_name_push)

    st.success("Lançamento salvo na planilha! ✅")
