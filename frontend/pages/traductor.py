import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
import mediapipe as mp
import numpy as np
import joblib
import tensorflow as tf
from pathlib import Path
import sys
import os
import av
import time

# Conectar con la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

@st.cache_resource
def load_model():
    model_path = Path(Config.ROOT_DIR) / "models" / "model.h5"
    labels_path = Path(Config.ROOT_DIR) / "models" / "labels.pkl"
    if model_path.exists() and labels_path.exists():
        model = tf.keras.models.load_model(str(model_path))
        encoder = joblib.load(str(labels_path))
        return model, encoder
    return None, None

# --- CLASE DE PROCESAMIENTO DE VIDEO EN VIVO (WEBRTC) ---
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model, self.encoder = load_model()
        
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        self.model_path_mp = "hand_landmarker.task"
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path_mp),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.7
        )

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        
        if self.model is not None:
            import mediapipe as mp
            from mediapipe.tasks.python import vision
            
            with vision.HandLandmarker.create_from_options(self.options) as landmarker:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
                
                timestamp_ms = int(time.time() * 1000)
                detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
                
                if detection_result.hand_landmarks:
                    landmarks = detection_result.hand_landmarks[0]
                    coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
                    coords = coords - coords[0]
                    max_dist = np.max(np.linalg.norm(coords, axis=1))
                    if max_dist > 0:
                        coords = coords / max_dist
                    
                    features = coords.flatten()
                    prediction = self.model.predict(np.expand_dims(features, axis=0), verbose=0)
                    predicted_class = np.argmax(prediction)
                    confidence = np.max(prediction) * 100
                    
                    if confidence > 70:
                        letra = self.encoder.inverse_transform([predicted_class])[0]
                        cv2.putText(img, f"Letra: {letra} ({confidence:.1f}%)", (20, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        st.session_state.letra_actual = letra
                    else:
                        cv2.putText(img, "Analizando...", (20, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        st.session_state.letra_actual = ""
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    st.session_state.letra_actual = ""

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    # Inicializar variables en sesión
    if "texto" not in st.session_state:
        st.session_state.texto = ""
    if "letra_actual" not in st.session_state:
        st.session_state.letra_actual = ""
    if "ultima_letra_agregada" not in st.session_state:
        st.session_state.ultima_letra_agregada = ""

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

    # --- CSS PARA MEJORAR EL DISEÑO DEL DASHBOARD ---
    st.markdown("""
    <style>
        .camara-card {
            background: white;
            border-radius: 16px;
            padding: 16px;
            border: 2px solid #06b6d4;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .traduccion-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            min-height: 300px;
            display: flex;
            flex-direction: column;
        }
        .texto-traducido {
            font-size: 2.5rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            word-wrap: break-word;
        }
        button[title="View fullscreen"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown("### 📷 Vista de cámara")
        
        # Envolver el video en el contenedor con clase CSS
        st.markdown('<div class="camara-card">', unsafe_allow_html=True)
        
        webrtc_streamer(
            key="senavoz-video",
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={"video": True, "audio": False},
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### ✨ Traducción")
        
        # Lógica para agregar letra automáticamente
        letra_actual = st.session_state.get("letra_actual", "")
        
        if letra_actual and letra_actual != st.session_state.ultima_letra_agregada:
            st.session_state.texto += letra_actual
            st.session_state.ultima_letra_agregada = letra_actual
            st.rerun() 
            
        if not letra_actual:
             st.session_state.ultima_letra_agregada = ""

        # Renderizar la tarjeta de traducción
        texto_actual = st.session_state.texto if st.session_state.texto else "El texto aparecerá aquí..."
        color_texto = "#0f172a" if st.session_state.texto else "#94a3b8"
        
        st.markdown(f"""
        <div class="traduccion-card">
            <div style="margin-bottom: 10px;">
                <span style="background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; color: #475569;">ESPAÑOL</span>
            </div>
            <div class="texto-traducido" style="color: {color_texto};">
                {texto_actual}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Botón para borrar texto
        if st.button("🗑️ Borrar texto", use_container_width=True):
            st.session_state.texto = ""
            st.session_state.letra_actual = ""
            st.session_state.ultima_letra_agregada = ""
            st.rerun()