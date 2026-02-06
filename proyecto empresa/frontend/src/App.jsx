import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [vehicles, setVehicles] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const wsRef = useRef(null);

  const connectWebSocket = () => {
    console.log('Intentando conectar...');
    // WebSocket
    
    const ws = new WebSocket('ws://' + window.location.hostname + ':8000/ws');

    ws.onopen = () => {
      console.log('Conectado!');
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Datos recibidos:', data);

        setVehicles((prev) => ({
          ...prev,
          [data.vehicle_id]: data,
        }));
      } catch (err) {
        console.error('Error parseando:', err);
      }
    };

    ws.onclose = () => {
      console.log('Desconectado');
      setConnectionStatus('disconnected');
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (err) => {
      console.error('Error WS:', err);
      ws.close();
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const hasVehicles = Object.keys(vehicles).length > 0;

  return (
    <div className="App">
      <h1>Telemetry Dashboard</h1>

      <div className={`status-box ${connectionStatus}`}>
        Estado de conexión: 
        {connectionStatus === 'connected' ? 'Conectado ✅' :
         connectionStatus === 'disconnected' ? 'Desconectado ❌' :
         'Reconectando... 🔄'}
      </div>

      {!hasVehicles ? (
        <div className="waiting">Esperando telemetría...</div>
      ) : (
        <div className="vehicles-grid">
          {Object.entries(vehicles).map(([id, data]) => (
            <div key={id} className="vehicle-card">
              <h2>{id}</h2>

              <div className="info">
                <p><strong>Velocidad:</strong> {data.speed_kmh?.toFixed(1) ?? '—'} km/h</p>
                <p><strong>Temperatura:</strong> {data.temperature_c?.toFixed(1) ?? '—'} °C</p>
                <p><strong>Batería:</strong> {data.battery_pct?.toFixed(1) ?? '—'} %</p>
                <p><strong>Estado:</strong> {data.status === 'moving' ? 'En movimiento' : 'Parado'}</p>
                <p>
                  <strong>Posición GPS:</strong><br />
                  Lat: {data.gps?.lat?.toFixed(6) ?? '—'}<br />
                  Lon: {data.gps?.lon?.toFixed(6) ?? '—'}
                </p>
                <p>
                  <strong>Última actualización:</strong><br />
                  {data.ts
                    ? new Date(data.ts).toLocaleString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })
                    : '—'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;