from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, field_validator, ValidationError
from datetime import datetime
import json
from fastapi import HTTPException, status as http_status

app = FastAPI()

# Aquí guardaremos la última telemetría por vehículo en memoria (un dict simple)
telemetry_storage = {}  # clave: vehicle_id, valor: dict de telemetría

# Lista para manejar conexiones WebSocket (para broadcast a múltiples clientes)
websocket_connections = []

class GPS(BaseModel):
    lat: float
    lon: float

    @field_validator('lat')
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('lon')
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class Telemetry(BaseModel):
    vehicle_id: str
    battery_pct: float
    gps: GPS
    status: str
    ts: str
    speed_kmh: float          # ← nuevo
    temperature_c: float      # ← nuevo

    @field_validator('battery_pct')
    @classmethod
    def validate_battery(cls, v: float) -> float:
        if not 0 <= v <= 100:
            raise ValueError('battery_pct must be between 0 and 100')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ['moving', 'stopped']:
            raise ValueError('status must be "moving" or "stopped"')
        return v

    @field_validator('ts')
    @classmethod
    def validate_ts(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('ts must be a valid ISO datetime string')
        return v

    @field_validator('speed_kmh')
    @classmethod
    def validate_speed(cls, v: float) -> float:
        if v < 0:
            raise ValueError('speed_kmh cannot be negative')
        return v

    @field_validator('temperature_c')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not -50 <= v <= 100:  # rango razonable para temperatura en vehículos
            raise ValueError('temperature_c must be between -50 and 100 °C')
        return v
    
    
@app.post("/ingest", status_code=http_status.HTTP_201_CREATED)
async def ingest_telemetry(telemetry: Telemetry):
    try:
        # Guardar en memoria (última por vehículo)
        telemetry_storage[telemetry.vehicle_id] = telemetry.dict()

        # Emitir a WebSocket (broadcast a todos los clientes conectados)
        payload_json = json.dumps(telemetry.dict())
        for connection in websocket_connections[:]:  # Copia para evitar errores durante iteración
            try:
                await connection.send_text(payload_json)
            except WebSocketDisconnect:
                websocket_connections.remove(connection)

        return {"saved": True}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            # Espera mensajes (aunque no los usemos, para mantener la conexión viva)
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        
    