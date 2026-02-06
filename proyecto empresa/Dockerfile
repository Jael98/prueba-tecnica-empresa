# Usamos una imagen base con Python (necesario para backend y simulador)
# y Node.js (para el frontend)
FROM python:3.11-slim AS python-base

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Etapa para el backend y simulador (Python)
FROM python-base AS python-app
WORKDIR /app

# Copiamos requirements (crearemos este archivo después)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . .

# Puerto del backend
EXPOSE 8000

# ------------------------------
# Etapa para el frontend (Node)
FROM node:20-slim AS frontend-build
WORKDIR /app

# Copiamos solo lo necesario para instalar dependencias primero (mejor cache)
COPY frontend/package*.json ./
RUN npm ci

# Copiamos el resto y construimos
COPY frontend/ ./
RUN npm run build

# ------------------------------
# Imagen final para frontend (servimos con nginx ligero)
FROM nginx:alpine AS frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

