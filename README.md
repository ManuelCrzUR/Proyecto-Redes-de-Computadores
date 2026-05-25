# SDN Firewall — Distributed Network Firewall System

Manuel Cruz, Isabella Posada, Santiago Peña

A distributed firewall system built on Software-Defined Networking (SDN) architecture with a centralized controller and multiple client nodes that evaluate traffic locally.

---

## Features

- **Centralized Server** — FastAPI-based controller to manage firewall rules and events
- **Replicable Clients** — Download rules and evaluate traffic independently
- **Web Dashboard** — Create, edit, and delete rules in real-time
- **Priority-Based Evaluation** — Conflict resolution via priority values
- **Wildcard Support** — Match any value with null fields in rules
- **Traffic Generator** — CLI tool for testing UDP and TCP packets
- **Multi-Platform** — Works on Windows, Linux, and Mac

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ · FastAPI · Uvicorn · Pydantic |
| Frontend | HTML5 · CSS3 · Vanilla JavaScript |
| Networking | Native UDP/TCP sockets |
| API | REST/JSON |
| Storage | In-memory (dictionaries/lists) |

---

## Prerequisites

- **Python 3.11 or higher**
- **pip** package manager
- **2+ computers on the same network** (or localhost for single-machine testing)
- Network connectivity between machines

---

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the project
cd final_redes

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python setup.py
```

The wizard will guide you through:
- Role selection (Server or Client)
- IP configuration
- Network connectivity verification
- Automatic configuration file generation

### Option 2: Manual Installation

```bash
# Clone or download the project
cd final_redes

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Then proceed to manual configuration below.

---

## Configuration

### Step 1: Identify Server IP

Get your server machine's local IP address:

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" (typically 192.168.X.X or 10.X.X.X)

**Linux:**
```bash
hostname -I
```
or
```bash
ip addr | grep "inet " | grep -v "127.0.0.1"
```

**Mac:**
```bash
ifconfig | grep "inet " | grep -v "127.0.0.1"
```

Example: `192.168.0.6`

### Step 2: Server Configuration

No special configuration needed. The server listens on all interfaces (0.0.0.0) on port 8000.

### Step 3: Client Configuration

For each client machine, edit the configuration file in `config/` directory:

**Example for Client 1 (Laptop):**
```json
{
  "server_ip": "192.168.0.6",
  "node_name": "nodo-laptop",
  "listen_port": 9001
}
```

**Example for Client 2 (Mac):**
```json
{
  "server_ip": "192.168.0.6",
  "node_name": "nodo-mac",
  "listen_port": 9002
}
```

Replace `192.168.0.6` with your actual server IP address.

---

## Running the System

### Terminal 1: Start Server

```bash
# On server machine
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Access the web dashboard at:
```
http://SERVER_IP:8000/static/index.html
```

API documentation available at:
```
http://SERVER_IP:8000/docs
```

### Terminal 2: Start Client 1

```bash
# On client machine 1
python client/client.py config/nodo1.json
```

Expected output:
```
INFO:Client:Cliente nodo-laptop esta iniciandose
INFO:Client:Nodo registrado: {...}
INFO:Listener:Escuchador iniciado en puerto 9001
INFO:Listener:Escuchador UDP en puerto 9001
INFO:Listener:Escuchador TCP en puerto 9101
INFO:Client:Se descargaron 0 reglas del servidor
```

### Terminal 3: Start Client 2 (Optional)

```bash
# On client machine 2
python client/client.py config/nodo2.json
```

### Terminal 4: Generate Test Traffic

```bash
# From any machine
python traffic_gen/generator.py --dst 192.168.0.X --port 9001 --proto udp --count 5
```

Replace `192.168.0.X` with the client's IP address.

---

## Web Dashboard Guide

### Accessing the Dashboard

Open your browser and navigate to:
```
http://SERVER_IP:8000/static/index.html
```

### Creating a Firewall Rule

1. Go to the **Rules** panel
2. Fill in the form:
   - **Source IP**: Leave empty for any
   - **Destination IP**: Leave empty for any
   - **Protocol**: UDP or TCP
   - **Destination Port**: Port number (e.g., 9001)
   - **Action**: allow, block, or report
   - **Priority**: Higher number = higher priority
   - **Description**: Rule description

3. Click **Add Rule**

### Monitoring Nodes

The **Nodes** panel shows:
- Connected client nodes
- Client IP address
- Listening port
- Last seen timestamp

### Viewing Events

The **Events** panel displays:
- Traffic events (when action="report")
- Source and destination information
- Protocol and port details
- Action taken
- Timestamp

---

## Firewall Rules

### Rule Structure

```json
{
  "id": "abc123",
  "src_ip": "192.168.0.50",
  "dst_ip": null,
  "protocol": "UDP",
  "src_port": null,
  "dst_port": 9001,
  "action": "block",
  "priority": 10,
  "description": "Block UDP to port 9001"
}
```

### Rule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `src_ip` | IPv4 string or null | No | Source IP (null = any) |
| `dst_ip` | IPv4 string or null | No | Destination IP (null = any) |
| `protocol` | "UDP", "TCP", or null | No | Protocol (null = any) |
| `src_port` | 0-65535 or null | No | Source port (null = any) |
| `dst_port` | 0-65535 or null | No | Destination port (null = any) |
| `action` | "allow", "block", "report" | Yes | Action to take |
| `priority` | Integer | Yes | Higher number = higher priority |
| `description` | String | No | Rule description |

### Wildcard Matching

Any field set to `null` acts as a wildcard (matches any value):

```json
{
  "protocol": "UDP",
  "dst_port": 9001,
  "src_ip": null,
  "action": "report",
  "priority": 10
}
```

This rule matches any UDP packet to port 9001, regardless of source IP.

### Default Policy

If a packet does not match any rule, it is **allowed** by default.

### Priority Resolution

When multiple rules match a packet, the rule with the **highest priority value wins**:

```
Rule 1: allow UDP:9001, priority 5
Rule 2: block UDP:9001, priority 20
        → Rule 2 (block) is applied (higher priority)
