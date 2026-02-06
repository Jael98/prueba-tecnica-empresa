# Proyecto Telemetría en Tiempo Real

Sistema completo de monitoreo de vehículos con actualización en tiempo real mediante WebSocket.

## Entregables

- `docker-compose.yml` → Orquesta los 3 servicios (backend, simulador y frontend)
- `backend/` → API FastAPI con WebSocket
- `simulator/` → Script Python que simula y envía datos de telemetría
- `frontend/` → Aplicación React que muestra el dashboard en tiempo real
- `README.md` → Esta documentación

## Tecnologías utilizadas

- Backend: FastAPI + Pydantic + Uvicorn + WebSocket
- Frontend: React + Vite
- Simulador: Python (requests para enviar datos)
- Contenedores: Docker + Docker Compose

## Cómo ejecutar

Requisitos previos:
- Docker y Docker Compose instalados
- (Opcional) Node.js y npm si quieres probar el frontend en modo desarrollo local

## Pasos:

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
2. Levantar el Docker que abrirá el simulador,el backend y React:
   ```powershell
   docker compose up --build
(La primera vez tardará varios minutos por la instalación de dependencias)

3. Abre tu navegador en:\
    http://localhost:5173 \
¡Aquí verás el dashboard completo con los datos actualizándose en tiempo real!

4. (Opcional) Consultar la API manualmente:
- Abre en el navegador: http://localhost:8000/docs (Swagger UI)
- Puedes probar el endpoint POST /ingest directamente desde la interfaz


Los servicios se comunican automáticamente:

- El simulador envía datos al backend cada 0.5 segundos
- El frontend se conecta por ***WebSocket*** al backend
  
Para detener el contenedor:

Presiona estas teclas para interrumpir (en la terminal donde está corriendo)\
   Ctrl + C


Una vez detenido, o desde otra terminal:


docker compose down



## Cómo probar

1. Ver que el simulador envía datos \
En los logs del contenedor simulator verás: \
✓ Datos enviados OK (status 201)

2. Probar el endpoint manualmente (opcional con curl o Swagger) \
Desde tu máquina (mientras Docker está corriendo): 
  ```powershell
  curl -X POST "http://localhost:8000/ingest" `
  -H "Content-Type: application/json" `
  -d '{
    "vehicle_id": "veh-test",
    "ts": "2026-02-06T18:00:00Z",
    "speed_kmh": 60.5,
    "temperature_c": 25.3,
    "battery_pct": 85.0,
    "gps": {"lat": 40.4168, "lon": -3.7038},
    "status": "moving"
  }'

Respuesta esperada:
JSON{"saved": true}

3. Ver el dashboard
Abre http://localhost:5173
Deberías ver:
Estado: Conectado ✅
Tarjeta del vehículo con velocidad, batería, temperatura, GPS y timestamp actualizándose


