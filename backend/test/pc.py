import json
from config.redis_config import redis_client

def test_packet_capture():
    # Limpar banco antes do teste
    redis_client.delete("network_packets")

    # Capturar um pacote simulado (ou real, dependendo do ambiente)
    sample_packet = {
        "timestamp": "2024-11-19T12:34:56.789",
        "src_ip": "192.168.0.1",
        "dst_ip": "8.8.8.8",
        "protocol": 6,
        "length": 128,
        "mac_src": "00:11:22:33:44:55",
        "mac_dst": "66:77:88:99:AA:BB",
        "src_port": 12345,
        "dst_port": 53,
        "tcp_flags": "S",
        "dns_queries": "meuCC.com",
        "payload": "48656c6c6f20776f726c64",
        "blacklist_flag": False,
        "whitelist_flag": True,
        "bytes": 128
    }

    # Inserir no Redis manualmente para teste
    redis_client.rpush("network_packets", json.dumps(sample_packet))

    # Verificar se foi salvo corretamente
    packets = redis_client.lrange("network_packets", 0, -1)
    assert len(packets) == 1
    assert json.loads(packets[0])["src_ip"] == "192.168.0.1"

    print("Teste de captura de pacotes: OK")

# Rodar o teste
test_packet_capture()