```

---

## API Endpoints

### Node Registration

```http
POST /register
Content-Type: application/json

{
  "name": "nodo-laptop",
  "ip": "192.168.0.100",
  "listen_port": 9001
}

Response:
{
  "status": "registered",
  "node": {
    "name": "nodo-laptop",
    "ip": "192.168.0.100",
    "listen_port": 9001,
    "last_seen": "2026-05-19T10:30:00"
  }
}
```

### List Nodes

```http
GET /nodes

Response:
[
  {
    "name": "nodo-laptop",
    "ip": "192.168.0.100",
    "listen_port": 9001,
    "last_seen": "2026-05-19T10:30:00"
  }
]
```

### Create Rule

```http
POST /rules
Content-Type: application/json

{
  "protocol": "UDP",
  "dst_port": 9001,
  "action": "block",
  "priority": 10,
  "description": "Block UDP 9001"
}

Response:
{
  "status": "created",
  "rule": {...}
}
```

### List Rules

```http
GET /rules

Response:
[
  {
    "id": "abc123",
    "protocol": "UDP",
    "dst_port": 9001,
    "action": "block",
    "priority": 10,
    "description": "Block UDP 9001"
  }
]
```

### Delete Rule

```http
DELETE /rules/abc123

Response:
{
  "status": "deleted",
  "rule_id": "abc123"
}
```

### Report Event

```http
POST /events
Content-Type: application/json

{
  "node_name": "nodo-laptop",
  "src_ip": "192.168.0.100",
  "dst_ip": "192.168.0.6",
  "protocol": "UDP",
  "port": 9001,
  "action": "report"
}
```

### List Events

```http
GET /events?limit=100

Response:
[
  {
    "id": "evt001",
    "node_name": "nodo-laptop",
    "src_ip": "192.168.0.100",
    "dst_ip": "192.168.0.6",
    "protocol": "UDP",
    "port": 9001,
    "action": "report",
    "timestamp": "2026-05-19T10:35:00"
  }
]
```

---

## Message Flow

```
1. Client starts
   └─ POST /register (name, IP, port)

2. Client every 10 seconds
   └─ GET /rules (downloads latest rules)

3. Traffic generator sends packets
   └─ UDP/TCP packets to client port

4. Client receives packet
   └─ Evaluates against local rules

5. If action == "report"
   └─ POST /events (reports to server)

6. Web dashboard every 5 seconds
   └─ GET /rules, /nodes, /events (refreshes display)
```

---

## Traffic Generator

### Basic Usage

```bash
python traffic_gen/generator.py --dst 192.168.0.100 --port 9001 --proto udp --count 10
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--dst` | string | required | Destination IP address |
| `--port` | int | required | Destination port |
| `--proto` | string | udp | Protocol (udp or tcp) |
| `--count` | int | 10 | Number of packets to send |
| `--interval` | float | 1.0 | Delay between packets (seconds) |
| `--message` | string | TEST | Message in packet payload |

### Examples

```bash
# Send 10 UDP packets to port 9001 with 0.5s delay
python traffic_gen/generator.py --dst 192.168.0.100 --port 9001 --proto udp --count 10 --interval 0.5

# Send 5 TCP packets to port 80 with 2s delay
python traffic_gen/generator.py --dst 192.168.0.100 --port 80 --proto tcp --count 5 --interval 2.0

# Send single packet with custom message
python traffic_gen/generator.py --dst 192.168.0.100 --port 9001 --proto udp --count 1 --message "CUSTOM_PAYLOAD"
```

---

## Platform-Specific Notes

### Windows

**Virtual Environment:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Firewall Configuration:**

If clients cannot connect to the server, disable Windows Defender Firewall temporarily:

```powershell
netsh advfirewall set allprofiles state off
```

To re-enable:
```powershell
netsh advfirewall set allprofiles state on
```

Or add exceptions for Python:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Find Python in the list and check both Private and Public

### Linux

**Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Firewall Configuration (UFW):**

```bash
# Check firewall status
sudo ufw status

