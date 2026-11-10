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

# Cargar el modelo
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
                        # Actualizamos la variable global de Streamlit
                        st.session_state.letra_actual = letra
                        st.session_state.ultimo_timestamp = time.time()
                    else:
                        cv2.putText(img, "Analizando...", (20, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        if time.time() - st.session_state.get("ultimo_timestamp", 0) > 1.0:
                            st.session_state.letra_actual = ""
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    if time.time() - st.session_state.get("ultimo_timestamp", 0) > 1.0:
                        st.session_state.letra_actual = ""

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    if "texto" not in st.session_state:
        st.session_state.texto = ""
    if "letra_actual" not in st.session_state:
        st.session_state.letra_actual = ""
    if "ultima_letra_agregada" not in st.session_state:
        st.session_state.ultima_letra_agregada = ""

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

    # --- CSS PARA EL DASHBOARD ---
    st.markdown("""
    <style>
        .title-sesion {
            color: #06b6d4; font-weight: bold; font-size: 0.875rem; margin-bottom: 0; letter-spacing: 0.05em;
        }
        .title-principal {
            margin-top: 0; font-size: 2.5rem; font-weight: 800; color: #0f172a; margin-bottom: 2rem;
        }
        .card-traduccion {
            background: #ffffff;
            border-radius: 20px;
            padding: 30px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            min-height: 350px;
            display: flex;
            flex-direction: column;
            position: relative;
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
            letter-spacing: 0.05em;
        }
        .texto-detectado {
            font-size: 2.8rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            word-wrap: break-word;
            font-family: 'Inter', sans-serif;
        }
        .texto-vacio {
            font-size: 2rem;
            font-weight: 500;
            color: #cbd5e1;
            line-height: 1.4;
        }
        /* Estilo para el contenedor de WebRTC */
        .stVideoProcessor > div {
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        button[title="View fullscreen"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENIDO PRINCIPAL ---
    st.markdown('<p class="title-sesion">SESIÓN NUEVA</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="title-principal">Comienza a comunicarte</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1], gap="large")

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
        
        # Lógica para agregar letra automáticamente
        letra_actual = st.session_state.get("letra_actual", "")
        
        if letra_actual and letra_actual != st.session_state.ultima_letra_agregada:
            st.session_state.texto += letra_actual
            st.session_state.ultima_letra_agregada = letra_actual
            st.rerun() 
            
        if not letra_actual:
             st.session_state.ultima_letra_agregada = ""

        # Determinar si hay texto para mostrar
        texto_mostrar = st.session_state.texto
        if texto_mostrar:
            clase_texto = "texto-detectado"
        else:
            texto_mostrar = "El texto aparecerá aquí..."
            clase_texto = "texto-vacio"
        
        # Renderizar Tarjeta
        st.markdown(f"""
        <div class="card-traduccion">
            <div><span class="badge-idioma">ESPAÑOL</span></div>
            <div class="{clase_texto}">{texto_mostrar}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Botón para borrar texto
        if st.button("🗑️ Borrar texto", use_container_width=True):
            st.session_state.texto = ""
            st.session_state.letra_actual = ""
            st.session_state.ultima_letra_agregada = ""
            st.rerun()