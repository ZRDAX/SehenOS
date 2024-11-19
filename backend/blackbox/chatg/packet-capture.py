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
import re
import socket

class AdvancedNetworkPacketAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'redis_host': 'localhost',
            'redis_port': 6380,
            'log_file': f'logs/netinfo.log',
            'suspicious_threshold': {
                'port_scan': 15,
                'high_traffic': 5_000_000,  # 5MB
                'connection_attempts': 10
            }
        }
        
        # Novas adições para detecção de domínios e IPs maliciosos
        self.malicious_domains = {
            'gambling': [
                'krunker.io', 
                'csgoempire.com', 
                'csgofast.com'
            ],
            'malware': [
                'malware-download.com',
                'suspicious-site.net'
            ],
            'phishing': [
                'fake-bank.com',
                'phishing-site.org'
            ]
        }
        
        self.blacklisted_ips = set()
        self.threat_intelligence_sources = [
            'https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset'
        ]
        
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
        self.load_blacklisted_ips()  # Novo método para carregar IPs de blacklist
        
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
    
    def load_blacklisted_ips(self):
        """Carrega IPs de fontes de inteligência de ameaças"""
        try:
            for source in self.threat_intelligence_sources:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    ips = [
                        line.strip() 
                        for line in response.text.split('\n') 
                        if line and not line.startswith('#')
                    ]
                    self.blacklisted_ips.update(ips)
            
            logging.info(f"Carregados {len(self.blacklisted_ips)} IPs de blacklist")
        except Exception as e:
            logging.error(f"Erro ao carregar IPs de blacklist: {e}")

    def resolve_domain(self, hostname):
        """Resolve hostname para IP"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

    def check_domain_reputation(self, domain):
        """Verifica reputação do domínio"""
        malicious_categories = []
        
        for category, domains in self.malicious_domains.items():
            if any(bad_domain in domain for bad_domain in domains):
                malicious_categories.append(category)
        
        return malicious_categories

    def is_ip_blacklisted(self, ip):
        """Verifica se o IP está na blacklist"""
        try:
            # Converte para string de IP
            ip_str = str(ipaddress.ip_address(ip))
            
            # Verifica na lista de blacklist
            return ip_str in self.blacklisted_ips
        except ValueError:
            return False

    def _check_ip_reputation(self, src_ip, dst_ip):
        """Verifica reputação dos IPs com novos checks"""
        # Verifica IPs maliciosos conhecidos
        if src_ip in self.threat_signatures['known_malicious_ips']:
            logging.warning(f"Potencial IP malicioso detectado: {src_ip}")
            self._report_threat(src_ip, 'malicious_ip')
        
        # Novo check de blacklist
        if self.is_ip_blacklisted(src_ip):
            logging.warning(f"IP encontrado em blacklist: {src_ip}")
            self._report_threat(src_ip, 'blacklisted_ip')

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
        
            # Extração de domínio (novo)
            domain = self._extract_domain(packet)
            domain_categories = []
        
            # Verificação de reputação de domínio (novo)
            if domain:
                domain_categories = self.check_domain_reputation(domain)
                if domain_categories:
                    logging.warning(f"Malicious domain detected: {domain} - Categories: {domain_categories}")
                    self._report_threat(src_ip, f'malicious_domain_{",".join(domain_categories)}')
        
            # Verificação de IP em blacklist (novo)
            src_ip_blacklisted = self.is_ip_blacklisted(src_ip)
            dst_ip_blacklisted = self.is_ip_blacklisted(dst_ip)
        
            # Construção de informações do pacote
            packet_info = {
                'timestamp': datetime.now().isoformat(),
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'signature': packet_signature,
                'protocol': protocol,
                'length': len(packet),
                'domain': domain,
                'domain_reputation': {
                    'categories': domain_categories
                },
                'ip_reputation': {
                    'src_ip_blacklisted': src_ip_blacklisted,
                    'dst_ip_blacklisted': dst_ip_blacklisted
                },
                'additional_details': {
                    'src_port': packet[TCP].sport if packet.haslayer(TCP) else packet[UDP].sport if packet.haslayer(UDP) else None,
                    'dst_port': packet[TCP].dport if packet.haslayer(TCP) else packet[UDP].dport if packet.haslayer(UDP) else None,
                }
            }
        
            return packet_info
    
        except Exception as e:
            logging.error(f"Comprehensive packet analysis error: {e}")
            return None

    def _extract_domain(self, packet):
        """Tenta extrair domínio do pacote com múltiplas estratégias"""
        try:
            # Estratégia 1: Pacotes DNS
            if packet.haslayer(scapy.DNS):
                try:
                    # Extração de domínio de consultas DNS
                    if packet[scapy.DNS].qd:
                        return packet[scapy.DNS].qd.qname.decode('utf-8').rstrip('.')
                except Exception as dns_error:
                    logging.debug(f"DNS domain extraction error: {dns_error}")

            # Estratégia 2: Camadas de payload HTTP
            if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.Raw):
                try:
                    payload = packet[scapy.Raw].load.decode('utf-8', errors='ignore')
                
                    # Padrões para extração de domínio
                    http_patterns = [
                        r'Host: ([^\r\n]+)',           # Cabeçalho Host padrão
                        r'https?://([^/\s]+)',          # URLs completas
                        r'\b([\w-]+\.[a-z]{2,})\b'     # Domínios genéricos
                    ]
                
                    for pattern in http_patterns:
                        domain_match = re.search(pattern, payload, re.IGNORECASE)
                        if domain_match:
                            domain = domain_match.group(1).strip()
                            # Validações adicionais
                            if self._is_valid_domain(domain):
                                return domain
                except Exception as http_error:
                    logging.debug(f"HTTP domain extraction error: {http_error}")

            # Estratégia 3: Extração de SNI (Server Name Indication) para TLS
            if packet.haslayer(scapy.TLS):
                try:
                    # Tenta extrair nome do servidor de extensões TLS
                    for ext in packet[scapy.TLS].extensions:
                        if ext.type == 0:  # Tipo de extensão SNI
                            server_name = ext.servernames[0].hostname.decode('utf-8')
                            if self._is_valid_domain(server_name):
                                return server_name
                except Exception as tls_error:
                    logging.debug(f"TLS SNI extraction error: {tls_error}")

            # Estratégia 4: Resolução reversa de IP
            try:
                if packet.haslayer(IP):
                    ip = packet[IP].dst  # Pode usar src ou dst
                    try:
                        domain = socket.gethostbyaddr(ip)[0]
                        if self._is_valid_domain(domain):
                            return domain
                    except socket.herror:
                        pass  # Falha na resolução reversa é esperada
            except Exception as ip_error:
                logging.debug(f"Reverse IP resolution error: {ip_error}")

            return None

        except Exception as e:
            logging.error(f"Comprehensive domain extraction error: {e}")
            return None

    def _is_valid_domain(self, domain):
        """Valida se o domínio extraído é válido"""
        try:
            # Critérios de validação de domínio
            if not domain:
                return False
        
            # Expressão regular para validação de domínio
            domain_regex = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,}$'
        
            if not re.match(domain_regex, domain):
                return False
        
            # Comprimento do domínio
            if len(domain) > 255:
                return False
        
            # Verifica se não contém caracteres inválidos
            if re.search(r'[^\w\.-]', domain):
                return False
        
            return True
    
        except Exception as e:
            logging.error(f"Domain validation error: {e}")
            return False
        
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
    analyzer.start_packet_capture('eth0')

if __name__ == "__main__":
    main()