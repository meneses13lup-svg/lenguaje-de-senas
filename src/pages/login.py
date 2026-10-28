import streamlit as st

def render_login(authenticator):
    # 1. Ocultar la barra lateral izquierda (la de "app" y "login") solo en esta pantalla
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="stHeader"] { display: none; }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # 2. Abrir el contenedor principal (el que tiene la sombra y los bordes redondos)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # 3. Crear las dos columnas (Izquierda oscura, Derecha formulario)
    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    # ==================== PANEL IZQUIERDO ====================
    with col_left:
        # Usamos una sola cadena de texto sin saltos de línea extraños para que Streamlit no se confunda
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
                        <span class="precision-badge">98% precisión</span>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(html_izq, unsafe_allow_html=True)

    # ==================== PANEL DERECHO ====================
    with col_right:
        html_der = """
        <div class="login-right">
            <p class="welcome-label">BIENVENIDO DE NUEVO</p>
            <h2 class="login-title">Inicia sesión</h2>
            <p class="login-subtitle">Ingresa tus datos para acceder a tu espacio de traducción.</p>
        </div>
        """
        st.markdown(html_der, unsafe_allow_html=True)

        # Formulario de autenticación (Streamlit-authenticator)
        authenticator.login(
            location="main",
            fields={
                "Form name": " ",  # Espacio en blanco para ocultar el título feo por defecto
                "Username": "Correo electrónico",
                "Password": "Contraseña",
                "Login": "Iniciar sesión",
            }
        )
        
        # Mostrar error si la contraseña está mal
        if st.session_state.get("authentication_status") is False:
            st.error("❌ Correo o contraseña incorrectos.")

        # Textos de la parte de abajo del formulario
        st.markdown("""
        <div class="divider">ACCESO SEGURO</div>
        <p class="secure-message">🔒 Tu información está protegida y cifrada.</p>
        """, unsafe_allow_html=True)

    # 4. Cerrar el contenedor principal
    st.markdown('</div>', unsafe_allow_html=True)