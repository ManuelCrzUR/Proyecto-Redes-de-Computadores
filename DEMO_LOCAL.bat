@echo off
REM Script de demostración local del SDN Firewall
REM Ejecuta servidor, cliente y generador de tráfico en localhost

setlocal enabledelayedexpansion

echo ===================================
echo SDN Firewall - Demo Local
echo ===================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.11+
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
pip list | findstr fastapi >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo.
echo PASO 1: Crear config local para cliente de prueba
echo {                                          > client\local_config.json
echo   "server_ip": "127.0.0.1",               >> client\local_config.json
echo   "node_name": "nodo-local",              >> client\local_config.json
echo   "listen_port": 9001                     >> client\local_config.json
echo }                                          >> client\local_config.json
echo OK: Config creado

echo.
echo PASO 2: Iniciando servidor en puerto 8000...
start "SDN Server" cmd /k "cd %cd% && python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak

echo PASO 3: Iniciando cliente...
start "SDN Client" cmd /k "cd %cd% && python client/client.py client/local_config.json"
timeout /t 2 /nobreak

echo.
echo PASO 4: Abriendo interfaz web en navegador...
start http://127.0.0.1:8000/static/index.html

echo.
echo PASO 5: Listo para generador de tráfico...
echo.
echo OPCIONES DE PRUEBA (ejecuta en otra terminal):
echo.
echo   UDP - Permitir (default):
echo   python traffic_gen/generator.py --dst 127.0.0.1 --port 9001 --proto udp --count 10
echo.
echo   TCP - Permitir:
echo   python traffic_gen/generator.py --dst 127.0.0.1 --port 9101 --proto tcp --count 5
echo.
echo   NOTA: Antes de ejecutar, crea reglas desde la interfaz web:
echo   - Allow UDP:9001 (prioridad 10)
echo   - Block TCP:9101 (prioridad 20)
echo.
echo ===================================
echo Las ventanas del servidor y cliente están abiertas
echo Presiona Ctrl+C para detener cualquiera
echo ===================================
pause
