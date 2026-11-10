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

# Inicializar shared_data de forma global para evitar errores en WebRTC
if "shared_data" not in st.session_state:
    st.session_state.shared_data = {"letra": "", "timestamp": 0.0}

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
        
        # Nos aseguramos de que shared_data exista en el hilo del video
        if "shared_data" not in st.session_state:
            st.session_state.shared_data = {"letra": "", "timestamp": 0.0}
        
        import mediapipe as mp
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
                    confidence = np.max(prediction) * 100
                    
                    if confidence > 70:
                        letra = self.encoder.inverse_transform([np.argmax(prediction)])[0]
                        cv2.putText(img, f"Letra: {letra} ({confidence:.1f}%)", (20, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Guardar de forma segura
                        st.session_state.shared_data["letra"] = letra
                        st.session_state.shared_data["timestamp"] = time.time()
                    else:
                        cv2.putText(img, "Analizando...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    # Inicializar variables en sesión
    if "texto" not in st.session_state:
        st.session_state.texto = ""
    if "ultima_letra_agregada" not in st.session_state:
        st.session_state.ultima_letra_agregada = ""
    if "shared_data" not in st.session_state:
        st.session_state.shared_data = {"letra": "", "timestamp": 0.0}

    # --- BARRA LATERAL ---
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

    # --- DISEÑO CSS ---
    st.markdown("""
    <style>
        .card-traduccion {
            background: #ffffff;
            border-radius: 20px;
            padding: 30px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            min-height: 350px;
            display: flex;
            flex-direction: column;
        }
        .badge-idioma {
            background-color: #f1f5f9; 
            padding: 6px 12px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            font-weight: 700; 
            color: #475569;
            display: inline-block;
            margin-bottom: 20px;
        }
        .texto-detectado {
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            word-wrap: break-word;
        }
        .texto-vacio {
            font-size: 2rem;
            font-weight: 500;
            color: #cbd5e1;
            line-height: 1.4;
        }
        button[title="View fullscreen"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p style="color: #06b6d4; font-weight: bold; font-size: 0.875rem; margin-bottom: 0;">SESIÓN NUEVA</p>', unsafe_allow_html=True)
    st.markdown('<h1 style="margin-top: 0; font-size: 2.5rem; font-weight: 800;">Comienza a comunicarte</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        st.markdown("### 📷 Cámara en vivo")
        webrtc_streamer(
            key="senavoz-video",
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
        )

    with col2:
        st.markdown("### ✨ Traducción")
        
        # Leer la letra desde el hilo del video
        letra_detectada = st.session_state.shared_data.get("letra", "")
        timestamp_letra = st.session_state.shared_data.get("timestamp", 0)
        
        # Lógica: Si la letra es nueva y tiene menos de 2 segundos de antigüedad, la agregamos
        if letra_detectada and letra_detectada != st.session_state.ultima_letra_agregada:
            st.session_state.texto += letra_detectada
            st.session_state.ultima_letra_agregada = letra_detectada
            st.rerun() # Fuerza a la pantalla a actualizarse

        # Si la mano no se detecta por más de 1.5 segundos, reseteamos la última letra
        if time.time() - timestamp_letra > 1.5:
            st.session_state.ultima_letra_agregada = ""

        # Renderizar la tarjeta de texto
        texto_mostrar = st.session_state.texto if st.session_state.texto else "El texto aparecerá aquí..."
        clase_texto = "texto-detectado" if st.session_state.texto else "texto-vacio"
        
        st.markdown(f"""
        <div class="card-traduccion">
            <div><span class="badge-idioma">ESPAÑOL</span></div>
            <div class="{clase_texto}">{texto_mostrar}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️ Borrar texto", use_container_width=True):
            st.session_state.texto = ""
            st.session_state.shared_data["letra"] = ""
            st.session_state.ultima_letra_agregada = ""
            st.rerun()