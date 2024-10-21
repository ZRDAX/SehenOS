import os
import redis
import json
from scapy.all import sniff, IP
import re

# Conexão com o Redis
def connect_redis():
    try:
        redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
        return redis_client
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Função para extrair IP, hostname e FQDN usando RegEx
def extract_info(packet):
    src_ip = packet[IP].src if packet.haslayer(IP) else None
    dst_ip = packet[IP].dst if packet.haslayer(IP) else None
    hostname_regex = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # RegEx simplificada para FQDN

    src_hostname = re.search(hostname_regex, src_ip).group(0) if src_ip and re.search(hostname_regex, src_ip) else None
    dst_hostname = re.search(hostname_regex, dst_ip).group(0) if dst_ip and re.search(hostname_regex, dst_ip) else None

    return src_ip, src_hostname, dst_ip, dst_hostname

# Função para armazenar pacotes no Redis
def store_packet_in_redis(redis_client, packet_data):
    try:
        redis_client.lpush('network_packets', packet_data)
        print("Pacote armazenado no Redis.")
    except Exception as e:
        print(f"Erro ao armazenar pacote no Redis: {e}")

# Função principal de callback para a captura de pacotes
def packet_callback(packet):
    src_ip, src_hostname, dst_ip, dst_hostname = extract_info(packet)
    print("Dados capturados:", src_ip, src_hostname, dst_ip, dst_hostname)
    
    # Conectar ao Redis
    redis_client = connect_redis()
    if redis_client:
        packet_data = {
            'src_ip': src_ip,
            'src_hostname': src_hostname,
            'dst_ip': dst_ip,
            'dst_hostname': dst_hostname
        }
        store_packet_in_redis(redis_client, json.dumps(packet_data))

# Iniciar a captura de pacotes
def start_sniffing():
    try:
        print('Iniciando a captura de pacotes...')
        sniff(prn=packet_callback, store=0, iface='eth0', promisc=True)
    except Exception as e:
        print(f"Erro durante a captura de pacotes: {str(e)}")

if __name__ == "__main__":
    start_sniffing()
