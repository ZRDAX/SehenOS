from scapy.all import sniff
import psycopg2
import re

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos_db",
            user="sehenos",
            password="swiredb",
            host="db"  # Nome do serviço no Docker Compose
        )
        return conn
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
        if src_hostname:
            src_hostname = src_hostname.group(0)
        else:
            src_hostname = None

    if dst_ip:
        dst_hostname = re.search(hostname_regex, dst_ip)
        if dst_hostname:
            dst_hostname = dst_hostname.group(0)
        else:
            dst_hostname = None

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
    except Exception as e:
        print(f"Erro ao inserir dados no banco de dados: {e}")

# Função principal de callback para a captura de pacotes
def packet_callback(packet):
    src_ip, src_hostname, dst_ip, dst_hostname = extract_info(packet)
    conn = connect_db()
    if conn:
        insert_packet_data(conn, src_ip, src_hostname, dst_ip, dst_hostname)
        conn.close()

# Iniciar a captura de pacotes
def start_sniffing():
    sniff(prn=packet_callback, filter="ip", store=0)

if __name__ == "__main__":
    start_sniffing()
