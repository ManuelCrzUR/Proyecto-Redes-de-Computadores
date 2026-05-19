#!/bin/bash
# Script de demostración local del SDN Firewall
# Ejecuta servidor, cliente y generador de tráfico en localhost

set -e

echo "==================================="
echo "SDN Firewall - Demo Local"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no encontrado. Instala Python 3.11+"
    exit 1
fi

# Verificar dependencias
echo "Verificando dependencias..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Instalando dependencias..."
    pip install -r requirements.txt
fi

echo ""
echo "PASO 1: Crear config local para cliente de prueba"
mkdir -p client
cat > client/local_config.json << EOF
{
  "server_ip": "127.0.0.1",
  "node_name": "nodo-local",
  "listen_port": 9001
}
EOF
echo "OK: Config creado"

echo ""
echo "PASO 2: Iniciando servidor en puerto 8000..."
python3 -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload &
SERVER_PID=$!
sleep 2

echo "PASO 3: Iniciando cliente..."
python3 client/client.py client/local_config.json &
CLIENT_PID=$!
sleep 2

echo ""
echo "PASO 4: Abriendo interfaz web..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:8000/static/index.html
elif command -v open &> /dev/null; then
    open http://127.0.0.1:8000/static/index.html
fi

echo ""
echo "PASO 5: Listo para generador de tráfico..."
echo ""
echo "OPCIONES DE PRUEBA (ejecuta en otra terminal):"
echo ""
echo "  UDP - Permitir (default):"
echo "  python3 traffic_gen/generator.py --dst 127.0.0.1 --port 9001 --proto udp --count 10"
echo ""
echo "  TCP - Permitir:"
echo "  python3 traffic_gen/generator.py --dst 127.0.0.1 --port 9101 --proto tcp --count 5"
echo ""
echo "  NOTA: Antes de ejecutar, crea reglas desde la interfaz web"
echo ""
echo "==================================="
echo "Procesos en ejecución:"
echo "  Servidor: PID $SERVER_PID"
echo "  Cliente:  PID $CLIENT_PID"
echo ""
echo "Para detener: kill $SERVER_PID $CLIENT_PID"
echo "O presiona Ctrl+C en esta terminal"
echo "==================================="

# Esperar a que se cierren los procesos
wait $SERVER_PID $CLIENT_PID
