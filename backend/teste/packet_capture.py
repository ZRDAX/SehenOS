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

# RegEx para verificar hostnames
hostname_regex = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

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

        # Garantindo que "network_packets" é uma lista antes de usar rpush
        try:
            if redis_conn.type("network_packets") not in ["none", "list"]:
                print("Tipo incorreto detectado para 'network_packets'. Redefinindo chave.")
                redis_conn.delete("network_packets")  # Limpa a chave incorreta

            redis_conn.rpush("network_packets", str(data))

        except redis.exceptions.ResponseError as e:
            print(f"Erro ao acessar a chave 'network_packets': {e}")

# Função para capturar pacotes continuamente
def start_sniffing():
    redis_conn = connect_redis()
    if redis_conn:
        print('Iniciando a captura de pacotes...')
        try:
            scapy.sniff(prn=packet_callback, store=0, iface='eth0', promisc=True)
        except Exception as e:
            print(f"Erro durante a captura de pacotes: {str(e)}")
    else:
        print('Não foi possível iniciar a captura de pacotes devido à falha na conexão com o Redis.')

# Função para criar backups periódicos
def create_backup_file():
    while True:
        #time.sleep(2 * 60 * 60)  # Espera por 2 horas
        time.sleep(5 * 60)  # Espera por 5 minutos para teste 
        redis_conn = connect_redis()
        if redis_conn:
            try:
                if redis_conn.type("network_packets") == "list":
                    packets = redis_conn.lrange("network_packets", 0, -1)
                else:
                    print("Tipo incorreto para 'network_packets'. Nenhum dado para backup.")
                    packets = []

            except redis.exceptions.ResponseError as e:
                print(f"Erro ao acessar a chave 'network_packets': {e}")
                packets = []

            if packets:
                with open("/home/zrdax/SehenOS/test/logs/packet_capture_backup.txt", "w") as file:
                    file.write("\n".join(packets))
                redis_conn.delete("network_packets")
                print("Backup dos pacotes realizado com sucesso.")
            else:
                print("Nenhum pacote encontrado para backup.")

# Inicializa a conexão Redis
redis_conn = connect_redis()

# Executa a captura de pacotes e o backup em threads separadas
if __name__ == "__main__":
    threading.Thread(target=start_sniffing, daemon=True).start()
    threading.Thread(target=create_backup_file, daemon=True).start()

    # Mantém a execução do programa principal
    while True:
        time.sleep(1)
