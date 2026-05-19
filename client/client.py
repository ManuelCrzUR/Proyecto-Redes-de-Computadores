import json
import requests
import time
import logging
import threading
from pathlib import Path
import sys

try:
    from .listener import PacketListener
    from .evaluator import evaluate
except ImportError:
    from listener import PacketListener
    from evaluator import evaluate

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger("Client")


class SDNClient:
    def __init__(self, config_path: str = "config.json"):
        """Inicializa cliente SDN con configuración."""
        with open(config_path) as f:
            config = json.load(f)

        self.server_ip = config["server_ip"]
        self.node_name = config["node_name"]
        self.listen_port = config["listen_port"]
        self.server_url = f"http://{self.server_ip}:8000"
        self.rules = []
        self.running = True

    def register(self):
        """Registra el nodo en el servidor."""
        try:
            local_ip = self._get_local_ip()
            payload = {"name": self.node_name, "ip": local_ip, "listen_port": self.listen_port}
            res = requests.post(f"{self.server_url}/register", json=payload, timeout=5)
            logger.info(f"Registrado: {res.json()}")
        except Exception as e:
            logger.error(f"Error registrando: {e}")

    def poll_rules(self):
        """Descarga reglas del servidor cada 10 segundos."""
        while self.running:
            try:
                res = requests.get(f"{self.server_url}/rules", timeout=5)
                self.rules = res.json()
                logger.info(f"Reglas actualizadas: {len(self.rules)} reglas")
            except Exception as e:
                logger.error(f"Error descargando reglas: {e}")
            time.sleep(10)

    def on_packet(self, packet_info: dict):
        """Callback al recibir un paquete."""
        action = evaluate(packet_info, self.rules)
        logger.info(f"Paquete de {packet_info['src_ip']}:{packet_info.get('src_port', '?')} → acción: {action}")

        if action == "report":
            try:
                event = {
                    "node_name": self.node_name,
                    "src_ip": packet_info["src_ip"],
                    "dst_ip": packet_info.get("dst_ip"),
                    "protocol": packet_info["protocol"],
                    "port": packet_info.get("dst_port", 0),
                    "action": action,
                }
                requests.post(f"{self.server_url}/events", json=event, timeout=5)
                logger.info(f"Evento reportado al servidor")
            except Exception as e:
                logger.error(f"Error reportando evento: {e}")

    def _get_local_ip(self) -> str:
        """Obtiene la IP local del cliente."""
        try:
            s = __import__("socket").socket(__import__("socket").AF_INET, __import__("socket").SOCK_DGRAM)
            s.connect((self.server_ip, 8000))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start(self):
        """Inicia el cliente."""
        logger.info(f"Iniciando cliente {self.node_name}")
        self.register()

        listener = PacketListener(self.listen_port, self.on_packet)
        listener.start()

        threading.Thread(target=self.poll_rules, daemon=True).start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Deteniendo cliente...")
            self.running = False
            listener.stop()


if __name__ == "__main__":
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    client = SDNClient(config_path)
    client.start()