# If active, allow port 8000
sudo ufw allow 8000

# Allow specific client ports
sudo ufw allow 9001
sudo ufw allow 9002
```

### Mac

**Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Firewall Configuration:**

System Preferences → Security & Privacy → Firewall Options:
- Click the lock to make changes
- Add Python to the firewall whitelist

Or use Terminal:
```bash
# Check if firewall is on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw -getglobalstate

# Disable temporarily
sudo /usr/libexec/ApplicationFirewall/socketfilterfw -setglobalstate off

# Enable
sudo /usr/libexec/ApplicationFirewall/socketfilterfw -setglobalstate on
```

---

## Project Structure

```
final_redes/
├── server/                  # FastAPI backend
│   ├── __init__.py
│   ├── main.py             # API routes and server setup
│   ├── models.py           # Pydantic data models
│   ├── store.py            # In-memory storage (nodes, rules, events)
│   └── rules_engine.py     # Rule evaluation logic
├── client/                 # SDN client nodes
│   ├── __init__.py
│   ├── client.py           # Main client orchestration
│   ├── listener.py         # UDP/TCP packet listener
│   ├── evaluator.py        # Local rule evaluation
│   └── config.json         # Configuration template
├── traffic_gen/            # Traffic generator for testing
│   ├── __init__.py
│   └── generator.py        # CLI packet sender
├── interface/              # Web dashboard
│   ├── index.html          # Dashboard layout
│   ├── app.js              # JavaScript frontend logic
│   └── style.css           # Dashboard styling
├── config/                 # Node-specific configurations
│   ├── nodo1.json          # Client 1 config
│   ├── nodo2.json          # Client 2 config
│   └── nodo3.json          # Client 3 config
├── tests/                  # Test scripts
│   ├── test_allow.sh
│   ├── test_block.sh
│   └── test_priority.sh
├── setup.py                # Interactive setup wizard
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## Use Cases

### Allow Traffic

Create a rule with `action: "allow"` and appropriate filters:

```json
{
  "protocol": "TCP",
  "dst_port": 80,
  "action": "allow",
  "priority": 10,
  "description": "Allow HTTP traffic"
}
```

### Block Traffic

Create a rule with `action: "block"`:

```json
{
  "protocol": "UDP",
  "dst_port": 9001,
  "action": "block",
  "priority": 15,
  "description": "Block UDP to port 9001"
}
```

### Monitor Traffic

Create a rule with `action: "report"` to log matching packets:

```json
{
  "src_ip": "192.168.0.100",
  "protocol": "TCP",
  "action": "report",
  "priority": 5,
  "description": "Log all TCP from 192.168.0.100"
}
```

Matching packets will appear in the **Events** panel with timestamps.

### Resolve Conflicts

When multiple rules match, the highest priority wins:

```json
Rule A: protocol=UDP, dst_port=9001, action=allow, priority=5
Rule B: protocol=UDP, dst_port=9001, action=block, priority=20

→ Rule B (block) is applied
```

---

## Architecture

```
┌─────────────────────────────────┐
│   WEB DASHBOARD (HTML/JS)       │
│   (Create rules, view events)   │
└────────────────┬────────────────┘
                 │ HTTP polling (5s)
┌────────────────▼────────────────┐
│  SERVER (FastAPI, port 8000)    │
│  (Rules, nodes, events)         │
└────┬──────────────────────┬─────┘
     │                      │
     │ HTTP polling (10s)   │ HTTP polling (10s)
     │                      │
┌────▼───────┐        ┌────▼──────┐
│  CLIENT 1   │        │  CLIENT 2  │
│  UDP:9001   │        │  UDP:9002  │
│  TCP:9101   │        │  TCP:9102  │
└─────────────┘        └────────────┘
```

---

## Important Notes

### Default Policy

If a packet does not match any rule, it is **allowed**. This is a permissive default.

### CORS Enabled

The server has CORS enabled (`allow_origins=["*"]`) to allow the web dashboard to access the API from any origin.

### Client Autonomy

Clients evaluate rules locally without contacting the server for each packet. Rules are cached and updated every 10 seconds via polling.

### Wildcards

Any field set to `null` in a rule acts as a wildcard:
- `src_ip: null` matches any source
- `protocol: null` matches any protocol
- `dst_port: null` matches any port

### Network Connectivity

For LAN deployments:
1. Ensure all machines are on the same network (WiFi or Ethernet)
2. Verify connectivity: `ping SERVER_IP` from client machines
3. Disable firewalls or add exceptions for ports 8000, 9001-9003, etc.

---

## License

Universidad del Rosario - Computer Networks Course - Final Project

---

## Support

For issues or questions:
1. Check the configuration files match your network setup
2. Verify firewall settings are correct for your OS
3. Ensure all machines are on the same network
4. Check API documentation at `http://SERVER_IP:8000/docs`
