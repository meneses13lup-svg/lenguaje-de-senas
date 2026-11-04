import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time
from pathlib import Path
import sys

# Conectar con la raíz para guardar el CSV en data/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

# --- NUEVA API DE MEDIAPIPE (Tasks) ---
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Configurar el modelo
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# Archivo donde guardaremos los datos
CSV_PATH = Path(Config.ROOT_DIR) / "data" / "landmarks.csv"

# Crear el encabezado del CSV si no existe
if not CSV_PATH.exists():
    with open(CSV_PATH, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = [f"{axis}{i}" for i in range(21) for axis in ['x', 'y', 'z']]
        header.append('label')
        writer.writerow(header)
    print(f"✅ Archivo creado en {CSV_PATH}")

def extract_landmarks(landmarks):
    """Extrae y normaliza los 21 puntos (63 coordenadas)."""
    coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
    # Centrar en la muñeca (punto 0)
    coords = coords - coords[0]
    # Escalar para que sea independiente de la distancia
    max_dist = np.max(np.linalg.norm(coords, axis=1))
    if max_dist > 0:
        coords = coords / max_dist
    return coords.flatten()

def main():
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)
    print("\n🎥 Cámara encendida.")
    print("👉 INSTRUCCIONES:")
    print("1. Presiona una TECLA (A-Z) para seleccionar qué letra vas a grabar.")
    print("2. Haz la seña frente a la cámara.")
    print("3. Presiona 's' para GUARDAR 50 muestras automáticas de esa letra.")
    print("4. Presiona 'q' para SALIR.\n")

    current_letter = None
    guardando = False
    muestras_guardadas = 0
    timestamp_ms = 0

    # Iniciar el detector de manos
    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1) # Efecto espejo
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convertir a formato MediaPipe
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detectar manos
            timestamp_ms += 33 # Simular ~30 FPS
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            landmarks = None
            if detection_result.hand_landmarks:
                hand_landmarks = detection_result.hand_landmarks[0]
                # Dibujar puntos manualmente (la nueva API no trae dibujador por defecto)
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                
                landmarks = extract_landmarks(hand_landmarks)

            # Mostrar texto en pantalla
            color = (0, 255, 0) if current_letter else (0, 0, 255)
            texto = f"Letra: {current_letter if current_letter else 'Ninguna'}"
            cv2.putText(frame, texto, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            if guardando and landmarks is not None:
                with open(CSV_PATH, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    row = list(landmarks) + [current_letter]
                    writer.writerow(row)
                muestras_guardadas += 1
                cv2.putText(frame, f"Guardando: {muestras_guardadas}/50", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                
                if muestras_guardadas >= 50:
                    guardando = False
                    muestras_guardadas = 0
                    print(f"✅ 50 muestras guardadas para la letra {current_letter}")

            cv2.imshow("Recolector de Datos - SeñaVoz", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and landmarks is not None and current_letter:
                guardando = True
                muestras_guardadas = 0
                print(f"⏳ Grabando 50 muestras para la letra {current_letter}...")
            elif 65 <= key <= 90 or 97 <= key <= 122:
                current_letter = chr(key).upper()
                print(f"🔤 Letra seleccionada: {current_letter}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()