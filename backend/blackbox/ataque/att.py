from scapy.all import IP, TCP, send

packet = IP(dst="192.168.1.115") / TCP(dport=80)
send(packet, count=10)
