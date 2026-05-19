import socket
import argparse
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrafficGenerator")


def send_udp(dst_ip: str, dst_port: int, count: int, interval: float, message: str):
    """Envía paquetes UDP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(count):
        try:
            payload = f"{message} #{i+1}".encode()
            sock.sendto(payload, (dst_ip, dst_port))
            logger.info(f"UDP enviado a {dst_ip}:{dst_port} - {payload.decode()}")
            time.sleep(interval)
        except Exception as e:
            logger.error(f"Error enviando UDP: {e}")
    sock.close()


def send_tcp(dst_ip: str, dst_port: int, count: int, interval: float, message: str):
    """Envía paquetes TCP."""
    for i in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((dst_ip, dst_port))
            payload = f"{message} #{i+1}".encode()
            sock.send(payload)
            logger.info(f"TCP enviado a {dst_ip}:{dst_port} - {payload.decode()}")
            sock.close()
            time.sleep(interval)
        except Exception as e:
            logger.error(f"Error enviando TCP: {e}")


def main():
    """Generador de tráfico con opciones CLI."""
    parser = argparse.ArgumentParser(description="Generador de tráfico UDP/TCP")
    parser.add_argument("--dst", required=True, help="IP destino")
    parser.add_argument("--port", type=int, required=True, help="Puerto destino")
    parser.add_argument("--proto", choices=["udp", "tcp"], default="udp", help="Protocolo")
    parser.add_argument("--count", type=int, default=10, help="Cantidad de paquetes")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo entre paquetes (segundos)")
    parser.add_argument("--message", default="TEST", help="Mensaje en payload")

    args = parser.parse_args()

    logger.info(f"Enviando {args.count} paquetes {args.proto.upper()} a {args.dst}:{args.port}")

    if args.proto.lower() == "udp":
        send_udp(args.dst, args.port, args.count, args.interval, args.message)
    else:
        send_tcp(args.dst, args.port, args.count, args.interval, args.message)

    logger.info("Generación completada")


if __name__ == "__main__":
    main()
