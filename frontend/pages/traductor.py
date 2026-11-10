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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

# 1. El archivo donde la cámara escribirá la letra
ARCHIVO_LETRA = "letra_actual.txt"

if "texto" not in st.session_state:
    st.session_state.texto = ""
if "ultima_letra" not in st.session_state:
    st.session_state.ultima_letra = ""

@st.cache_resource
def load_model():
    model_path = Path(Config.ROOT_DIR) / "models" / "model.h5"
    labels_path = Path(Config.ROOT_DIR) / "models" / "labels.pkl"
    if model_path.exists() and labels_path.exists():
        model = tf.keras.models.load_model(str(model_path))
        encoder = joblib.load(str(labels_path))
        return model, encoder
    return None, None

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model, self.encoder = load_model()
        
        import mediapipe as mp
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        self.options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
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
                    
                    prediction = self.model.predict(np.expand_dims(coords.flatten(), axis=0), verbose=0)
                    confidence = np.max(prediction) * 100
                    
                    if confidence > 70:
                        letra = self.encoder.inverse_transform([np.argmax(prediction)])[0]
                        cv2.putText(img, f"Letra: {letra} ({confidence:.1f}%)", (20, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # 2. ESCRIBIR LA LETRA EN EL ARCHIVO DE TEXTO
                        try:
                            with open(ARCHIVO_LETRA, "w") as f:
                                f.write(letra)
                        except:
                            pass
                    else:
                        cv2.putText(img, "Analizando...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    # --- DISEÑO CSS ---
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
        .panel-traduccion {
            background: linear-gradient(145deg, #0f172a, #1e293b);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.3);
            min-height: 400px;
            display: flex;
            flex-direction: column;
            border: 1px solid #334155;
            position: relative;
            overflow: hidden;
        }
        .panel-traduccion::before {
            content: '';
            position: absolute;
            top: -50px; right: -50px;
            width: 150px; height: 150px;
            background: #06b6d4;
            filter: blur(80px);
            opacity: 0.2;
            border-radius: 50%;
        }
        .badge-idioma {
            background-color: rgba(6, 182, 212, 0.15);
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            color: #22d3ee;
            display: inline-block;
            margin-bottom: 25px;
        }
        .texto-traducido { font-size: 3.5rem; font-weight: 900; line-height: 1.1; color: #ffffff; }
        .texto-vacio { font-size: 2rem; font-weight: 500; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown('<h2 style="margin:0; font-weight: 900; color:#0f172a;">Traductor en vivo</h2>', unsafe_allow_html=True)
    with col_header2:
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state["authentication_status"] = None
            st.rerun()

    st.markdown('<h1 style="margin-top: 1rem; font-size: 2.8rem; font-weight: 900; color: #0f172a;">Comienza a comunicarte</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

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
        
        # 3. LEER LA LETRA DEL ARCHIVO CUANDO SE PRESIONA EL BOTÓN
        if st.button("🔄 Capturar Letra", use_container_width=True, type="primary"):
            try:
                if os.path.exists(ARCHIVO_LETRA):
                    with open(ARCHIVO_LETRA, "r") as f:
                        letra_leida = f.read().strip()
                        if letra_leida:
                            st.session_state.texto += letra_leida
                            st.session_state.ultima_letra = letra_leida
                            # Borramos el archivo para que no se repita la letra
                            os.remove(ARCHIVO_LETRA)
                            st.rerun()
            except Exception as e:
                st.error(f"Error al leer: {e}")

        texto_mostrar = st.session_state.texto if st.session_state.texto else "El texto aparecerá aquí..."
        clase_texto = "texto-traducido" if st.session_state.texto else "texto-vacio"
        
        st.markdown(f"""
        <div class="panel-traduccion">
            <div><span class="badge-idioma">ESPAÑOL</span></div>
            <div class="{clase_texto}">{texto_mostrar}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️ Borrar todo el texto", use_container_width=True):
            st.session_state.texto = ""
            st.session_state.ultima_letra = ""
            if os.path.exists(ARCHIVO_LETRA):
                os.remove(ARCHIVO_LETRA)
            st.rerun()