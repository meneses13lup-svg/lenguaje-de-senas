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

# --- CLASE DE PROCESAMIENTO DE VIDEO EN VIVO ---
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model, self.encoder = load_model()
        self.model_path_mp = "hand_landmarker.task"
        
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
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
            with HandLandmarker.create_from_options(self.options) as landmarker:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
                
                # Usar timestamp actual para el video
                import time
                timestamp_ms = int(time.time() * 1000)
                detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
                
                if detection_result.hand_landmarks:
                    landmarks = detection_result.hand_landmarks[0]
                    coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
                    coords = coords - coords[0]
                    max_dist = np.max(np.linalg.norm(coords, axis=1))
                    if max_dist > 0: coords = coords / max_dist
                    
                    features = coords.flatten()
                    prediction = self.model.predict(np.expand_dims(features, axis=0), verbose=0)
                    predicted_class = np.argmax(prediction)
                    confidence = np.max(prediction) * 100
                    letra = self.encoder.inverse_transform([predicted_class])[0]
                    
                    # Dibujar en el video
                    cv2.putText(img, f"Letra: {letra} ({confidence:.1f}%)", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Guardar en sesión
                    st.session_state.letra_actual = letra
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    if "texto" not in st.session_state:
        st.session_state.texto = ""

    with st.sidebar:
        st.markdown("""
        <div class="brand">
            <div class="brand-icon">🤟</div>
            <div class="brand-text"><h2>Seña<span>Voz</span></h2></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state["authentication_status"] = None
            st.rerun()

    st.markdown("<h1>Comienza a comunicarte</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("### 📷 Cámara en vivo")
        # Componente WebRTC
        webrtc_streamer(
            key="senavoz-video",
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={"video": True, "audio": False},
        )

    with col2:
        st.markdown("### ✨ Traducción")
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; height: 200px;">
            <p style="font-size: 2rem; font-weight: bold; color: #0f172a;">{st.session_state.texto}</p>
        </div>
        """, unsafe_allow_html=True)
        
        letra = st.session_state.get("letra_actual", "")
        if letra and st.button(f"Agregar letra '{letra}' al texto"):
            st.session_state.texto += letra
            st.rerun()
            
        if st.button("🗑️ Borrar texto", use_container_width=True):
            st.session_state.texto = ""
            st.rerun()