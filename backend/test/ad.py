import json
from config.redis_config import redis_client
from models.anomaly_models import load_models
from models.preprocessing import preprocess_data

def test_anomaly_detection():
    # Limpar banco antes do teste
    redis_client.delete("network_packets")
    redis_client.delete("network_anomalies")

    # Simular pacotes normais e anômalos
    packets = [
        {"length": 128, "src_port": 12345, "dst_port": 53, "bytes": 128},  # Normal
        {"length": 512, "src_port": 80, "dst_port": 443, "bytes": 2048}   # Anômalo
    ]

    # Salvar pacotes no Redis
    for packet in packets:
        redis_client.rpush("network_packets", json.dumps(packet))

    # Carregar modelos e processar pacotes
    models = load_models()
    packets_from_redis = redis_client.lrange("network_packets", 0, -1)
    packets_json = [json.loads(p) for p in packets_from_redis]
    df, scaled_data = preprocess_data(packets_json)

    # Detectar anomalias
    isolation_preds, reconstruction_error = detect_anomalies(models, scaled_data)

    # Salvar no Redis
    anomalies = [df.iloc[i].to_dict() for i in range(len(isolation_preds)) if isolation_preds[i] == -1]
    for anomaly in anomalies:
        redis_client.rpush("network_anomalies", json.dumps(anomaly))

    # Verificar se as anomalias foram salvas corretamente
    detected_anomalies = redis_client.lrange("network_anomalies", 0, -1)
    assert len(detected_anomalies) > 0
    print("Teste de detecção de anomalias: OK")

# Rodar o teste
test_anomaly_detection()
