import redis
import scapy.all as scapy
import re
import time
import threading

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# RegEx simplificada para FQDN
hostname_regex = re.compile(r"^(?=.{1,255}$)([a-zA-Z0-9_-]+\.)*[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$")

# Callback para captura de pacotes
def packet_callback(packet):
    redis_conn = connect_redis()
    if packet.haslayer(scapy.IP):
        src_ip = packet[scapy.IP].src
        dst_ip = packet[scapy.IP].dst
        src_mac = packet.src
        dst_mac = packet.dst
        src_hostname = src_ip if not hostname_regex.match(src_ip) else "unknown"
        dst_hostname = dst_ip if not hostname_regex.match(dst_ip) else "unknown"

        data = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_mac": src_mac,
            "dst_mac": dst_mac,
            "src_hostname": src_hostname,
            "dst_hostname": dst_hostname
        }
        
        if redis_conn:
            redis_conn.rpush("network_packets", str(data))

# Função para capturar pacotes continuamente
def start_sniffing():
    global r
    r = connect_redis()
    if r:
        print('Iniciando a captura de pacotes...')
        try:
            scapy.sniff(prn=packet_callback, store=0, iface='eth0', promisc=True)
        except Exception as e:
            print(f"Erro durante a captura de pacotes: {str(e)}")
    else:
        print('Não foi possível iniciar a captura de pacotes devido à falha na conexão com o Redis.')

# Função para criar arquivos .txt a cada 2 horas
def create_backup_file():
    while True:
        time.sleep(2 * 60 * 60)  # 2 horas
        redis_conn = connect_redis()
        if redis_conn:
            packets = redis_conn.lrange("network_packets", 0, -1)
            with open("packet_capture_backup.txt", "w") as file:
                file.write("\n".join(packets))
            redis_conn.delete("network_packets")

# Executar captura de pacotes em um thread separado
threading.Thread(target=start_sniffing).start()
threading.Thread(target=create_backup_file).start()
