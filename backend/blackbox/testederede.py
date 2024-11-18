import redis
import json
from datetime import datetime 
import logging

r = redis.StrictRedis(host='localhost', port=6380, decode_responses=True)

for i in range(100):
    packet = {
        "src_ip": f"192.168.1.{i}",
        "dst_ip": "8.8.8.8",
        "protocol": "TCP",
        'timestamp': datetime.now().isoformat()
    }
    r.rpush("network_packets", json.dumps(packet))
print("Dados simulados adicionados ao Redis.")
