import streamlit as st
from pathlib import Path
import sys
import os

# 1. Le decimos a Python que busque en la carpeta raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Importaciones base (Súper ligeras, cargan en milisegundos)
from backend.utils.config import Config
from backend.auth.authenticator import get_authenticator
from backend.auth.database import init_db

st.set_page_config(
    page_title=f"{Config.APP_NAME} — Traductor",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def load_css():
    css_path = Path(Config.ROOT_DIR) / "frontend" / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()
init_db()

authenticator = get_authenticator()
auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

# --- AQUÍ ESTÁ LA MAGIA: CARGA DIFERIDA ---
if auth_status is True:
    # Si ya inició sesión, RECIÉN AHORA importamos el traductor (que es pesado)
    from frontend.pages.traductor import render_traductor
    render_traductor()
else:
    # Si no ha iniciado sesión, solo mostramos el login (súper rápido)
    from frontend.pages.login import render_login
    render_login(authenticator)
    
    if auth_status is False:
        st.error("❌ Correo o contraseña incorrectos.")