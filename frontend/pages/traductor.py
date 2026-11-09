import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import joblib
import tensorflow as tf
from pathlib import Path
import sys
import os

# Conectar con la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

# Cargar modelo y etiquetas
@st.cache_resource
def load_model():
    model_path = Path(Config.ROOT_DIR) / "models" / "model.h5"
    labels_path = Path(Config.ROOT_DIR) / "models" / "labels.pkl"
    if model_path.exists() and labels_path.exists():
        model = tf.keras.models.load_model(str(model_path))
        encoder = joblib.load(str(labels_path))
        return model, encoder
    return None, None

# --- NUEVA API DE MEDIAPIPE ---
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path_mp = "hand_landmarker.task"
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path_mp),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7
)

def extract_landmarks(landmarks):
    coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
    coords = coords - coords[0]
    max_dist = np.max(np.linalg.norm(coords, axis=1))
    if max_dist > 0:
        coords = coords / max_dist
    return coords.flatten()

def render_traductor():
    # Inicializar variables en sesión
    if "texto" not in st.session_state:
        st.session_state.texto = ""

    # Barra lateral
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
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state["authentication_status"] = None
            st.rerun()

    # Contenido principal
    st.markdown("""
        <p style="color: #06b6d4; font-weight: bold; font-size: 0.875rem; margin-bottom: 0;">SESIÓN NUEVA</p>
        <h1 style="margin-top: 0;">Comienza a comunicarte</h1>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])
    
    model, encoder = load_model()

    with col1:
        st.markdown("### 📷 Vista de cámara")
        
        # Widget nativo de Streamlit para foto
        foto = st.camera_input("Haz una seña y toma la foto", label_visibility="collapsed")
        
        if foto is not None and model is not None:
            # Convertir la foto a formato OpenCV
            bytes_data = foto.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # --- INICIO DEL PARCHE PARA DOCKER ---
            # Detecta si estamos dentro de un contenedor Docker
            en_docker = os.path.exists('/.dockerenv') 
            
            if en_docker:
                st.error("🚨 El reconocimiento de cámara no está disponible en este entorno de Docker.")
                st.info("La librería gráfica 'libEGL' no está disponible en contenedores Windows. Corre la app localmente con 'python -m streamlit run fullstack/app.py' para usar la cámara.")
                return # Detiene la ejecución aquí para que no explote
            # --- FIN DEL PARCHE ---

            # Procesar con MediaPipe
            with HandLandmarker.create_from_options(options) as landmarker:
                rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
                detection_result = landmarker.detect(mp_image)
                
                if detection_result.hand_landmarks:
                    landmarks = extract_landmarks(detection_result.hand_landmarks[0])
                    # Predecir con la Red Neuronal
                    prediction = model.predict(np.expand_dims(landmarks, axis=0), verbose=0)
                    predicted_class = np.argmax(prediction)
                    confidence = np.max(prediction) * 100
                    letra = encoder.inverse_transform([predicted_class])[0]
                    
                    st.success(f"✅ Letra detectada: **{letra}** (Confianza: {confidence:.1f}%)")
                    
                    # Agregar al texto
                    if st.button("Agregar al texto"):
                        st.session_state.texto += letra
                        st.rerun()
                else:
                    st.warning("⚠️ No se detectó ninguna mano en la foto. Intenta de nuevo.")

    with col2:
        st.markdown("### ✨ Traducción")
        st.markdown('<span style="background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">ESPAÑOL</span>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; height: 200px; margin-top: 1rem;">
            <p style="font-size: 2rem; font-weight: bold; color: #0f172a;">{st.session_state.texto}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Borrar texto", use_container_width=True):
            st.session_state.texto = ""
            st.rerun()