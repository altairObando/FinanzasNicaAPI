# api/Dockerfile
FROM python:3.12.16-slim

# Evita que Python escriba .pyc y fuerza salida en consola (útil para logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema para Pillow (imágenes)
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Script de arranque (migraciones + collectstatic)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# Gunicorn: servidor WSGI de producción para Django
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "finanzasnica.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3"]
