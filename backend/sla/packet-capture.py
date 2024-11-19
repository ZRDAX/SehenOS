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
import requests

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
            },
            'backup_interval': 3600  # Backup a cada 1 hora
        }
        self.blacklisted_ips = set()
        self.whitelisted_ips = set()
        self.threat_intelligence_sources = [
            'https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset'
        ]
        self._setup_logging()
        self._initialize_redis()
        self.load_blacklisted_ips()
        self.last_backup_time = time.time()

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

    def load_blacklisted_ips(self):
        try:
            for source in self.threat_intelligence_sources:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    ips = [line.strip() for line in response.text.split('\n') if line and not line.startswith('#')]
                    self.blacklisted_ips.update(ips)
            logging.info(f"Carregados {len(self.blacklisted_ips)} IPs de blacklist")
        except Exception as e:
            logging.error(f"Erro ao carregar IPs de blacklist: {e}")

    def is_ip_blacklisted(self, ip):
        return ip in self.blacklisted_ips

    def is_ip_whitelisted(self, ip):
        return ip in self.whitelisted_ips

    def analyze_packet(self, packet):
        try:
            if not packet.haslayer(IP):
                return None

            src_ip = packet[IP].src
            dst_ip = packet[IP].dst

            if self.is_ip_whitelisted(src_ip) or self.is_ip_whitelisted(dst_ip):
                logging.info(f"IP {src_ip} ou {dst_ip} na whitelist, ignorado.")
                return None

            protocol = 'TCP' if packet.haslayer(TCP) else 'UDP' if packet.haslayer(UDP) else 'ICMP' if packet.haslayer(ICMP) else 'Unknown'
            packet_info = {
                'timestamp': datetime.now().isoformat(),
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'protocol': protocol,
                'length': len(packet),
                'ip_reputation': {
                    'src_ip_blacklisted': self.is_ip_blacklisted(src_ip),
                    'dst_ip_blacklisted': self.is_ip_blacklisted(dst_ip)
                }
            }

            if packet_info['ip_reputation']['src_ip_blacklisted'] or packet_info['ip_reputation']['dst_ip_blacklisted']:
                self.report_threat(packet_info)

            return packet_info
        except Exception as e:
            logging.error(f"Packet analysis error: {e}")
            return None

    def report_threat(self, packet_info):
        try:
            self.redis_client.rpush('network_threats', json.dumps(packet_info))
        except Exception as e:
            logging.error(f"Failed to report threat: {e}")

    def start_packet_capture(self, interface='eth0'):
        if interface not in get_if_list():
            raise ValueError(f"Interface {interface} not found!")
        logging.info(f"Starting capture on interface {interface}")
        try:
            scapy.sniff(prn=self.process_packet, store=0, iface=interface, promisc=True)
        except Exception as e:
            logging.critical(f"Capture error: {e}")

    def process_packet(self, packet):
        analyzed_packet = self.analyze_packet(packet)
        if analyzed_packet:
            try:
                self.redis_client.rpush('processed_packets', json.dumps(analyzed_packet))
            except Exception as e:
                logging.error(f"Redis storage failed: {e}")

        if time.time() - self.last_backup_time >= self.config['backup_interval']:
            self.create_backup()
            self.redis_client.delete("processed_packets")
            self.last_backup_time = time.time()

    def create_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"./logs/packet_capture_backup_{timestamp}.json"
            packets = self.redis_client.lrange('processed_packets', 0, -1)
            with open(backup_path, 'w') as f:
                for packet in packets:
                    f.write(packet + "\n")
            logging.info(f"Backup created at {backup_path}")
        except Exception as e:
            logging.error(f"Backup creation failed: {e}")

def main():
    analyzer = AdvancedNetworkPacketAnalyzer()
    analyzer.start_packet_capture('eth0')

if __name__ == "__main__":
    main()
