#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import os
from pathlib import Path

def get_local_ip():
    """Detecta IP local del equipo."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_ping(ip):
    """Verifica conectividad a una IP."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(["ping", "-n", "1", ip], capture_output=True, timeout=2)
        else:
            result = subprocess.run(["ping", "-c", "1", ip], capture_output=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def check_dependencies():
    """Verifica que FastAPI y uvicorn estén instalados."""
    try:
        import fastapi
        import uvicorn
        import requests
        return True
    except ImportError:
        return False

def setup_server():
    """Configura el servidor."""
    print("\n" + "="*60)
    print("CONFIGURACION: SERVIDOR")
    print("="*60)

    local_ip = get_local_ip()
    print(f"\nIP detectada: {local_ip}")

    print("\n[OK] Servidor escuchara en: 0.0.0.0:8000")
    print("[OK] Los clientes se conectaran a: " + local_ip + ":8000")

    print("\n" + "="*60)
    print("PROXIMOS PASOS:")
    print("="*60)
    print(f"\n1. En ESTE equipo (servidor), ejecuta:")
    print(f"   python -m uvicorn server.main:app --host 0.0.0.0 --port 8000")
    print(f"\n2. En los CLIENTES, usa esta IP del servidor:")
    print(f"   {local_ip}")
    print(f"\n3. El dashboard estara en:")
    print(f"   http://{local_ip}:8000/static/index.html")

    return {"type": "server", "ip": local_ip}

def setup_client():
    """Configura un cliente."""
    print("\n" + "="*60)
    print("CONFIGURACION: CLIENTE")
    print("="*60)

    local_ip = get_local_ip()
    print(f"\nIP local de este equipo: {local_ip}")

    # Entrada: IP del servidor
    while True:
        server_ip = input("\nIP del servidor (ej: 192.168.0.6): ").strip()
        if not server_ip:
            server_ip = "192.168.0.6"

        print(f"\nVerificando conectividad a {server_ip}...")
        if check_ping(server_ip):
            print("Conectividad confirmada.")
            break
        else:
            print("No hay respuesta de esa IP. Verifica que sea correcta.")
            retry = input("Reintentar (s/n): ").strip().lower()
            if retry != 's':
                print("Continuando con la IP ingresada...")
                break

    # Entrada: Nombre del nodo
    node_name = input("\nNombre del nodo (ej: nodo-laptop): ").strip()
    if not node_name:
        node_name = "nodo-cliente"

    # Entrada: Puerto de escucha
    listen_port = input("\nPuerto de escucha (ej: 9001): ").strip()
    if not listen_port:
        listen_port = 9001
    else:
        try:
            listen_port = int(listen_port)
        except:
            listen_port = 9001

    # Crear configuración
    config = {
        "server_ip": server_ip,
        "node_name": node_name,
        "listen_port": listen_port
    }

    # Guardar archivo
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "client_config.json"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print("\n" + "="*60)
    print("CONFIGURACION GUARDADA")
    print("="*60)
    print(f"\nArchivo: {config_file}")
    print(json.dumps(config, indent=2))

    print("\n" + "="*60)
    print("PROXIMOS PASOS:")
    print("="*60)
    print(f"\n1. Ejecuta el cliente:")
    print(f"   python client/client.py config/client_config.json")
    print(f"\n2. Accede al dashboard desde cualquier equipo:")
    print(f"   http://{server_ip}:8000/static/index.html")
    print(f"\n3. Veras '{node_name}' en el panel de Nodos")

    return config

def main():
    print("\n" + "="*60)
    print("SDN FIREWALL - SETUP WIZARD")
    print("="*60)

    # Verificar dependencias
    print("\nVerificando dependencias...")
    if not check_dependencies():
        print("Faltan dependencias. Ejecuta:")
        print("   pip install -r requirements.txt")
        return
    print("Todas las dependencias estan disponibles.")

    # Pregunta: ¿Servidor o Cliente?
    print("\n" + "="*60)
    print("CUAL ES TU ROL EN LA RED?")
    print("="*60)
    print("\n1. SERVIDOR (controla reglas y nodos)")
    print("   - Ejecuta en el equipo principal")
    print("   - Los clientes se conectan a este")
    print("\n2. CLIENTE (escucha trafico y reporta)")
    print("   - Ejecuta en multiples equipos")
    print("   - Se conecta al servidor para descargar reglas")

    choice = input("\nElige tu rol [1/2]: ").strip()

    if choice == "1":
        setup_server()
    elif choice == "2":
        setup_client()
    else:
        print("Opcion no valida. Intenta de nuevo.")
        return

    print("\n" + "="*60)
    print("SETUP COMPLETADO")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
