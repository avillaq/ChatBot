FROM python:3.9-slim

# Metadatos
LABEL maintainer="ChatBot P2P Financiero"
LABEL description="Nodo P2P Financiero con Interfaz Web"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar datos NLTK necesarios
RUN python -c "import nltk; nltk.download('punkt')"

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs

# Variables de entorno configurables
ENV NODE_PORT=8000
ENV NODE_NAME=Banco_Principal
ENV WEB_PORT=5000
ENV CONFIG_FILE=/app/config.json

# Exponer puertos
EXPOSE 5000 8000

# Comando por defecto
CMD ["python", "app/app.py"]