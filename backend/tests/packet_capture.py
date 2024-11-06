# packet_capture.py
import os
import pandas as pd
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import sessionmaker
from scapy.all import sniff, IP, Ether
import re
import redis
import json
import uuid

# Conexão com o banco de dados PostgreSQL usando SQLAlchemy
def connect_db():
    try:
        # Atualize o host para o nome do serviço no Docker Compose
        engine = create_engine('postgresql://cypher:piswos@localhost:5432/sehenos-db')
        print('Conexão estabelecida com sucesso.')
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Função para extrair IP, hostname e FQDN usando RegEx
def extract_info(packet):
    src_ip = packet[IP].src if packet.haslayer(IP) else None
    dst_ip = packet[IP].dst if packet.haslayer(IP) else None
    src_mac = packet[Ether].src if packet.haslayer(Ether) else None
    dst_mac = packet[Ether].dst if packet.haslayer(Ether) else None
    hostname_regex = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # RegEx simplificada para FQDN

    src_hostname = re.search(hostname_regex, src_ip).group(0) if src_ip and re.search(hostname_regex, src_ip) else None
    dst_hostname = re.search(hostname_regex, dst_ip).group(0) if dst_ip and re.search(hostname_regex, dst_ip) else None

    return src_ip, src_hostname, src_mac, dst_ip, dst_hostname, dst_mac

# Armazenar dados no Redis
def store_packet_in_redis(r, src_ip, src_hostname, src_mac, dst_ip, dst_hostname, dst_mac):
    try:
        # Cria uma chave única para o pacote
        packet_id = f"packet:{uuid.uuid4()}"
        packet_data = {
            "src_ip": src_ip,
            "src_hostname": src_hostname,
            "src_mac": src_mac,
            "dst_ip": dst_ip,
            "dst_hostname": dst_hostname,
            "dst_mac": dst_mac,
        }
        r.set(packet_id, json.dumps(packet_data))
        print(f"Pacote armazenado no Redis com a chave: {packet_id}")
    except Exception as e:
        print(f"Erro ao armazenar o pacote no Redis: {e}")

# Função principal de callback para a captura de pacotes
def packet_callback(packet):
    src_ip, src_hostname, src_mac, dst_ip, dst_hostname, dst_mac = extract_info(packet)
    print("Dados capturados:", src_ip, src_hostname, src_mac, dst_ip, dst_hostname, dst_mac)
    if r:
        store_packet_in_redis(r, src_ip, src_hostname, src_mac, dst_ip, dst_hostname, dst_mac)

# Iniciar a captura de pacotes
def start_sniffing():
    global r
    r = connect_redis()
    if r:
        print('Iniciando a captura de pacotes...')
        try:
            sniff(prn=packet_callback, store=0, iface='eth0', promisc=True)
        except Exception as e:
            print(f"Erro durante a captura de pacotes: {str(e)}")
    else:
        print('Não foi possível iniciar a captura de pacotes devido à falha na conexão com o Redis.')

if __name__ == "__main__":
    start_sniffing()
