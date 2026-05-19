# Manual de Uso — SDN Firewall

## Requisitos previos

- Python 3.11+
- Windows/Linux/Mac con soporte de sockets
- 3 equipos en la misma LAN (recomendado) o localhost para pruebas
- pip/venv para gestionar dependencias

---

## Fase 1: Setup Inicial

### Paso 1: Clonar/descargar el proyecto

```bash
cd C:\Users\manue\Desktop\final_redes
```

### Paso 2: Crear virtual environment e instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Paso 3: Identificar la IP del servidor

En la PC del escritorio (que será servidor):

```bash
# Windows
ipconfig

# Linux/Mac
ip a
```

**Busca la IP local (192.168.X.X o 10.X.X.X) — NO uses 127.0.0.1 en LAN real.**

Ejemplo: `192.168.1.50`

---

## Fase 2: Configuración por equipos

### Servidor (PC Escritorio)

**No requiere configuración especial.** El servidor escucha en puerto 8000 en todos los interfaces.

### Cliente 1 (Portátil principal)

Edita `config/nodo1.json`:

```json
{
  "server_ip": "192.168.1.50",
  "node_name": "nodo1-portátil",
  "listen_port": 9001
}
```

### Cliente 2 (Mac o segundo equipo)

Edita `config/nodo2.json`:

```json
{
  "server_ip": "192.168.1.50",
  "node_name": "nodo2-mac",
  "listen_port": 9002
}
```

---

## Fase 3: Ejecución

### Terminal 1: Servidor (PC Escritorio)

```bash
cd sdn-firewall
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

**Esperado:**
```
Uvicorn running on http://0.0.0.0:8000
Application startup complete
```

**Acceso:**
- API Swagger: http://localhost:8000/docs
- Interfaz web: http://localhost:8000/static/index.html
- Desde otro equipo: http://192.168.1.50:8000/docs

### Terminal 2: Cliente 1 (Portátil)

```bash
cd sdn-firewall
python client/client.py config/nodo1.json
```

**Esperado:**
```
Registrado: {'status': 'registered', 'node': {...}}
Listener iniciado en puerto 9001
UDP listener en puerto 9001
TCP listener en puerto 9101
Reglas actualizadas: 0 reglas
```

### Terminal 3: Cliente 2 (Mac)

```bash
cd sdn-firewall
python client/client.py config/nodo2.json
```

---

## Fase 4: Uso de la Interfaz Web

1. Abre http://192.168.1.50:8000/static/index.html en el navegador
2. Deberías ver los dos nodos registrados en el panel "Nodos Registrados"

### Crear una Regla desde la Web

**Ejemplo 1: Allow UDP al puerto 9001**

```
IP origen:    (vacío)
IP destino:   (vacío)
Protocolo:    UDP
Puerto destino: 9001
Acción:       allow
Prioridad:    10
Descripción:  Permitir UDP al 9001
```

Click en "+ Crear Regla"

---

## Fase 5: Generar Tráfico de Prueba

### Terminal 4: Generador de Tráfico

**Prueba 1: UDP permitido**

```bash
python traffic_gen/generator.py --dst 192.168.1.100 --port 9001 --proto udp --count 10 --interval 0.5 --message "TEST_ALLOW"
```

**Esperado en el cliente:** Logs mostrando "acción: allow"

---

**Prueba 2: UDP bloqueado**

Primero, crea una regla desde la web:
```
Puerto destino: 9002
Acción:         block
Prioridad:      20
```

Luego:
```bash
python traffic_gen/generator.py --dst 192.168.1.100 --port 9002 --proto udp --count 5 --interval 1.0 --message "TEST_BLOCK"
```

**Esperado:** Logs mostrando "acción: block", sin eventos reportados

---

**Prueba 3: TCP con reporte**

Crea una regla:
```
Protocolo:      TCP
Puerto destino: 80
Acción:         report
Prioridad:      15
```

Luego:
```bash
python traffic_gen/generator.py --dst 192.168.1.100 --port 80 --proto tcp --count 3 --interval 1.0 --message "TEST_REPORT"
```

**Esperado:** Los eventos aparecen en el panel "Eventos Recientes"

---

## Fase 6: Pruebas Automáticas (Bash Scripts)

```bash
# Test 1: Verificar allow
bash tests/test_allow.sh

