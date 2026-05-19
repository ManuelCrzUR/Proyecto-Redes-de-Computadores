# Quick Start — SDN Firewall

## 1️⃣ Instalación (una sola vez)

```bash
cd C:\Users\manue\Desktop\final_redes
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2️⃣ Obtener IP del servidor

```bash
ipconfig
```

Busca la línea `IPv4 Address` bajo la sección de tu conexión (WiFi o Ethernet).  
Ejemplo: `192.168.1.50`

## 3️⃣ Configurar clientes

Edita los archivos de configuración con la IP correcta:

```bash
# Editar config/nodo1.json
{
  "server_ip": "192.168.1.50",  <- REEMPLAZAR CON TU IP
  "node_name": "nodo1",
  "listen_port": 9001
}
```

Repite para `nodo2.json` y `nodo3.json`.

## 4️⃣ Levantar servidor

**En la PC del escritorio:**

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Abre en el navegador:
- API: http://localhost:8000/docs
- Interfaz web: http://localhost:8000/static/index.html

## 5️⃣ Levantar cliente

**En portátil o Mac (en otra terminal):**

```bash
python client/client.py config/nodo1.json
```

Deberías ver en el servidor que el nodo aparece en `/nodes`.

## 6️⃣ Probar tráfico

**En otra terminal:**

```bash
# Enviar 5 paquetes UDP al puerto 9001 del cliente
python traffic_gen/generator.py --dst 192.168.1.100 --port 9001 --proto udp --count 5 --interval 0.5

# Enviar 3 paquetes TCP al puerto 9101
python traffic_gen/generator.py --dst 192.168.1.100 --port 9101 --proto tcp --count 3 --interval 1.0
```

## 7️⃣ Crear una regla desde la interfaz web

1. Abre http://IP_SERVIDOR:8000/static/index.html
2. Completa el formulario:
   - **Puerto destino:** 9001
   - **Protocolo:** UDP
   - **Acción:** block
   - **Prioridad:** 15
   - **Descripción:** Bloquear UDP al 9001
3. Click en "+ Crear Regla"
4. Envía nuevamente tráfico → el cliente debe bloquearlo

---

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Cliente no se conecta | Verifica IP en config.json |
| Firewall bloquea | `netsh advfirewall set allprofiles state off` |
| Puerto en uso | Cambia `--port` o mata el proceso anterior |
| ModuleNotFoundError | `pip install -r requirements.txt` |

---

## Estructura de carpetas

```
final_redes/
├── server/          ← FastAPI backend
├── client/          ← Cliente SDN replicable
├── traffic_gen/     ← Generador de paquetes
├── interface/       ← Web UI (HTML/CSS/JS)
├── config/          ← Configs por nodo
├── tests/           ← Scripts de prueba
├── requirements.txt
├── README.md
└── QUICK_START.md   ← TÚ ESTÁS AQUÍ
```

---

## Comandos útiles

```bash
# Ver API swagger
curl http://localhost:8000/docs

# Listar nodos
curl http://localhost:8000/nodes | python -m json.tool

# Crear regla por CLI
curl -X POST http://localhost:8000/rules \
  -H "Content-Type: application/json" \
  -d '{"action":"allow","priority":10,"protocol":"UDP","dst_port":9001,"description":"Test"}'

# Listar eventos
curl http://localhost:8000/events | python -m json.tool
```

---

**¡Listo! Ahora tienes un sistema SDN firewall funcional.**
