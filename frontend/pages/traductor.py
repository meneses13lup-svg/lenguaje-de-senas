import streamlit as st

def render_traductor():
    # Barra lateral (Sidebar)
    with st.sidebar:
        st.markdown("""
        <div class="brand">
            <div class="brand-icon">🤟</div>
            <div class="brand-text">
                <h2>Seña<span>Voz</span></h2>
                <p>Comunicación sin límites</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menú de navegación (falso por ahora)
        st.button("🏠 Traductor", use_container_width=True)
        st.button("🕒 Historial", use_container_width=True)
        st.button("⚙️ Configuración", use_container_width=True)
        st.button("❓ Ayuda y soporte", use_container_width=True)
        
        st.markdown("---")
        
        # Tarjeta de consejo
        st.info("✨ **Consejo rápido**\nMantén tus manos visibles y procura tener buena iluminación.")
        
        # Botón de cerrar sesión
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state["authentication_status"] = None
            st.rerun()

    # Contenido principal
    st.markdown("""
        <p style="color: #06b6d4; font-weight: bold; font-size: 0.875rem; margin-bottom: 0;">SESIÓN NUEVA</p>
        <h1 style="margin-top: 0;">Comienza a comunicarte</h1>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📷 Vista de cámara")
        # Aquí iría el video real, por ahora una caja simulada
        st.markdown("""
        <div style="background-color: #0f172a; border-radius: 16px; height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; border: 2px dashed #06b6d4;">
            <h2 style="font-size: 4rem; margin: 0;">📷</h2>
            <h3 style="margin-top: 1rem;">Tu cámara está apagada</h3>
            <p style="color: #94a3b8;">Actívala para comenzar a reconocer y traducir tus señas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.button("📷 Activar cámara", type="primary", use_container_width=True)
        st.button("▶ Iniciar traducción", use_container_width=True)

    with col2:
        st.markdown("### ✨ Traducción")
        st.markdown('<span style="background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">ESPAÑOL</span>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; height: 250px; margin-top: 1rem;">
            <p style="font-size: 1.5rem; color: #94a3b8;">El texto aparecerá aquí...</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Palabras:** 0 | **Tiempo:** 00:00")