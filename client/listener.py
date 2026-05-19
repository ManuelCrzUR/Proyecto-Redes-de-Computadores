import socket
import threading
import struct
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Listener")


class PacketListener:
    def __init__(self, listen_port: int, on_packet_callback):
        """Inicializa listener UDP y TCP en puerto especificado."""
        self.listen_port = listen_port
        self.on_packet_callback = on_packet_callback
        self.running = False
        self.udp_sock = None
        self.tcp_sock = None

    def start(self):
        """Inicia threads para escuchar UDP y TCP."""
        self.running = True
        threading.Thread(target=self._listen_udp, daemon=True).start()
        threading.Thread(target=self._listen_tcp, daemon=True).start()
        logger.info(f"Listener iniciado en puerto {self.listen_port}")

    def stop(self):
        """Detiene los listeners."""
        self.running = False
        if self.udp_sock:
            self.udp_sock.close()
        if self.tcp_sock:
            self.tcp_sock.close()

    def _listen_udp(self):
        """Escucha paquetes UDP."""
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind(("", self.listen_port))
        logger.info(f"UDP listener en puerto {self.listen_port}")

        while self.running:
            try:
                self.udp_sock.settimeout(2)
                data, addr = self.udp_sock.recvfrom(1024)
                packet_info = {
                    "src_ip": addr[0],
                    "src_port": addr[1],
                    "dst_ip": None,
                    "dst_port": self.listen_port,
                    "protocol": "UDP",
                    "payload": data.decode("utf-8", errors="ignore"),
                }
                self.on_packet_callback(packet_info)
            except socket.timeout:
                pass
            except Exception as e:
                if self.running:
                    logger.error(f"Error UDP: {e}")

    def _listen_tcp(self):
        """Escucha conexiones TCP."""
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind(("", self.listen_port + 100))
        self.tcp_sock.listen(5)
        logger.info(f"TCP listener en puerto {self.listen_port + 100}")

        while self.running:
            try:
                self.tcp_sock.settimeout(2)
                client_sock, addr = self.tcp_sock.accept()
                packet_info = {
                    "src_ip": addr[0],
                    "src_port": addr[1],
                    "dst_ip": None,
                    "dst_port": self.listen_port + 100,
                    "protocol": "TCP",
                    "payload": "",
                }
                self.on_packet_callback(packet_info)
                client_sock.close()
            except socket.timeout:
                pass
            except Exception as e:
                if self.running:
                    logger.error(f"Error TCP: {e}")
