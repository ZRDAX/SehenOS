import scapy.all as scapy
import time
import json
import threading
import requests
from datetime import datetime
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.dns import DNS
from scapy.layers.l2 import Ether
import socket
from config.redis_config import redis_client
from app.config import Config
from config.settings import REMOTE_BLACKLIST_URL
import os
import logging
import gzip

# Configuração de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carregar Blacklist e Whitelist
def load_blacklist_whitelist():
    try:
        with open(Config.BLACKLIST_FILE, 'r') as f:
            blacklist = set(line.strip() for line in f)
    except FileNotFoundError:
        blacklist = set()

    try:
        with open(Config.WHITELIST_FILE, 'r') as f:
            whitelist = set(line.strip() for line in f)
    except FileNotFoundError:
        whitelist = set()

    return blacklist, whitelist

# Buscar Blacklist Remota
def fetch_remote_blacklist():
    try:
        response = requests.get(REMOTE_BLACKLIST_URL)
        response.raise_for_status()
        return set(response.text.splitlines())
    except Exception as e:
        logging.error(f"Erro ao buscar blacklist remota: {e}")
        return set()

# Resolução Reversa de DNS
def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

processed_packets = set()

def process_packet(packet):
    if not packet.haslayer(IP):
        return

    data = {
        "timestamp": datetime.now().isoformat(),
        "src_ip": packet[IP].src,
        "dst_ip": packet[IP].dst,
        "protocol": getattr(packet[IP], "proto", None),
        "length": len(packet),
        "mac_src": packet[Ether].src if packet.haslayer(Ether) else None,
        "mac_dst": packet[Ether].dst if packet.haslayer(Ether) else None,
        "time_to_live": getattr(packet[IP], "ttl", None),
        "is_blacklisted": (packet[IP].src in blacklist or packet[IP].dst in blacklist),
        "is_whitelisted": (packet[IP].src in whitelist or packet[IP].dst in whitelist),
    }

    # Portas e flags TCP/UDP
    if packet.haslayer(TCP):
        data.update({
            "src_port": getattr(packet[TCP], "sport", None),
            "dst_port": getattr(packet[TCP], "dport", None),
            "tcp_flags": str(getattr(packet[TCP], "flags", None)),
        })
    elif packet.haslayer(UDP):
        data.update({
            "src_port": getattr(packet[UDP], "sport", None),
            "dst_port": getattr(packet[UDP], "dport", None),
        })

    # DNS
    if packet.haslayer(DNS):
        dns_layer = packet[DNS]
        dns_queries = None
        if hasattr(dns_layer, "qd") and dns_layer.qd:
            dns_queries = getattr(dns_layer.qd, "qname", b"").decode("utf-8", errors="ignore")
        data.update({
            "dns_queries": dns_queries,
            "fqdns": reverse_dns(packet[IP].dst),
        })

    # Payload
    if hasattr(packet[IP], "payload"):
        raw_payload = bytes(packet[IP].payload)
        data["payload"] = raw_payload.hex() if raw_payload else None
    else:
        data["payload"] = None

    # Volume (bytes)
    data["bytes"] = len(packet)

    # Serialização e envio para Redis
    try:
        redis_client.rpush("network_packets", json.dumps(data))
    except TypeError as e:
        logging.error(f"Erro ao serializar pacote: {e}")
        logging.debug(f"Dados problemáticos: {data}")


# Iniciar Captura de Pacotes
def start_capture():
    logging.info("Iniciando captura de pacotes...")
    scapy.sniff(prn=process_packet, store=False)

# Gerenciamento de Backup de Pacotes
def save_backup():
    while True:
        time.sleep(180)
        packets = redis_client.lrange("network_packets", 0, -1)
        redis_client.delete("network_packets")

        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        backup_file = f"{Config.BACKUP_DIR}/packets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.gz"
        try:
            with gzip.open(backup_file, "wt", encoding="utf-8") as f:
                f.write(json.dumps([json.loads(packet) for packet in packets]))
            logging.info(f"Backup de pacotes salvo: {backup_file}")
        except Exception as e:
            logging.error(f"Erro ao salvar backup: {e}")

if __name__ == "__main__":
    blacklist, whitelist = load_blacklist_whitelist()
    remote_blacklist = fetch_remote_blacklist()
    blacklist.update(remote_blacklist)

    threading.Thread(target=save_backup, daemon=True).start()
    start_capture()
