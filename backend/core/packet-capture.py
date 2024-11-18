import redis
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.http import HTTP
import re
import time
import threading
import json
from collections import defaultdict
import logging
import socket
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='network_capture.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NetworkPacketAnalyzer:
    def __init__(self):
        self.redis_conn = None
        self.hostname_regex = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.packet_stats = defaultdict(int)
        self.connection_tracking = defaultdict(lambda: {
            'start_time': None,
            'packets': 0,
            'bytes': 0,
            'protocols': set()
        })
        self.suspicious_patterns = {
            'port_scan': defaultdict(int),
            'high_traffic': defaultdict(lambda: {'bytes': 0, 'last_reset': time.time()}),
            'failed_connections': defaultdict(int)
        }
        self.initialize_redis()

    def initialize_redis(self):
        """Inicializa a conexão com Redis com retry automático"""
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.redis_conn = redis.StrictRedis(
                    host='localhost',
                    port=6380,
                    db=0,
                    decode_responses=True
                )
                self.redis_conn.ping()
                logging.info("Conexão com Redis estabelecida com sucesso")
                return
            except redis.ConnectionError as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Tentativa {attempt + 1} falhou. Tentando novamente em {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"Falha ao conectar ao Redis após {max_retries} tentativas: {e}")
                    raise

    def resolve_hostname(self, ip):
        """Resolve hostname a partir do IP com cache"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname if self.hostname_regex.match(hostname) else ip
        except (socket.herror, socket.gaierror):
            return ip

    def analyze_protocol(self, packet):
        """Analisa detalhes específicos do protocolo"""
        protocol_info = {
            'protocol': 'unknown',
            'src_port': None,
            'dst_port': None,
            'flags': None,
            'payload_size': 0
        }

        if TCP in packet:
            protocol_info.update({
                'protocol': 'TCP',
                'src_port': packet[TCP].sport,
                'dst_port': packet[TCP].dport,
                'flags': packet[TCP].flags
            })
        elif UDP in packet:
            protocol_info.update({
                'protocol': 'UDP',
                'src_port': packet[UDP].sport,
                'dst_port': packet[UDP].dport
            })
        elif ICMP in packet:
            protocol_info.update({
                'protocol': 'ICMP',
                'type': packet[ICMP].type,
                'code': packet[ICMP].code
            })

        if packet.haslayer(scapy.Raw):
            protocol_info['payload_size'] = len(packet[scapy.Raw].load)

        return protocol_info

    def detect_suspicious_activity(self, packet, protocol_info):
        """Detecta atividades suspeitas no tráfego"""
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            # Detecção de port scan
            if protocol_info['protocol'] == 'TCP':
                key = f"{src_ip}_{dst_ip}"
                self.suspicious_patterns['port_scan'][key] += 1
                
                # Alerta se muitas portas diferentes forem acessadas em pouco tempo
                if self.suspicious_patterns['port_scan'][key] > 20:
                    self.record_suspicious_activity({
                        'type': 'port_scan',
                        'source_ip': src_ip,
                        'target_ip': dst_ip,
                        'ports_attempted': self.suspicious_patterns['port_scan'][key],
                        'timestamp': datetime.now().isoformat()
                    })
                    self.suspicious_patterns['port_scan'][key] = 0

            # Detecção de tráfego anormal
            current_time = time.time()
            traffic_key = f"{src_ip}_{dst_ip}"
            traffic_data = self.suspicious_patterns['high_traffic'][traffic_key]
            
            # Reset contador se passou mais de 1 minuto
            if current_time - traffic_data['last_reset'] > 60:
                traffic_data['bytes'] = 0
                traffic_data['last_reset'] = current_time

            traffic_data['bytes'] += len(packet)
            
            # Alerta se o tráfego exceder 1MB por minuto
            if traffic_data['bytes'] > 1_000_000:
                self.record_suspicious_activity({
                    'type': 'high_traffic',
                    'source_ip': src_ip,
                    'target_ip': dst_ip,
                    'bytes_transferred': traffic_data['bytes'],
                    'timestamp': datetime.now().isoformat()
                })
                traffic_data['bytes'] = 0

            # Detecção de falhas de conexão TCP
            if protocol_info['protocol'] == 'TCP' and protocol_info['flags'] == 0x04:  # RST flag
                self.suspicious_patterns['failed_connections'][src_ip] += 1
                
                if self.suspicious_patterns['failed_connections'][src_ip] > 10:
                    self.record_suspicious_activity({
                        'type': 'failed_connections',
                        'source_ip': src_ip,
                        'count': self.suspicious_patterns['failed_connections'][src_ip],
                        'timestamp': datetime.now().isoformat()
                    })
                    self.suspicious_patterns['failed_connections'][src_ip] = 0

    def record_suspicious_activity(self, activity_data):
        """Registra atividades suspeitas no Redis"""
        try:
            self.redis_conn.rpush('suspicious_activities', json.dumps(activity_data))
            logging.warning(f"Atividade suspeita detectada: {activity_data}")
        except redis.RedisError as e:
            logging.error(f"Erro ao registrar atividade suspeita: {e}")

    def process_packet(self, packet):
        """Processa cada pacote capturado"""
        try:
            if not packet.haslayer(IP):
                return

            # Extrai informações básicas do pacote
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol_info = self.analyze_protocol(packet)
            
            # Analisa comportamento suspeito
            self.detect_suspicious_activity(packet, protocol_info)

            # Prepara dados do pacote para armazenamento
            packet_data = {
                "timestamp": datetime.now().isoformat(),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_hostname": self.resolve_hostname(src_ip),
                "dst_hostname": self.resolve_hostname(dst_ip),
                "protocol": protocol_info['protocol'],
                "src_port": protocol_info.get('src_port'),
                "dst_port": protocol_info.get('dst_port'),
                "flags": protocol_info.get('flags'),
                "payload_size": protocol_info.get('payload_size', 0),
                "packet_size": len(packet)
            }

            # Atualiza estatísticas
            self.update_statistics(packet_data)

            # Armazena no Redis
            self.store_packet_data(packet_data)

        except Exception as e:
            logging.error(f"Erro ao processar pacote: {e}")

    def update_statistics(self, packet_data):
        """Atualiza estatísticas de tráfego"""
        try:
            stats_key = f"stats:{datetime.now().strftime('%Y-%m-%d:%H')}"
            
            # Incrementa contadores
            pipe = self.redis_conn.pipeline()
            pipe.hincrby(stats_key, 'total_packets', 1)
            pipe.hincrby(stats_key, f"protocol_{packet_data['protocol']}", 1)
            pipe.hincrby(stats_key, 'total_bytes', packet_data['packet_size'])
            
            # Adiciona IPs únicos
            pipe.sadd(f"{stats_key}:unique_src_ips", packet_data['src_ip'])
            pipe.sadd(f"{stats_key}:unique_dst_ips", packet_data['dst_ip'])
            
            # Executa todas as operações
            pipe.execute()
            
        except redis.RedisError as e:
            logging.error(f"Erro ao atualizar estatísticas: {e}")

    def store_packet_data(self, packet_data):
        """Armazena dados do pacote no Redis"""
        try:
            self.redis_conn.rpush("network_packets", json.dumps(packet_data))
        except redis.RedisError as e:
            logging.error(f"Erro ao armazenar dados do pacote: {e}")

    def create_backup(self):
        """Cria backup dos dados periodicamente"""
        while True:
            try:
                time.sleep(300)  # 5 minutos
                
                # Backup de pacotes
                packets = self.redis_conn.lrange("network_packets", 0, -1)
                if packets:
                    backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_path = f"/home/zrdax/SehenOS/test/logs/packet_capture_backup_{backup_time}.txt"
                    
                    with open(backup_path, "w") as file:
                        for packet in packets:
                            file.write(f"{packet}\n")
                    
                    # Limpa dados após backup
                    self.redis_conn.delete("network_packets")
                    logging.info(f"Backup criado: {backup_path}")

                # Backup de atividades suspeitas
                suspicious = self.redis_conn.lrange("suspicious_activities", 0, -1)
                if suspicious:
                    suspicious_backup_path = f"/home/zrdax/SehenOS/test/logs/suspicious_activities_{backup_time}.txt"
                    
                    with open(suspicious_backup_path, "w") as file:
                        for activity in suspicious:
                            file.write(f"{activity}\n")
                    
                    self.redis_conn.delete("suspicious_activities")
                    logging.info(f"Backup de atividades suspeitas criado: {suspicious_backup_path}")

            except Exception as e:
                logging.error(f"Erro durante backup: {e}")

    def start_capture(self, interface='eth0'):
        """Inicia a captura de pacotes"""
        logging.info(f"Iniciando captura na interface {interface}")
        
        # Inicia thread de backup
        threading.Thread(target=self.create_backup, daemon=True).start()
        
        try:
            # Inicia captura de pacotes
            scapy.sniff(
                prn=self.process_packet,
                store=0,
                iface=interface,
                promisc=True
            )
        except Exception as e:
            logging.error(f"Erro durante a captura de pacotes: {e}")

if __name__ == "__main__":
    try:
        analyzer = NetworkPacketAnalyzer()
        analyzer.start_capture()
    except Exception as e:
        logging.critical(f"Erro fatal na aplicação: {e}")
