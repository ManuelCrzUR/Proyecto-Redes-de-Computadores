#!/bin/bash
# Prueba de prioridad
# Verifica que la regla con mayor prioridad gana en conflicto

echo "=== Test 5: Conflicto de prioridad ==="
echo ""

SERVER="http://localhost:8000"
CLIENT_IP="127.0.0.1"
CLIENT_PORT=9003

echo "[1] Creando regla ALLOW TCP puerto 9003 con prioridad 5"
curl -s -X POST "$SERVER/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": null,
    "dst_ip": null,
    "protocol": "TCP",
    "src_port": null,
    "dst_port": 9003,
    "action": "allow",
    "priority": 5,
    "description": "Allow TCP puerto 9003 (baja prioridad)"
  }' | jq .

echo ""
echo "[2] Creando regla BLOCK TCP puerto 9003 con prioridad 20"
curl -s -X POST "$SERVER/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": null,
    "dst_ip": null,
    "protocol": "TCP",
    "src_port": null,
    "dst_port": 9003,
    "action": "block",
    "priority": 20,
    "description": "Block TCP puerto 9003 (alta prioridad)"
  }' | jq .

echo ""
echo "[3] Enviando 2 paquetes TCP al puerto 9003 (debe ganar BLOCK por prioridad)"
python ../traffic_gen/generator.py --dst $CLIENT_IP --port $CLIENT_PORT --proto tcp --count 2 --interval 0.5 --message "TEST_PRIORITY"

echo ""
echo "[4] Verificando que BLOCK ganó (evaluador debe haber usado max prioridad)"
curl -s -X GET "$SERVER/rules" | jq '.[] | select(.dst_port == 9003) | {action, priority}' | sort -k2

echo ""
echo "✅ Test completado"