# Test 2: Verificar block
bash tests/test_block.sh

# Test 3: Verificar prioridad
bash tests/test_priority.sh
```

---

## Guía de Troubleshooting

### Problema: "Connection refused" al conectar cliente

**Causa:** IP servidor incorrecta  
**Solución:**
1. Verifica con `ipconfig` la IP real del servidor
2. Edita `config/nodo1.json` con la IP correcta
3. Reinicia el cliente

### Problema: Paquetes no llegan al cliente

**Causa:** Firewall del SO bloqueando  
**Solución (Windows):**
```bash
netsh advfirewall set allprofiles state off
# ... después de las pruebas, reactiva:
netsh advfirewall set allprofiles state on
```

### Problema: "ModuleNotFoundError" al ejecutar

**Causa:** Dependencias no instaladas  
**Solución:**
```bash
pip install -r requirements.txt
```

### Problema: Puerto 8000 ya en uso

**Causa:** Otro proceso ocupando el puerto  
**Solución:**
```bash
# Cambiar puerto (edita server/main.py línea 11)
uvicorn server.main:app --host 0.0.0.0 --port 9999
```

### Problema: Cliente no aparece en `/nodes`

**Causa:** Cliente no se registró correctamente  
**Solución:**
1. Verifica logs del cliente (debe mostrar "Registrado")
2. Revisa la IP servidor en config.json
3. Usa `curl http://192.168.1.50:8000/nodes` para listar nodos

---

## Endpoints REST (Referencia Rápida)

### Nodos
```bash
POST /register          # Registra un cliente
GET  /nodes             # Lista nodos activos
```

### Reglas
```bash
GET  /rules             # Lista todas las reglas
POST /rules             # Crea una regla
DELETE /rules/{id}      # Elimina una regla
```

### Eventos
```bash
GET  /events            # Lista eventos (últimos 100)
POST /events            # Cliente reporta un evento
```

---

## Ejemplo Completo: Demo en LAN Real

### Setup
- **Servidor:** PC escritorio (IP: 192.168.1.50)
- **Cliente 1:** Portátil (IP: 192.168.1.100)
- **Cliente 2:** Mac (IP: 192.168.1.101)

### Ejecución (simultáneamente)

```bash
# En PC escritorio:
uvicorn server.main:app --host 0.0.0.0 --port 8000

# En Portátil (Terminal A):
python client/client.py config/nodo1.json

# En Mac (Terminal B):
python client/client.py config/nodo2.json

# Desde cualquier equipo (navegador):
http://192.168.1.50:8000/static/index.html
```

### Demostración de reglas

1. **Crear regla ALLOW TCP:80** desde interfaz web
2. **Crear regla BLOCK UDP:9001** desde interfaz web
3. **Desde cualquier equipo, enviar tráfico:**

```bash
# Será permitido (logs en cliente)
python traffic_gen/generator.py --dst 192.168.1.100 --port 80 --proto tcp --count 3

# Será bloqueado (logs en cliente, sin evento)
python traffic_gen/generator.py --dst 192.168.1.100 --port 9001 --proto udp --count 3
```

4. **Verificar en interfaz web:**
   - Panel "Eventos Recientes" muestra actividad TCP
   - Panel "Nodos" muestra ambos clientes con timestamp actualizado

---

## Documentación Adicional

- Ver `README.md` para arquitectura detallada
- Ver `QUICK_START.md` para inicio rápido
- Ver `plan_sdn_firewall.md` para especificación de proyecto
