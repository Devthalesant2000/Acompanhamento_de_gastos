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

    # DEBUG: mostra qual service account está sendo usada
    try:
        print("🔐 Service account em uso:", creds.service_account_email)
    except Exception:
        print("Não foi possível obter o e-mail da service account.")

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
    """
    Lê uma aba da planilha e devolve um DataFrame.
    Tenta várias vezes em caso de erro de conexão (rede instável).
    """
    ws = get_worksheet(spreadsheet_id, sheet_name)

    last_exc = None
    for attempt in range(retries):
        try:
            data = ws.get_all_records()
            df = pd.DataFrame(data)
            return df
        except (requests.exceptions.ConnectionError, TransportError) as e:
            last_exc = e
            print(f"⚠️ Erro de conexão ao ler a planilha (tentativa {attempt+1}/{retries}): {repr(e)}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # backoff: 1s, 2s, 4s...
            else:
                # última tentativa falhou
                raise

    # se por algum motivo sair do loop sem retornar/raise
    raise last_exc

def append_data_by_columns(
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
    target_columns: Optional[List[str]] = None,
):
    """
    Adiciona linhas em uma aba específica, preenchendo colunas pelo NOME do cabeçalho.

    - spreadsheet_id: ID da planilha
    - sheet_name: nome da aba
    - df: DataFrame com os dados a serem inseridos
    - target_columns: lista de colunas (nomes do cabeçalho do Sheets) a serem usadas.
      Se None, usa df.columns.

    Requisitos:
    - A aba deve ter uma primeira linha como cabeçalho.
    - Os nomes em target_columns devem existir no cabeçalho do Sheets.
    """
    ws = get_worksheet(spreadsheet_id, sheet_name)

    # Lê o cabeçalho da aba (primeira linha)
    header_row = ws.row_values(1)  # ex: ["data", "categoria", "valor", "descricao"]

    if not header_row:
        raise ValueError(f"A aba '{sheet_name}' não possui cabeçalho na primeira linha.")

    # Se não passar target_columns, usa as colunas do df
    if target_columns is None:
        target_columns = list(df.columns)

    # Verifica se todas as colunas existem no cabeçalho do Sheets
    for col in target_columns:
        if col not in header_row:
            raise ValueError(
                f"Coluna '{col}' não encontrada no cabeçalho da aba '{sheet_name}'. "
                f"Cabeçalho atual: {header_row}"
            )

    # Mapeia nome da coluna -> índice no Sheets
    col_index_map = {name: idx for idx, name in enumerate(header_row)}  # 0-based

    # Ordena as colunas do DF conforme target_columns
    df_to_write = df[target_columns].copy()

    # Monta as linhas no formato que o Sheets espera
    rows_to_append = []
    for _, row in df_to_write.iterrows():
        # Cria linha vazia com o mesmo número de colunas do header
        new_row = [""] * len(header_row)

        for col_name in target_columns:
            sheet_idx = col_index_map[col_name]  # posição da coluna no header
            new_row[sheet_idx] = row[col_name]
        
        rows_to_append.append(new_row)

    # Faz o append em batch
    ws.append_rows(rows_to_append, value_input_option="USER_ENTERED")


def append_resposta_forms(
    spreadsheet_id: str,
    df_row: pd.DataFrame,
    sheet_name: str = "respostas_forms",
):
    expected_cols = [
        "Data",
        "Centro_de_Custo",
        "Categoria",
        "Valor_Total",
        "Forma_de_Pagamento",
        "Parcelas",
    ]

    if df_row.empty:
        raise ValueError("df_row está vazio. Passe um DataFrame com pelo menos 1 linha.")

    missing = [c for c in expected_cols if c not in df_row.columns]
    if missing:
        raise ValueError(f"Estão faltando colunas no df_row: {missing}")

    # pega a primeira linha do DF na ordem certa
    row_values = df_row[expected_cols].iloc[0].tolist()

    # 👇 AQUI: converte tudo pra tipos nativos do Python
    cleaned_values = []
    for v in row_values:
        # trata numpy int/float
        if isinstance(v, (np.integer,)):
            cleaned_values.append(int(v))
        elif isinstance(v, (np.floating,)):
            cleaned_values.append(float(v))
        else:
            # deixa como está (str, int, float puro etc.)
            cleaned_values.append(v)

    ws = get_worksheet(spreadsheet_id, sheet_name)
    ws.append_row(cleaned_values, value_input_option="USER_ENTERED")