import os
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from typing import List, Optional
from google.auth.exceptions import TransportError
import numpy as np
import streamlit as st
import time
import requests
from gspread.utils import ValueRenderOption

# Escopos: leitura (se depois for escrever, trocamos p/ full)
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_gspread_client():
    """
    Retorna um client do gspread usando:
    - GOOGLE_SERVICE_ACCOUNT_JSON (Cloud Run)
    - service_account.json (ambiente local)
    """
    service_account_info_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if service_account_info_str:
        # Cloud Run / variável de ambiente
        service_account_info = json.loads(service_account_info_str)
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
    else:
        # Local
        if not os.path.exists("service_account.json"):
            raise FileNotFoundError(
                "Arquivo service_account.json não encontrado na pasta do projeto."
            )
        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=SCOPES,
        )
        
    client = gspread.authorize(creds)
    return client


def get_worksheet(spreadsheet_id: str, sheet_name: str):
    client = get_gspread_client()

    try:
        sh = client.open_by_key(spreadsheet_id)
    except TransportError as e:
        # erro de rede (sem internet, VPN, firewall, etc.)
        st.error("❌ Não consegui me conectar ao Google Sheets. Verifique sua internet / VPN e tente de novo.")
        print("Erro de transporte (rede):", repr(e))
        raise
    except Exception as e:
        print(f"❌ Erro ao abrir a planilha com ID {spreadsheet_id}: {repr(e)}")
        raise

    ws = sh.worksheet(sheet_name)
    return ws


def get_sheet_as_df(spreadsheet_id: str, sheet_name: str, retries: int = 3, delay: float = 1.0) -> pd.DataFrame:
    ws = get_worksheet(spreadsheet_id, sheet_name)

    last_exc = None
    for attempt in range(retries):
        try:
            data = ws.get_all_records(
                value_render_option=ValueRenderOption.unformatted  # 👈 pega o valor cru
            )
            df = pd.DataFrame(data)
            return df
        except (requests.exceptions.ConnectionError, TransportError) as e:
            last_exc = e
            print(f"⚠️ Erro de conexão ao ler a planilha (tentativa {attempt+1}/{retries}): {repr(e)}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise

    raise last_exc

def append_resposta_forms(
    spreadsheet_id: str,
    df_rows: pd.DataFrame,
    sheet_name: str = "respostas_forms",
):
    expected_cols = [
        "ID_Compra",
        "Fornecedor",
        "Data",
        "Centro_de_Custo",
        "Categoria",
        "Valor_Total",
        "Forma_de_Pagamento",
        "Parcelas",
        "Valor_parcela",
        "Parcela_Atual",
    ]

    if df_rows.empty:
        raise ValueError("df_rows está vazio. Passe um DataFrame com pelo menos 1 linha.")

    missing = [c for c in expected_cols if c not in df_rows.columns]
    if missing:
        raise ValueError(f"Estão faltando colunas no df_rows: {missing}")

    df_use = df_rows[expected_cols].copy()

    rows_to_append = []
    for _, row in df_use.iterrows():
        row_values = row.tolist()

        cleaned_values = []
        for v in row_values:
            if isinstance(v, (np.integer,)):
                cleaned_values.append(int(v))
            elif isinstance(v, (np.floating,)):
                cleaned_values.append(float(v))
            else:
                cleaned_values.append(v)
        rows_to_append.append(cleaned_values)

    ws = get_worksheet(spreadsheet_id, sheet_name)
    ws.append_rows(rows_to_append, value_input_option="USER_ENTERED")


def append_fornecedor(spreadsheet_id: str, fornecedor: str, sheet_name: str = "fornecedores_db"):
    """
    Adiciona um fornecedor na aba de fornecedores, se ainda não existir.
    """
    if not fornecedor:
        return

    ws = get_worksheet(spreadsheet_id, sheet_name)

    # Lê fornecedores já cadastrados
    valores = ws.col_values(1)  # coluna A
    fornecedores_existentes = [v.strip() for v in valores[1:] if v]  # ignora cabeçalho (linha 1)

    if fornecedor.strip() in fornecedores_existentes:
        return  # já existe, não precisa cadastrar

    ws.append_row([fornecedor.strip()], value_input_option="USER_ENTERED")