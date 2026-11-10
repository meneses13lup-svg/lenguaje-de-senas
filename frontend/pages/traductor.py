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

# Variables globales
if "texto" not in st.session_state:
    st.session_state.texto = ""
if "letra_detectada" not in st.session_state:
    st.session_state.letra_detectada = ""

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
                        
                        # Guardamos en la sesión global
                        st.session_state.letra_detectada = letra
                    else:
                        cv2.putText(img, "Analizando...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    cv2.putText(img, "Mano no detectada", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    st.session_state.letra_detectada = ""

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def render_traductor():
    # --- DISEÑO CSS PREMIUM ---
    st.markdown("""
    <style>
        /* Ocultar el menú de Streamlit y el pie de página */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Panel de traducción estilo Neón/Oscuro */
        .panel-traduccion {
            background: linear-gradient(145deg, #0f172a, #1e293b);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
            min-height: 400px;
            display: flex;
            flex-direction: column;
            border: 1px solid #334155;
            position: relative;
            overflow: hidden;
        }
        
        /* Efecto de luz brillante en la esquina */
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
            letter-spacing: 0.1em;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
        }

        .texto-traducido {
            font-size: 3.5rem;
            font-weight: 900;
            line-height: 1.1;
            font-family: 'Inter', sans-serif;
            word-wrap: break-word;
            z-index: 10;
            color: #ffffff;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }

        .texto-vacio {
            font-size: 2rem;
            font-weight: 500;
            color: #64748b;
            line-height: 1.4;
            z-index: 10;
            font-style: italic;
        }

        .letra-detectada-badge {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: #06b6d4;
            color: #0f172a;
            padding: 10px 20px;
            border-radius: 12px;
            font-weight: 900;
            font-size: 1.5rem;
            box-shadow: 0 0 20px rgba(6,182,212,0.5);
        }
        
        /* Mejorar el aspecto del contenedor del video */
        .stVideoProcessor {
            border-radius: 20px;
            overflow: hidden;
            border: 2px solid #1e293b;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
    </style>
    """, unsafe_allow_html=True)

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px;">
            <div style="background: #06b6d4; width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 15px rgba(6,182,212,0.4);">🤟</div>
            <div>
                <h2 style="margin: 0; color: #0f172a; font-size: 1.4rem; font-weight: 800;">Seña<span style="color: #06b6d4;">Voz</span></h2>
                <p style="margin: 0; color: #64748b; font-size: 0.65rem; letter-spacing: 0.1em; font-weight: 700;">SIN LÍMITES</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state["authentication_status"] = None
            st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    st.markdown("""
        <p style="color: #06b6d4; font-weight: 800; font-size: 0.85rem; margin-bottom: 5px; letter-spacing: 0.1em;">SESIÓN NUEVA</p>
        <h1 style="margin-top: 0; font-size: 2.8rem; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; margin-bottom: 2rem;">Comienza a comunicarte</h1>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

    # --- COLUMNA IZQUIERDA: CÁMARA ---
    with col1:
        st.markdown("### 📷 Cámara en vivo")
        
        # Usamos un contenedor para que WebRTC se vea bien
        with st.container():
            webrtc_streamer(
                key="senavoz-video",
                video_processor_factory=VideoProcessor,
                rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
                media_stream_constraints={"video": True, "audio": False},
            )

    # --- COLUMNA DERECHA: TRADUCCIÓN ---
    with col2:
        st.markdown("### ✨ Traducción")
        
        # Lógica para agregar letra automáticamente
        letra = st.session_state.get("letra_detectada", "")
        
        # Si la letra cambió y es válida, la agregamos al texto
        if letra and letra != st.session_state.get("ultima_letra", ""):
            st.session_state.texto += letra
            st.session_state.ultima_letra = letra
            st.rerun() # Recarga la pantalla para mostrar el nuevo texto
        
        # Si no hay letra, reseteamos el bloqueo para permitir escribir la misma letra otra vez
        if not letra:
            st.session_state.ultima_letra = ""

        # Determinar qué mostrar
        texto_mostrar = st.session_state.texto if st.session_state.texto else "El texto aparecerá aquí..."
        clase_texto = "texto-traducido" if st.session_state.texto else "texto-vacio"
        
        # HTML del panel con el diseño bonito
        st.markdown(f"""
        <div class="panel-traduccion">
            <div><span class="badge-idioma">ESPAÑOL</span></div>
            <div class="{clase_texto}">{texto_mostrar}</div>
            {f'<div class="letra-detectada-badge">Última letra: {letra}</div>' if letra else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Botón para borrar texto
        if st.button("🗑️ Borrar todo el texto", use_container_width=True, type="primary"):
            st.session_state.texto = ""
            st.session_state.letra_detectada = ""
            st.session_state.ultima_letra = ""
            st.rerun()