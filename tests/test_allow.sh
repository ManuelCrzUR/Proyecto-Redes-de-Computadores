#!/bin/bash
# Prueba de regla ALLOW
# Verifica que un paquete permitido es aceptado

echo "=== Test 1: Regla ALLOW UDP puerto 9001 ==="
echo ""

SERVER="http://localhost:8000"
CLIENT_IP="127.0.0.1"
CLIENT_PORT=9001

echo "[1] Creando regla: Allow UDP puerto 9001"
curl -s -X POST "$SERVER/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": null,
    "dst_ip": null,
    "protocol": "UDP",
    "src_port": null,
    "dst_port": 9001,
    "action": "allow",
    "priority": 10,
    "description": "Allow UDP al puerto 9001"
  }' | jq .

echo ""
echo "[2] Enviando 5 paquetes UDP al puerto 9001"
python ../traffic_gen/generator.py --dst $CLIENT_IP --port $CLIENT_PORT --proto udp --count 5 --interval 0.5 --message "TEST_ALLOW"

echo ""
echo "[3] Listando reglas activas"
curl -s -X GET "$SERVER/rules" | jq '.[] | {action, protocol, dst_port}'

echo ""
echo "✅ Test completado"
