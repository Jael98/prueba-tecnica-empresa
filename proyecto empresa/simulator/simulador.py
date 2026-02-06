import random
import math
from datetime import datetime, timezone
import requests
import json
import time

BACKEND_URL = "http://api:8000/ingest"

def enviar_al_backend(vehiculo):
    """Envía el estado actual del vehículo al backend"""
    try:
        response = requests.post(
            BACKEND_URL,
            json=vehiculo,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            print(f"✓ Datos enviados OK (status {response.status_code})")
        else:
            print(f"✗ Error al enviar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error de conexión al backend: {e}")

def actualizar_timestamp(vehiculo):
    vehiculo["ts"] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    
def cambio_gps(vehiculo):
    #Simularemos que siempre va para una dirrecion de 60 grados para simplificar operaciones
    velocidad_m_s=vehiculo["speed_kmh"]*(1000/3600)#pasamos la velocidad de km/h a m/s
    distancia_recorrida=velocidad_m_s*0.5
    lat=(distancia_recorrida * math.cos(math.radians(60))) / 111195
    lon = (distancia_recorrida * math.sin(math.radians(60))) / (111195 * math.cos(vehiculo["gps"]["lat"] * math.pi/180))
    
    
    vehiculo["gps"]["lat"] += lat
    vehiculo["gps"]["lon"] += lon
    
    
    
def descarga_bateria(vehiculo):
    
    if vehiculo["speed_kmh"] > 0:
        consumo = 0.02 + (vehiculo["speed_kmh"] / 100) * 0.08   # 2–10% por minuto aprox
    else:
        consumo = 0.005   # consumo en parado (sistemas, etc)
    vehiculo["battery_pct"] -= consumo * 0.5   # por cada medio segundo
    vehiculo["battery_pct"] = max(0, vehiculo["battery_pct"])
def temperatura(vehiculo):
    
    base = 20.0
    factor_vel = vehiculo["speed_kmh"] * 0.08   # 100 km/h → +8 °C aprox
    ruido = random.uniform(-0.4, 0.4)
    target = base + factor_vel + ruido
    
    # Suavizado
    vehiculo["temperature_c"] += (target - vehiculo["temperature_c"]) * 0.15#Calculos simplificados sacados de grok

def acelerar(vehiculo,velocidad):
    
    if vehiculo["speed_kmh"]>=220:#La velocidad maxima para que no pueda pillar mas y se le vaya demasiado
        
        vehiculo["speed_kmh"]=220
        return vehiculo["speed_kmh"]
    
    vehiculo["speed_kmh"] += velocidad
    
    cambio_gps(vehiculo)#Con esto cambiaremos el GPS con la velocidad al acelerar
    return vehiculo["speed_kmh"]

def frenar(vehiculo,velocidad):
    
    if (vehiculo["speed_kmh"] - velocidad) > 0:
        
        vehiculo["speed_kmh"] -= velocidad
        cambio_gps(vehiculo)#Con esto cambiaremos el GPS al frenar
        
    else: 
        vehiculo["speed_kmh"]=0
        
    return vehiculo["speed_kmh"]

def comprobar_velocidad(vehiculo):
    
    if vehiculo["speed_kmh"]==0:
        
        vehiculo["status"]="stopped"
    
    else:
        
        vehiculo["status"]="moving"

def comportamiento(vehiculo):
    comprobar_velocidad(vehiculo)
    
    if vehiculo["status"].lower()== "moving":
        
        accion_aleatoria=random.choice(("acelerar","frenar"))
        velocidad_aleatoria=random.randint(3, 15)
        
        if accion_aleatoria=="frenar":
            frenar(vehiculo,velocidad_aleatoria)
            print(f"Despues de frenar {velocidad_aleatoria}km/h su velocidad es:{vehiculo['speed_kmh']} km/h")
        else:
            acelerar(vehiculo,velocidad_aleatoria)
            print(f"Despues de acelerar {velocidad_aleatoria}km/h su velocidad es:{vehiculo['speed_kmh']} km/h")
    
    else:#Caso en el que esta parado
        accion_aleatoria=random.choice(("moverse","quieto"))
        
        
        if accion_aleatoria == "moverse":
            
            velocidad_aleatoria=random.randint(8, 25)
            acelerar(vehiculo, velocidad_aleatoria)
            
            print(f"El coche arranca a una velocidad de {velocidad_aleatoria} km/h")
            
        else:
            print("El coche sigue parado")


vehiculo ={
"vehicle_id": "veh-001",
"ts": "2026-02-04T12:00:00Z",
"speed_kmh": 0,
"temperature_c": 20,
"battery_pct": 40,
"gps": {"lat": 40.4168, "lon": -3.7038},
"status": "moving"#moving o stopping
}


print("=== SIMULADOR INICIADO ===")
print("Enviando datos cada 0.5 segundos al backend...")
print("Ctrl+C para detener\n")

try:
    while True:
        print("\n" + "="*50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Estado actual:")

        comportamiento(vehiculo)
        descarga_bateria(vehiculo)
        temperatura(vehiculo)
        actualizar_timestamp(vehiculo)

        # Mostrar estado actual
        print(f"  Velocidad:     {vehiculo['speed_kmh']:.1f} km/h")
        print(f"  Batería:       {vehiculo['battery_pct']:.1f} %")
        print(f"  Temperatura:   {vehiculo['temperature_c']:.1f} °C")
        print(f"  GPS:           lat {vehiculo['gps']['lat']:.6f}, lon {vehiculo['gps']['lon']:.6f}")
        print(f"  Estado:        {vehiculo['status']}")
        print(f"  Timestamp:     {vehiculo['ts']}")

        if vehiculo["battery_pct"] <= 0:
            print("\n" + "!"*60)
            print("¡EL COCHE SE HA QUEDADO SIN BATERÍA!")
            print("Simulación detenida.")
            print("!"*60)
            # Enviamos el último estado (batería 0)
            enviar_al_backend(vehiculo)
            break  # Detiene el bucle while
        
        # Enviar al backend
        enviar_al_backend(vehiculo)

        # Esperar 0.5 segundos antes del siguiente ciclo
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\nSimulador detenido por el usuario.")