FROM python:3.11
WORKDIR /app

# ESTA LÍNEA ES LA QUE FALTA
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY exe/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "fullstack/app.py", "--server.port=8501", "--server.address=0.0.0.0"]