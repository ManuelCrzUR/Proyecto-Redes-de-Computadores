#!/bin/bash
# Prueba de regla BLOCK
# Verifica que un paquete bloqueado es descartado sin respuesta

echo "=== Test 2: Regla BLOCK UDP puerto 9002 ==="
echo ""

SERVER="http://localhost:8000"
CLIENT_IP="127.0.0.1"
CLIENT_PORT=9002

echo "[1] Creando regla: Block UDP puerto 9002"
curl -s -X POST "$SERVER/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": null,
    "dst_ip": null,
    "protocol": "UDP",
    "src_port": null,
    "dst_port": 9002,
    "action": "block",
    "priority": 15,
    "description": "Block UDP al puerto 9002"
  }' | jq .

echo ""
echo "[2] Enviando 3 paquetes UDP al puerto 9002 (deberían ser bloqueados)"
python ../traffic_gen/generator.py --dst $CLIENT_IP --port $CLIENT_PORT --proto udp --count 3 --interval 0.5 --message "TEST_BLOCK"

echo ""
echo "[3] Verificando que NO hay eventos reportados (paquetes bloqueados)"
curl -s -X GET "$SERVER/events" | jq '.[] | select(.port == 9002) | .'

echo ""
echo "✅ Test completado"
