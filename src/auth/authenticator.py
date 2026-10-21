import streamlit as st
import streamlit_authenticator as stauth
import yaml
from pathlib import Path
from src.utils.config import Config

CONFIG_PATH = Path(Config.ROOT_DIR) / "config" / "auth.yaml"

@st.cache_resource
def load_auth_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"No se encontró {CONFIG_PATH}.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_authenticator():
    config = load_auth_config()
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )