import streamlit as st


#frontend para as show pages
def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* TEMA PALMEIRENSE - VERDE E BRANCO */
        
        /* Fundo geral com gradiente sutil */
        .stApp {
            background: linear-gradient(135deg, #f5fdf5 0%, #f0f7f0 100%);
        }
        
        /* Cabeçalhos com estilo palmeirense */
        h1, h2, h3, h4, h5, h6 {
            color: #006400 !important;
            font-weight: 700 !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif !important;
        }
        
        h1 {
            border-left: 6px solid #006400 !important;
            padding-left: 15px !important;
            margin-bottom: 30px !important;
            background: linear-gradient(90deg, rgba(0,100,0,0.1) 0%, rgba(0,100,0,0.05) 100%) !important;
            padding: 15px !important;
            border-radius: 0 10px 10px 0 !important;
        }
        
        /* Botões com gradiente verde palmeirense */
        .stButton > button {
            background: linear-gradient(135deg, #006400 0%, #228B22 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 100, 0, 0.2) !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #004d00 0%, #1a6b1a 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0, 100, 0, 0.3) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Containers dos formulários */
        .stForm {
            background: white !important;
            border-radius: 12px !important;
            padding: 25px !important;
            border: 1px solid #d4edd4 !important;
            box-shadow: 0 4px 20px rgba(0, 100, 0, 0.08) !important;
            margin-bottom: 20px !important;
        }
        
        /* Selectboxes e inputs */
        .stSelectbox > div > div {
            border: 2px solid #d4edd4 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #006400 !important;
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #006400 !important;
            box-shadow: 0 0 0 3px rgba(0, 100, 0, 0.1) !important;
        }
        
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input,
        .stDateInput > div > div > input {
            border: 2px solid #d4edd4 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            padding: 10px 12px !important;
        }
        
        .stNumberInput > div > div > input:focus,
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: #006400 !important;
            box-shadow: 0 0 0 3px rgba(0, 100, 0, 0.1) !important;
        }
        
        /* Labels */
        label {
            font-weight: 600 !important;
            color: #2d5016 !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif !important;
        }
        
        /* Alertas e mensagens */
        .stAlert {
            border-radius: 10px !important;
            border: none !important;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%) !important;
            border-left: 5px solid #ffc107 !important;
        }
        
        .stError {
            background: linear-gradient(135deg, #fdeaea 0%, #fad6d6 100%) !important;
            border-left: 5px solid #dc3545 !important;
        }
        
        .stSuccess {
            background: linear-gradient(135deg, #e8f5e9 0%, #d4edd4 100%) !important;
            border-left: 5px solid #28a745 !important;
        }
        
        /* Radio buttons customizados */
        .stRadio > div {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #d4edd4;
        }
        
        /* Sidebar se tiver */
        .css-1d391kg {
            background: linear-gradient(180deg, #006400 0%, #004d00 100%) !important;
        }
        
        /* Tabelas */
        .dataframe {
            border-radius: 8px !important;
            overflow: hidden !important;
            border: 1px solid #d4edd4 !important;
        }
        
        .dataframe th {
            background: linear-gradient(135deg, #006400 0%, #228B22 100%) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f8fdf8 !important;
        }
        
        .dataframe tr:hover {
            background-color: #e8f5e9 !important;
        }
        
        /* Badges e chips */
        .st-bw {
            background-color: #e8f5e9 !important;
            color: #006400 !important;
            font-weight: 500 !important;
            border-radius: 20px !important;
            padding: 2px 12px !important;
            border: 1px solid #c8e6c9 !important;
        }
        
        /* Separadores */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #d4edd4, transparent);
            margin: 25px 0;
        }
        
        /* Tabs se usar */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            background-color: #f0f7f0;
            border: 1px solid #d4edd4;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #006400 !important;
            color: white !important;
        }
        
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c8e6c9;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a5d6a7;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_success_message(message):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #e8f5e9 0%, #d4edd4 100%);
        border-left: 5px solid #28a745;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 100, 0, 0.1);
    ">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 24px; margin-right: 15px;">✅</span>
            <div>
                <h4 style="margin: 0; color: #006400;">Sucesso!</h4>
                <p style="margin: 5px 0 0 0; color: #2d5016;">{message}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
