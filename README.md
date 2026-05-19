# SDN Firewall — Proyecto Final Redes de Computadores

Sistema de firewall distribuido sobre una red SDN simulada con arquitectura cliente-servidor.

## Características

- **Servidor centralizado** con FastAPI para gestionar reglas y eventos
- **Clientes replicables** que descargan reglas y evalúan tráfico entrante
- **Interfaz web** para crear/editar reglas y monitorear nodos
- **Motor de evaluación** con soporte de prioridades y wildcards
- **Generador de tráfico** para pruebas UDP y TCP

---

## Stack Tecnológico

- **Backend:** Python 3.11+ · FastAPI · Uvicorn
- **Frontend:** HTML5 · CSS3 · Vanilla JavaScript
- **Networking:** sockets UDP/TCP nativos
- **Gestión:** Pydantic · requests

---

## Instalación

### 1. Clonar repositorio e instalar dependencias

```bash
cd sdn-firewall
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Obtener IP local del servidor

```bash
# Windows
ipconfig

# Linux/Mac
ip a
```

Busca la IP en la LAN (ej: `192.168.1.50` o `192.168.0.100`).

---

## Ejecución

### Servidor (PC escritorio)

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Accede a:
- API Swagger: `http://SERVIDOR_IP:8000/docs`
- Interfaz web: `http://SERVIDOR_IP:8000/static/index.html`

### Cliente (Portátil o Mac)

1. Edita `config/nodo1.json` (o `nodo2.json`):
```json
{
  "server_ip": "192.168.1.50",
  "node_name": "nodo1",
  "listen_port": 9001
}
```

2. Ejecuta el cliente:
```bash
python client/client.py config/nodo1.json
```

### Generador de Tráfico

```bash
# UDP: 10 paquetes a puerto 9001 con intervalo de 0.5s
python traffic_gen/generator.py --dst 192.168.1.100 --port 9001 --proto udp --count 10 --interval 0.5

# TCP: 5 paquetes a puerto 80
python traffic_gen/generator.py --dst 192.168.1.100 --port 80 --proto tcp --count 5 --interval 1.0
```

---

## Estructura de una Regla

```json
{
  "id": "abc123",
  "src_ip": "192.168.1.50",
  "dst_ip": null,
  "protocol": "UDP",
  "src_port": null,
  "dst_port": 9001,
  "action": "block",
  "priority": 10,
  "description": "Bloquear UDP a puerto 9001"
}
```

| Campo | Valores | Obligatorio |
|-------|---------|-------------|
| `src_ip` / `dst_ip` | IPv4 o `null` | No |
| `protocol` | `"TCP"`, `"UDP"`, `null` | No |
| `src_port` / `dst_port` | 0–65535 o `null` | No |
| `action` | `"allow"`, `"block"`, `"report"` | **Sí** |
| `priority` | entero (mayor = más prioritario) | **Sí** |

### Lógica de Evaluación

```python
def evaluate(packet, rules):
    matches = [r for r in rules if rule_matches(packet, r)]
    if not matches:
        return "allow"  # política por defecto
    return max(matches, key=lambda r: r["priority"])["action"]
```

**Wildcards:** Un campo `null` o no especificado en la regla actúa como "cualquiera" en la coincidencia.

---

## Endpoints REST del Servidor

### Nodos

```http
POST   /register                # Registra un cliente
GET    /nodes                   # Lista nodos activos
```

### Reglas

```http
GET    /rules                   # Lista todas las reglas
POST   /rules                   # Crea una nueva regla
DELETE /rules/{id}              # Elimina una regla
```

### Eventos

```http
POST   /events                  # Recibe reporte de un cliente
GET    /events?limit=100        # Lista eventos recientes
```

---

## Flujo de Mensajes

1. **Cliente arranca** → `POST /register` con nombre, IP, puerto de escucha
2. **Cliente cada 10s** → `GET /rules` y actualiza tabla local
3. **Generador envía tráfico** → paquetes UDP/TCP al cliente
4. **Cliente recibe paquete** → evalúa contra reglas locales
5. **Si action == "report"** → `POST /events` al servidor
6. **Interfaz web** → polling cada 5s a `/rules`, `/nodes`, `/events`

---

## Casos de Prueba

### Test 1: Allow
```bash
bash tests/test_allow.sh
```

Crea una regla `allow` para UDP:9001 y envía 5 paquetes. El cliente debe loguear "allow" sin reportar.

### Test 2: Block
```bash
bash tests/test_block.sh
```

Crea una regla `block` para UDP:9002. Los paquetes son descartados sin reporte.

### Test 3: Prioridad
```bash
bash tests/test_priority.sh
```

Crea dos reglas conflictivas (allow prioridad 5 vs block prioridad 20). El evaluador elige `block`.

---

## Notas Importantes

### Firewall del SO
En Windows, el Firewall puede bloquear los puertos. Abre excepción o desactívalo temporalmente:
```powershell
netsh advfirewall set allprofiles state off
```

Para reactivar:
```powershell
netsh advfirewall set allprofiles state on
```

### CORS
El servidor tiene CORS habilitado (`allow_origins=["*"]`). Permite que la interfaz web acceda desde cualquier origen.

### Política por Defecto
Si un paquete no coincide con ninguna regla, es **permitido** (`allow`). Esta es una decisión de diseño permisiva.

### IP del Servidor
Reemplaza `REEMPLAZAR_CON_IP_SERVIDOR` en todos los archivos `config/*.json` con la IP local real del PC escritorio.

---

## Estructura de Carpetas

```
sdn-firewall/
├── server/              # Backend FastAPI
│   ├── main.py
│   ├── models.py
│   ├── rules_engine.py
│   └── store.py
├── client/              # Clientes SDN
│   ├── client.py
│   ├── listener.py
│   ├── evaluator.py
│   └── config.json
├── traffic_gen/         # Generador de tráfico
│   └── generator.py
├── interface/           # Frontend web
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config/              # Configuraciones por nodo
│   ├── nodo1.json
│   ├── nodo2.json
│   └── nodo3.json
├── tests/               # Scripts de prueba
│   ├── test_allow.sh
│   ├── test_block.sh
│   └── test_priority.sh
├── requirements.txt
└── README.md
```

---

## Troubleshooting

### El cliente no se conecta al servidor
- Verifica la IP en `config.json` con `ipconfig` (Windows) o `ip a` (Linux)
- Asegúrate de que el servidor esté corriendo: `curl http://SERVER_IP:8000/docs`

### El generador de tráfico no envía paquetes
- Verifica que el cliente esté escuchando: revisa los logs del cliente
- En Windows, desactiva el Firewall temporalmente

### La interfaz web no carga
- Asegúrate de que `SERVER` en `app.js` apunta a la IP correcta
- Abre la consola del navegador (F12) para ver errores de red

---

## Autor

Redes de Computadores · Proyecto Final  
Universidad del Rosario
