import streamlit as st
import streamlit_authenticator as stauth
import yaml
from pathlib import Path
from backend.utils.config import Config

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

def registrar_usuario_yaml(email: str, nombre: str, password: str) -> tuple[bool, str]:
    try:
        config = load_auth_config()
        
        if email in config["credentials"]["usernames"]:
            return False, "Este correo ya está registrado."
        
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."

        hashed_pw = stauth.Hasher.hash(password)
        config["credentials"]["usernames"][email] = {
            "email": email,
            "name": nombre,
            "password": hashed_pw,
            "plan": "personal"
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False)

        # Limpiamos la caché para que el login lea el archivo actualizado
        load_auth_config.clear()
        
        return True, "Usuario registrado correctamente."
    except Exception as e:
        return False, f"Error: {e}"