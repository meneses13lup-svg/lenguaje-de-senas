import streamlit as st
from pathlib import Path

from src.utils.config import Config
from src.auth.authenticator import get_authenticator
from src.auth.database import init_db

st.set_page_config(
    page_title=f"{Config.APP_NAME} — Traductor",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css():
    css_path = Path(Config.ROOT_DIR) / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()
init_db()

authenticator = get_authenticator()
auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

if auth_status is True:
    # Dashboard (por ahora simple para que veas que entraste)
    with st.sidebar:
        st.title("SeñaVoz")
        authenticator.logout("Cerrar sesión", location="sidebar")
    st.success(f"¡Bienvenido/a, {name}! Ya estás dentro del sistema.")
    st.write("Aquí irá la cámara y el traductor en el siguiente paso.")
else:
    from src.pages.login import render_login
    render_login(authenticator)
    if auth_status is False:
        st.error("❌ Correo o contraseña incorrectos.")