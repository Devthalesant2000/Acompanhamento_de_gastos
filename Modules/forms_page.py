import pandas as pd
import streamlit as st
from Functions.get_data_from_sheets import (
    get_sheet_as_df,
    append_resposta_forms,
    append_fornecedor,
)

spreadsheet_id = '1q0xLDFXhV_k7QNePUdA43KqFxvxyeI8AzyqZfdES42w'
sheet_name_get = 'categorias'
sheet_name_push = 'respostas_forms'
sheet_fornecedores = 'fornecedores_db'  # aba de fornecedores

# ---------------------------
# BLOCO DE RESET DO FORM
# ---------------------------
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False

if st.session_state["reset_form"]:
    # apaga os valores dos widgets ANTES de recriá-los
    for key in [
        "centro_de_custo",
        "fornecedor_select",
        "fornecedor_novo",
        "categoria",
        "forma_pagamento",
        "valor_total",
        "parcelas",
        "data_input",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["reset_form"] = False
# ---------------------------

df_categorias = get_sheet_as_df(spreadsheet_id, sheet_name_get)

st.header("💸 Lançar Gastos por Centro de Custo")

# --- CENTRO DE CUSTO ---
centros_de_custo = list(df_categorias.columns)

centro_de_custo = st.selectbox(
    "Centro de Custo",
    centros_de_custo,
    key="centro_de_custo",
    index=None,  # começa sem seleção
)

if centro_de_custo == None:
    st.warning("Favor Selecionar um Centro de Custo!")
    st.stop()


# --- CATEGORIAS DEPENDENTES ---
if centro_de_custo in df_categorias.columns:
    categorias_base = (
        df_categorias[centro_de_custo]
        .dropna()
        .tolist()
    )
else:
    categorias_base = []

opcoes_categoria = categorias_base

# --- FORNECEDORES (database) ---
try:
    df_fornecedores = get_sheet_as_df(spreadsheet_id, sheet_fornecedores)
    fornecedores_lista = (
        df_fornecedores["Fornecedor"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
except Exception:
    fornecedores_lista = []

opcoes_fornecedor = fornecedores_lista + ["+ Cadastrar novo fornecedor"]

fornecedor_selecionado = st.selectbox(
    "Fornecedor",
    opcoes_fornecedor,
    key="fornecedor_select",
    index=None,  # começa vazio
)

if fornecedor_selecionado == None:
    st.warning("Favor Selecionar um Fornecdor ou cadastrar um novo")
    st.stop()

novo_fornecedor = ""
if fornecedor_selecionado == "+ Cadastrar novo fornecedor":
    novo_fornecedor = st.text_input("Digite o nome do novo fornecedor", key="fornecedor_novo")
    novo_fornecedor = novo_fornecedor.upper()

# --- FORM PRINCIPAL ---
with st.form("form_gasto"):
    data = st.date_input("Data", key="data_input")

    categoria = st.selectbox(
        "Categoria",
        opcoes_categoria,
        key="categoria",
        index=None,
    )

    valor_total = st.number_input("Valor Total", min_value=0.0, step=1.0, key="valor_total")

    opcoes_forma_pagto = ["Selecione a forma de pagamento", "Crédito", "Débito", "Pix", "Dinheiro", "Boleto"]
    forma_pagamento = st.selectbox(
        "Forma de Pagamento",
        opcoes_forma_pagto,
        key="forma_pagamento",
        index=None,
    )

    parcelas = st.number_input("Parcelas", min_value=1, step=1, value=1, key="parcelas")

    submit = st.form_submit_button("Salvar")

if submit:
    # --- validação de centro, categoria, fornecedor, forma pagamento ---

    if centro_de_custo is None:
        st.error("Por favor, selecione o centro de custo.")
        st.stop()

    if categoria == "Selecione a categoria":
        st.error("Por favor, selecione a categoria.")
        st.stop()

    if fornecedor_selecionado is None:
        st.error("Por favor, selecione ou cadastre um fornecedor.")
        st.stop()

    # define fornecedor final
    if fornecedor_selecionado == "+ Cadastrar novo fornecedor":
        fornecedor_final = novo_fornecedor.strip()
    else:
        fornecedor_final = fornecedor_selecionado

    if not fornecedor_final:
        st.error("Por favor, selecione ou cadastre um fornecedor.")
        st.stop()

    if forma_pagamento == None:
        st.error("Por favor, selecione a forma de pagamento.")
        st.stop()

    if valor_total <= 0:
        st.error("O valor total deve ser maior que zero.")
        st.stop()

    # se fornecedor for novo, salva no database
    if fornecedor_selecionado == "+ Cadastrar novo fornecedor" and fornecedor_final:
        append_fornecedor(spreadsheet_id, fornecedor_final, sheet_fornecedores)

    parcelas_int = int(parcelas)

    # --- cálculo das parcelas ---
    if parcelas_int > 0:
        valor_parcela = round(valor_total / parcelas_int, 2)
        valores_parcelas = [valor_parcela] * (parcelas_int - 1)
        ultimo_valor = round(valor_total - valor_parcela * (parcelas_int - 1), 2)
        valores_parcelas.append(ultimo_valor)
    else:
        valores_parcelas = [valor_total]
        parcelas_int = 1

    # datas das parcelas (mensal)
    datas_parcelas = []
    base_date = pd.to_datetime(data)
    for i in range(parcelas_int):
        d = (base_date + pd.DateOffset(months=i)).date()
        datas_parcelas.append(d.strftime("%d/%m/%Y"))

    # ID da compra
    data_compra_id = base_date.strftime("%Y-%m-%d")
    id_compra = f"{fornecedor_final} - {data_compra_id}"

    linhas = []
    for i in range(parcelas_int):
        linhas.append({
            "ID_Compra": id_compra,
            "Fornecedor": fornecedor_final,
            "Data": datas_parcelas[i],
            "Centro_de_Custo": centro_de_custo,
            "Categoria": categoria,
            "Valor_Total": valores_parcelas[i],
            "Forma_de_Pagamento": forma_pagamento,
            "Parcelas": parcelas_int,
            "Parcela_Atual": f"{i+1}/{parcelas_int}",
        })

    df_nova_linha = pd.DataFrame(linhas)
    append_resposta_forms(spreadsheet_id, df_nova_linha, sheet_name_push)

    st.success(f"{parcelas_int} lançamento(s) salvo(s) na planilha! ✅")

    # --- MARCA RESET PARA O PRÓXIMO RUN ---
    st.session_state["reset_form"] = True
    st.rerun()
