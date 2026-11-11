import streamlit as st
import streamlit.components.v1 as components
from backend.auth.authenticator import registrar_usuario_yaml

def render_login(authenticator):
    # 1. Ocultar el header y ajustar el margen de Streamlit
    st.markdown("""
    <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .block-container { padding-top: 1rem !important; max-width: 100% !important; }
        
        /* Forzar a que el contenedor de columnas se alinee arriba */
        [data-testid="stVerticalBlock"] {
            gap: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # 2. Renderizar el HTML con components.html para que Streamlit no lo empuje
    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    # ==================== PANEL IZQUIERDO ====================
    with col_left:
        html_izq = """
        <div class="login-left">
            <div class="brand">
                <div class="brand-icon">
                    <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9.2 14.8V9.5a1.7 1.7 0 0 1 3.4 0v3.3-6a1.7 1.7 0 1 1 3.4 0v5.5-4.6a1.7 1.7 0 1 1 3.4 0v5.1-2.7a1.7 1.7 0 1 1 3.4 0v6.1c0 6-3.2 9.2-8.4 9.2-4 0-6.2-2.3-8.4-5.9l-1.4-2.3a1.8 1.8 0 0 1 2.9-2l1.7 1.8v-2.2Z"/>
                    </svg>
                </div>
                <div class="brand-text">
                    <h2>Seña<span>Voz</span></h2>
                    <p>Comunicación sin límites</p>
                </div>
            </div>
            <div class="login-hero">
                <span class="badge-pill">✨ Traducción inteligente en tiempo real</span>
                <h1>Tus manos hablan.<span class="accent">Nosotros les damos voz.</span></h1>
                <p>Convierte el lenguaje de señas en texto de forma clara, rápida y accesible.</p>
                <div class="status-card">
                    <div class="status-header">
                        <div class="status-indicator">
                            <span class="status-dot"></span>
                            <span>Reconocimiento activo</span>
                        </div>
                        <span class="precision-badge">100% precisión</span>
                    </div>
                </div>
            </div>
        </div>
        <style>
            .login-left { background-color: #020617; color: white; padding: 4rem; border-radius: 24px; min-height: 600px; display: flex; flex-direction: column; }
            .brand { display: flex; align-items: center; gap: 1rem; }
            .brand-icon { background: #22d3ee; width: 3rem; height: 3rem; border-radius: 12px; display: grid; place-items: center; color: #020617; }
            .brand-text h2 { margin: 0; font-size: 1.5rem; font-weight: 800; }
            .brand-text h2 span { color: #22d3ee; }
            .brand-text p { margin: 0; color: #94a3b8; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; }
            .badge-pill { display: inline-block; padding: 0.5rem 1rem; border-radius: 9999px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); font-size: 0.75rem; color: #22d3ee; margin-bottom: 2rem; margin-top: 2rem;}
            .login-hero h1 { font-size: 3rem; line-height: 1.1; margin-bottom: 1.5rem; }
            .login-hero h1 .accent { color: #22d3ee; display: block; }
            .login-hero p { font-size: 1rem; color: #cbd5e1; margin-bottom: 3rem; line-height: 1.6; }
            .status-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 1.5rem; }
            .status-header { display: flex; justify-content: space-between; margin-bottom: 1rem; align-items: center; }
            .status-indicator { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: #cbd5e1; }
            .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #34d399; box-shadow: 0 0 10px #34d399; }
            .precision-badge { background: rgba(52,211,153,0.1); color: #34d399; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
        </style>
        """
        # USAMOS COMPONENTS PARA QUE NO HAYA CUADRO BLANCO
        components.html(html_izq, height=650)

    # ==================== PANEL DERECHO ====================
    with col_right:
        st.markdown('<p style="color: #0891b2; font-weight: 700; font-size: 0.875rem; margin-bottom: 0.5rem; margin-top: 2rem;">BIENVENIDO DE NUEVO</p>', unsafe_allow_html=True)
        st.markdown('<h2 style="font-size: 2.5rem; font-weight: 800; color: #020617; margin-bottom: 0.5rem; margin-top: 0;">Inicia sesión</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; margin-bottom: 2rem; font-size: 1rem;">Ingresa tus datos para acceder a tu espacio de traducción.</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta"])

        with tab1:
            authenticator.login(
                location="main",
                fields={
                    "Form name": " ", 
                    "Username": "Correo electrónico",
                    "Password": "Contraseña",
                    "Login": "Iniciar sesión",
                }
            )
            
            if st.session_state.get("authentication_status") is False:
                st.error("❌ Correo o contraseña incorrectos.")

        with tab2:
            with st.form("registro_form", clear_on_submit=True):
                new_email = st.text_input("Correo electrónico")
                new_name = st.text_input("Nombre completo")
                new_pass = st.text_input("Contraseña", type="password")
                new_pass2 = st.text_input("Confirmar contraseña", type="password")
                
                submitted = st.form_submit_button("Registrarse", use_container_width=True)
                
                if submitted:
                    if not new_email or not new_name or not new_pass:
                        st.warning("⚠️ Por favor, llena todos los campos.")
                    elif new_pass != new_pass2:
                        st.error("❌ Las contraseñas no coinciden.")
                    else:
                        exito, mensaje = registrar_usuario_yaml(new_email, new_name, new_pass)
                        if exito:
                            st.success(f"✅ {mensaje} Ahora puedes iniciar sesión.")
                        else:
                            st.error(f"❌ {mensaje}")

        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin: 2rem 0; color: #94a3b8; font-size: 0.75rem; font-weight: 600;">
            <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
            ACCESO SEGURO
            <div style="flex: 1; height: 1px; background: #e2e8f0;"></div>
        </div>
        <p style="text-align: center; color: #94a3b8; font-size: 0.75rem;">🔒 Tu información está protegida y cifrada.</p>
        """, unsafe_allow_html=True)