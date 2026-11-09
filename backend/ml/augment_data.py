import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.utils.config import Config

def augment_data():
    CSV_PATH = Path(Config.ROOT_DIR) / "data" / "landmarks.csv"
    if not CSV_PATH.exists():
        print("❌ No hay datos.")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"✅ Datos originales: {len(df)} muestras.")

    X = df.drop('label', axis=1).values
    y = df['label'].values

    # Crear datos aumentados (Ruido Gaussiano)
    X_noisy = X + np.random.normal(0, 0.01, X.shape) # Variación del 1%
    
    # Juntar originales + ruidosos
    X_final = np.vstack((X, X_noisy))
    y_final = np.concatenate((y, y))

    # Guardar el nuevo CSV
    df_augmented = pd.DataFrame(X_final, columns=df.columns[:-1])
    df_augmented['label'] = y_final
    df_augmented.to_csv(CSV_PATH, index=False)
    
    print(f"✅ Nuevo dataset creado con {len(df_augmented)} muestras (se duplicó).")
    print("👉 Ahora vuelve a correr: python backend/ml/train.py")

if __name__ == "__main__":
    augment_data()