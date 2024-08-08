import logging
import time
from scapy.all import sniff, IP, Ether, TCP, ICMP, DNS, DNSQR
from threading import Thread

# Configurar o logging
logging.basicConfig(filename='../logs/LogsGET.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

packet_log = [] 

def is_intrusion(packet):
    # Exemplo: detectar escaneamento de portas
    if packet.haslayer(TCP) and packet[TCP].flags == "S":
        return True, "Port scan detected"
    # Exemplo: detectar alto volume de pacotes ICMP (DDoS simples)
    if packet.haslayer(ICMP):
        return True, "Possible ICMP flood attack"
    return False, None

def packet_handler(packet):
    log_entry = []

    # Verificar se o pacote tem uma camada Ethernet
    if Ether in packet:
        ether_layer = packet[Ether]
        mac_src = ether_layer.src
        mac_dst = ether_layer.dst
        log_entry.append(f"MACo: {mac_src}, MACd: {mac_dst}")

    # Verificar se o pacote tem uma camada IP
    if IP in packet:
        ip_layer = packet[IP]
        ip_src = ip_layer.src
        ip_dst = ip_layer.dst
        log_entry.append(f"IPo: {ip_src}, IPd: {ip_dst}")

    # Verificar se o pacote tem uma camada DNS
    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
        dns_layer = packet[DNSQR]
        fqdn = dns_layer.qname.decode('utf-8')
        log_entry.append(f"FQDN: {fqdn}")

    # Verificar se o pacote indica uma intrusão
    is_intrusion_flag, intrusion_type = is_intrusion(packet)
    if is_intrusion_flag:
        log_entry.append(f"Intrusion: {intrusion_type}")

    if log_entry:
        logging.info(", ".join(log_entry))
        packet_log.append(", ".join(log_entry))

def print_logs_periodically():
    while True:
        if packet_log:
            for entry in packet_log:
                print(entry)
            packet_log.clear()
        time.sleep(5)

# Iniciar a captura de pacotes em um thread separado
sniff_thread = Thread(target=lambda: sniff(prn=packet_handler, store=0, iface='eth0', promisc=True))
sniff_thread.start()

# Iniciar o loop de impressão periódica
print_logs_periodically()
