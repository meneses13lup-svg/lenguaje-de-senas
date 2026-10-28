 # SeñaVoz — Traductor de Lengua de Señas Mexicana


![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange?style=flat-square&logo=tensorflow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**SeñaVoz** es un sistema de visión por computadora que reconoce en tiempo real las letras del abecedario dactilológico de la Lengua de Señas Mexicana (LSM) a través de una cámara web y las convierte en texto en pantalla.

El proyecto fue desarrollado como parte de la materia de **Reconocimiento de Patrones** en la **Universidad Autónoma del Estado de México (UAEM) - Centro Universitario Nezahualcóyotl**.

---
##  Características principales
- **Reconocimiento en tiempo real:** Detecta 27 letras estáticas (A-Z + Ñ) usando MediaPipe Hands.
- **Red Neuronal (MLP):** Clasificación de las señas mediante un Perceptrón Multicapa entrenado con un dataset propio.
- **Interfaz amigable:** UI construida en Streamlit con diseño personalizado (CSS).
- **Autenticación:** Inicio de sesión seguro para los usuarios con contraseñas encriptadas (bcrypt).
- **Historial:** Guarda las traducciones realizadas por cada usuario en una base de datos local (SQLite).
- **Procesamiento local:** Todo ocurre en la máquina del usuario, sin enviar video a la nube (Privacidad 100% garantizada).

---
##  Stack Tecnológico

- **Lenguaje:** Python 3.11
- **Visión por Computadora:** OpenCV, MediaPipe
- **Machine Learning:** TensorFlow/Keras, Scikit-learn, Pandas, NumPy
- **Interfaz Gráfica:** Streamlit, Pillow
- **Base de Datos:** SQLite, SQLAlchemy
- **Autenticación:** Streamlit-Authenticator, Passlib (bcrypt)
- **Despliegue:** Docker, GitHub Actions (CI/CD)
- **Pruebas:** Pytest, Flake8

---
##  Estructura del Proyecto

```text
senavoz/
├── .github/workflows/   # Pipelines de CI/CD (GitHub Actions)
├── assets/              # Archivos estáticos (CSS, imágenes)
├── config/              # Configuración de autenticación (YAML)
├── data/                # Base de datos SQLite y CSV de landmarks
├── docs/                # Documentación adicional (UAT, Seguridad)
├── models/              # Modelo entrenado (.h5) y etiquetas
├── src/                 # Código fuente principal
│   ├── app.py           # Punto de entrada de Streamlit
│   ├── auth/            # Lógica de login y base de datos
│   ├── ml/              # Detección (MediaPipe) y entrenamiento
│   ├── pages/           # Pantallas de la UI
│   └── utils/           # Configuración y variables de entorno
├── tests/               # Pruebas unitarias con Pytest
├── .env.example         # Plantilla de variables de entorno
├── docker-compose.yml   # Orquestación de contenedores
├── Dockerfile           # Imagen de Docker
├── requirements.txt     # Dependencias del proyecto
└── README.md