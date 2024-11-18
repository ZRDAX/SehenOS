import redis
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.arch import get_if_list
import threading
import time
import json
import logging
from datetime import datetime
import ipaddress
import socket
import hashlib
from typing import Dict, Any
from collections import defaultdict

class AdvancedNetworkPacketAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'redis_host': 'localhost',
            'redis_port': 6380,
            'log_file': 'network_capture_enhanced.log',
            'suspicious_threshold': {
                'port_scan': 15,
                'high_traffic': 5_000_000,  # 5MB
                'connection_attempts': 10
            }
        }
        
        # Configurações avançadas de segurança
        self.threat_signatures = {
            'known_malicious_ips': set(),
            'suspicious_ports': {
                21, 22, 23, 3389, 445, 135, 137, 138, 139  # Portas comumente atacadas
            }
        }
        
        self.connection_tracking = {
            'ip_connection_count': defaultdict(int),
            'port_connection_attempts': defaultdict(int),
            'traffic_volume': defaultdict(int)
        }
        
        self._setup_logging()
        self._initialize_redis()
        self._load_threat_intelligence()

    def _setup_logging(self):
        logging.basicConfig(
            filename=self.config['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    def _initialize_redis(self):
        try:
            self.redis_client = redis.Redis(
                host=self.config['redis_host'], 
                port=self.config['redis_port']
            )
            self.redis_client.ping()
        except Exception as e:
            logging.critical(f"Redis connection failed: {e}")
            raise

    def _load_threat_intelligence(self):
        # Método para carregar IPs maliciosos de fontes externas
        # Pode ser expandido para integrar com feeds de inteligência de ameaças
        try:
            # Exemplo simplificado, na prática integraria com API externa
            malicious_ips = [
                '220.166.14.129',
                '51.161.152.203'
            ]
            self.threat_signatures['known_malicious_ips'].update(malicious_ips)
        except Exception as e:
            logging.warning(f"Threat intelligence load failed: {e}")

    def _generate_packet_signature(self, packet):
        """Gera uma assinatura única para o pacote"""
        try:
            packet_data = f"{packet[IP].src}:{packet[IP].dst}"
            return hashlib.md5(packet_data.encode()).hexdigest()
        except Exception:
            return None

    def analyze_packet(self, packet):
        #Análise avançada de pacotes com tratamento de erros e validações
        try:
            # Verifica se o pacote tem camada IP
            if not packet.haslayer(IP):
                return None

            # Extração segura de metadados
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
            # Validação de endereços IP
            if not self._validate_ip_address(src_ip) or not self._validate_ip_address(dst_ip):
                logging.warning(f"Invalid IP addresses: {src_ip} -> {dst_ip}")
                return None
            
            # Verificações de segurança
            try:
                self._check_ip_reputation(src_ip, dst_ip)
                self._track_connection_attempts(src_ip, dst_ip)
            except Exception as security_error:
                logging.error(f"Security check failed: {security_error}")
                return None
            
            # Determinação do protocolo de forma mais robusta
            protocol = 'Unknown'
            if packet.haslayer(TCP):
                protocol = 'TCP'
            elif packet.haslayer(UDP):
                protocol = 'UDP'
            elif packet.haslayer(ICMP):
                protocol = 'ICMP'
            
            # Geração de assinatura
            try:
                packet_signature = self._generate_packet_signature(packet)
            except Exception as sig_error:
                logging.error(f"Signature generation failed: {sig_error}")
                packet_signature = None
            
            # Construção de informações do pacote
            packet_info = {
                'timestamp': datetime.now().isoformat(),
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'signature': packet_signature,
                'protocol': protocol,
                'length': len(packet),
                'additional_details': {
                    'src_port': packet[TCP].sport if packet.haslayer(TCP) else packet[UDP].sport if packet.haslayer(UDP) else None,
                    'dst_port': packet[TCP].dport if packet.haslayer(TCP) else packet[UDP].dport if packet.haslayer(UDP) else None,
                }
            }
            
            return packet_info
        
        except Exception as e:
            logging.error(f"Comprehensive packet analysis error: {e}")
            return None
        
    def _validate_ip_address(self, ip_address):
        """Validação de endereço IP"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def _check_ip_reputation(self, src_ip, dst_ip):
        """Verifica reputação dos IPs"""
        if src_ip in self.threat_signatures['known_malicious_ips']:
            logging.warning(f"Potencial IP malicioso detectado: {src_ip}")
            self._report_threat(src_ip, 'malicious_ip')

    def _track_connection_attempts(self, src_ip, dst_ip):
        """Rastreia tentativas de conexão"""
        self.connection_tracking['ip_connection_count'][src_ip] += 1
        
        if self.connection_tracking['ip_connection_count'][src_ip] > self.config['suspicious_threshold']['connection_attempts']:
            self._report_threat(src_ip, 'excessive_connections')

    def _report_threat(self, ip, threat_type):
        """Reporta ameaças detectadas"""
        threat_data = {
            'ip': ip,
            'type': threat_type,
            'timestamp': datetime.now().isoformat()
        }
        try:
            self.redis_client.rpush('network_threats', json.dumps(threat_data))
        except Exception as e:
            logging.error(f"Threat reporting failed: {e}")

    def start_packet_capture(self, interface='eth0'):
        """Inicia captura de pacotes"""
        if interface not in get_if_list():
            raise ValueError(f"Interface {interface} não encontrada!")

        logging.info(f"Iniciando captura na interface {interface}")
        try:
            scapy.sniff(
                prn=self.process_packet,
                store=0,
                iface=interface,
                promisc=True
            )
        except Exception as e:
            logging.critical(f"Capture error: {e}")

    def process_packet(self, packet):
        """Processa pacote capturado"""
        analyzed_packet = self.analyze_packet(packet)
        
        if analyzed_packet:
            try:
                self.redis_client.rpush(
                    'processed_packets', 
                    json.dumps(analyzed_packet)
                )
            except Exception as e:
                logging.error(f"Redis storage failed: {e}")

def main():
    analyzer = AdvancedNetworkPacketAnalyzer()
    analyzer.start_packet_capture("eth0")

if __name__ == "__main__":
    main()