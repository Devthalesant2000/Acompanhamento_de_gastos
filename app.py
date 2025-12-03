import streamlit as st
from Functions import *

st.set_page_config(
    page_title="Acompanhamento de Gastos - Napoleone",
    layout="wide",
    page_icon="💰",
)


# ============================================
# DEFINIÇÃO DAS PÁGINAS
# ============================================

forms_page = st.Page(
    "Modules/forms_page.py",
    title="Envio de Gastos",
    icon="💸",
)

current_month_page = st.Page(
    "Modules/current_month_page.py",
    title="Mês Atual",
    icon="📊",
)

compiled_analysis_page = st.Page(
    "Modules/compiled_analysis_page.py",
    title="Análise Compilada",
    icon="📈",
)

configurations_page = st.Page(
    "Modules/configurations_page.py",
    title="Configurações",
    icon="⚙️",
)

# config_page = st.Page(
#     "Views/configuracoes.py",
#     title="Configurações",
#     icon="⚙️",
# )

# ============================================
# NAVEGAÇÃO PADRÃO (sem roles, por enquanto)
# ============================================

NAV_MAP = {
    "Gastos": [
        forms_page,
        current_month_page,
        compiled_analysis_page,
        configurations_page,
        # config_page,
    ]
}

# ============================================
# RODA A NAVEGAÇÃO
# ============================================

pg = st.navigation(NAV_MAP)
pg.run()