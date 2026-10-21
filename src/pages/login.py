import streamlit as st

def render_waveform():
    heights = [32, 58, 42, 80, 55, 92, 65, 40, 72, 88, 48, 62, 36, 70, 52, 84, 44, 64, 34, 54]
    bars = "".join(f'<span style="height: {h}%; animation-delay: {i * 0.05}s;"></span>' for i, h in enumerate(heights))
    st.markdown(f'<div class="waveform">{bars}</div>', unsafe_allow_html=True)

def render_login_left():
    st.markdown("""
    <div class="login-left">
        <div class="brand">
            <div class="brand-icon">
                <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
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
            <p>Convierte el lenguaje de señas en texto y audio de forma clara, rápida y accesible.</p>
            <div class="status-card">
                <div class="status-header">
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <span>Reconocimiento activo</span>
                    </div>
                    <span class="precision-badge">98% precisión</span>
                </div>
                <div id="waveform-container"></div>
            </div>
        </div>
        <p class="login-footer">© 2025 SeñaVoz · Tecnología para todos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inyectar el waveform
    st.markdown("""
    <script>
        const wf = document.getElementById('waveform-container');
        if (wf && !wf.hasChildNodes()) {
            const heights = [32, 58, 42, 80, 55, 92, 65, 40, 72, 88, 48, 62, 36, 70, 52, 84, 44, 64, 34, 54];
            const div = document.createElement('div');
            div.className = 'waveform';
            heights.forEach((h, i) => {
                const bar = document.createElement('span');
                bar.style.height = h + '%';
                bar.style.animationDelay = (i * 0.05) + 's';
                div.appendChild(bar);
            });
            wf.appendChild(div);
        }
    </script>
    """, unsafe_allow_html=True)

def render_login_right(authenticator):
    st.markdown('<div class="login-right"><div class="login-form-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="welcome-label">BIENVENIDO DE NUEVO</p>', unsafe_allow_html=True)
    st.markdown('<h2 class="login-title">Inicia sesión</h2>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Ingresa tus datos para acceder a tu espacio de traducción.</p>', unsafe_allow_html=True)

    authenticator.login(
        location="main",
        fields={
            "Form name": "Iniciar sesión",
            "Username": "Correo electrónico",
            "Password": "Contraseña",
            "Login": "Iniciar sesión",
        },
        key="login_form",
    )
    
    st.markdown("""<div class="divider"><span></span><em>ACCESO SEGURO</em><span></span></div>""", unsafe_allow_html=True)
    st.markdown("""<p class="secure-message">🔒 Tu información está protegida y cifrada.</p>""", unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

def render_login(authenticator):
    col_left, col_right = st.columns([1.05, 0.95], gap="small")
    with col_left:
        render_login_left()
    with col_right:
        render_login_right(authenticator)