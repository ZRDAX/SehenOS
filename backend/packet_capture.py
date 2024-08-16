#backend/packet_capture.py
from scapy.all import sniff, IP
import psycopg2
import re

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos_db",
            user="sehenos",
            password="piswos",
            host="sehenos_db",  # Nome do serviço no Docker Compose
            port="5432"
        )
        print("Connect to db: ", conn.get_dsn_parameters())
        print('Conexão estabelecida com sucesso.')
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para extrair IP, hostname e FQDN usando RegEx
def extract_info(packet):
    src_ip = packet[0][1].src if packet.haslayer("IP") else None
    dst_ip = packet[0][1].dst if packet.haslayer("IP") else None
    hostname_regex = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # RegEx simplificada para FQDN

    if src_ip:
        src_hostname = re.search(hostname_regex, src_ip)
        src_hostname = src_hostname.group(0) if src_hostname else None

    if dst_ip:
        dst_hostname = re.search(hostname_regex, dst_ip)
        dst_hostname = dst_hostname.group(0) if dst_hostname else None

    return src_ip, src_hostname, dst_ip, dst_hostname

# Função para inserir dados no PostgreSQL
def insert_packet_data(conn, src_ip, src_hostname, dst_ip, dst_hostname):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO network_traffic (src_ip, src_hostname, dst_ip, dst_hostname)
            VALUES (%s, %s, %s, %s);
        """, (src_ip, src_hostname, dst_ip, dst_hostname))
        conn.commit()
        cur.close()
        print(f"Dados inseridos: src_ip={src_ip}, src_hostname={src_hostname}, dst_ip={dst_ip}, dst_hostname={dst_hostname}")
    except psycopg2.Error as e:
        print(f" /problema-atual/ Erro ao inserir dados no banco de dados: {e.pgcode} - {e.pgerror}")
        print(f"Detalhes da exceção: {str(e)}")
        conn.rollback()

# Função principal de callback para a captura de pacotes
def packet_callback(packet):
    src_ip, src_hostname, dst_ip, dst_hostname = extract_info(packet)
    print("Dados capturados:", src_ip, src_hostname, dst_ip, dst_hostname)
    if conn:
        insert_packet_data(conn, src_ip, src_hostname, dst_ip, dst_hostname)

# Iniciar a captura de pacotes
def start_sniffing():
    global conn
    conn = connect_db()
    if conn:
        print('Iniciando a captura de pacotes...')
        sniff(prn=packet_callback, filter="ip", store=0, iface='eth0', promisc=True)
        conn.close()
    else:
        print('Não foi possivel iniciar a captura de pacotes devido à falha na conexão com o banco de dados.')

if __name__ == "__main__":
    start_sniffing()