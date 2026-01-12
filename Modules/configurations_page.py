import pandas as pd
import streamlit as st 
from Functions.theme import *

apply_custom_theme()
st.title("Configurações")


limpar = st.button("Clique Aqui para Limpar o Cachê! 🧹")

if limpar:
    st.cache_data.clear()