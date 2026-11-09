import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from pathlib import Path
import sys

# Conectar con la raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

def train_model():
    # 1. Cargar datos
    CSV_PATH = Path(Config.ROOT_DIR) / "data" / "landmarks.csv"
    if not CSV_PATH.exists():
        print("❌ No hay datos. Corre collect_data.py primero.")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"✅ Datos cargados: {len(df)} muestras.")

    # Separar características (X) y etiquetas (y)
    X = df.drop('label', axis=1).values
    y = df['label'].values

    # 2. Codificar las etiquetas (A, B, C... a 0, 1, 2...)
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    num_classes = len(encoder.classes_)
    y_categorical = to_categorical(y_encoded, num_classes=num_classes)
    
    print(f"✅ Letras detectadas en el dataset: {encoder.classes_}")

    # 3. Dividir datos (70% entrenamiento, 15% validación, 15% prueba)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y_categorical, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    # 4. Crear la Red Neuronal (MLP)
    model = Sequential([
        Dense(128, activation='relu', input_shape=(63,)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    # 5. Entrenar
    print("⏳ Entrenando la red neuronal...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=32,
        verbose=1
    )

    # 6. Evaluar
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"\n🎯 Precisión final (Accuracy): {accuracy*100:.2f}%")

    # 7. Guardar el modelo y el codificador de letras
    model.save(os.path.join(Config.ROOT_DIR, "models", "model.h5"))
    joblib.dump(encoder, os.path.join(Config.ROOT_DIR, "models", "labels.pkl"))
    print("✅ Modelo guardado en models/model.h5")
    print("✅ Etiquetas guardadas en models/labels.pkl")

if __name__ == "__main__":
    train_model()