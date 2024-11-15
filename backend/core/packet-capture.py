import os
import pandas as pd
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import sessionmaker
from scapy.all import sniff, IP
import re

# Conexão com o banco de dados PostgreSQL usando SQLAlchemy
def connect_db():
    try:
        # Atualize o host para o nome do serviço no Docker Compose
        engine = create_engine('postgresql://cypher:piswos@db:5432/sehenos-db')
        print('Conexão estabelecida com sucesso.')
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para criar a tabela se não existir
def create_table(engine):
    metadata = MetaData()
    network_traffic = Table('network_traffic', metadata,
        Column('id', String, primary_key=True),
        Column('src_ip', String),
        Column('src_hostname', String),
        Column('dst_ip', String),
        Column('dst_hostname', String)
    )
    metadata.create_all(engine)

# Função para extrair IP, hostname e FQDN usando RegEx
def extract_info(packet):
    src_ip = packet[IP].src if packet.haslayer(IP) else None
    dst_ip = packet[IP].dst if packet.haslayer(IP) else None
    hostname_regex = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # RegEx simplificada para FQDN

    src_hostname = re.search(hostname_regex, src_ip).group(0) if src_ip and re.search(hostname_regex, src_ip) else None
    dst_hostname = re.search(hostname_regex, dst_ip).group(0) if dst_ip and re.search(hostname_regex, dst_ip) else None

    return src_ip, src_hostname, dst_ip, dst_hostname
    
# Função para inserir dados no PostgreSQL usando SQLAlchemy
def insert_packet_data(engine, src_ip, src_hostname, dst_ip, dst_hostname):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        metadata = MetaData()
        network_traffic = Table('network_traffic', metadata, autoload_with=engine)
        
        insert_stmt = network_traffic.insert().values(
            src_ip=src_ip,
            src_hostname=src_hostname,
            dst_ip=dst_ip,
            dst_hostname=dst_hostname
        )
        session.execute(insert_stmt)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")
        session.rollback()
        session.close()

# Função principal de callback para a captura de pacotes
def packet_callback(packet):
    src_ip, src_hostname, dst_ip, dst_hostname = extract_info(packet)
    print("Dados capturados:", src_ip, src_hostname, dst_ip, dst_hostname)
    if engine:
        insert_packet_data(engine, src_ip, src_hostname, dst_ip, dst_hostname)

# Iniciar a captura de pacotes
def start_sniffing():
    global engine
    engine = connect_db()
    if engine:
        create_table(engine)
        try:
            print('Iniciando a captura de pacotes...')
            sniff(prn=packet_callback, store=0, iface='eth0', promisc=True)
        except Exception as e:
            print(f"Erro durante a captura de pacotes: {str(e)}")
    else:
        print('Não foi possível iniciar a captura de pacotes devido à falha na conexão com o banco de dados.')

if __name__ == "__main__":
    start_sniffing()
