import os
import json
from datetime import datetime
from app.config import Config
from config.redis_config import redis_client

def save_backup(data, backup_type):
    """
    Salva um backup no diretório apropriado.
    :param data: Dados a serem salvos.
    :param backup_type: Tipo do backup ('packets' ou 'anomalies').
    :return: Caminho do arquivo de backup salvo.
    """
    backup_file = f"{Config.BACKUP_DIR}/{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)  # Garantir que o diretório existe
    with open(backup_file, "w") as f:
        json.dump(data, f)
    return backup_file

def get_data_from_redis(redis_key):
    """
    Recupera dados do Redis por uma chave específica.
    :param redis_key: Chave no Redis ('network_packets' ou 'network_anomalies').
    :return: Lista de dados do Redis.
    """
    data = redis_client.lrange(redis_key, 0, -1)
    return [json.loads(item) for item in data] if data else []

def save_packet_backup():
    """
    Salva manualmente um backup de pacotes capturados.
    :return: Caminho do arquivo de backup salvo.
    """
    packets = get_data_from_redis("network_packets")
    if not packets:
        raise ValueError("Nenhum pacote encontrado para backup.")
    return save_backup(packets, "packets")

def save_anomaly_backup():
    """
    Salva manualmente um backup de anomalias detectadas.
    :return: Caminho do arquivo de backup salvo.
    """
    anomalies = get_data_from_redis("network_anomalies")
    if not anomalies:
        raise ValueError("Nenhuma anomalia encontrada para backup.")
    return save_backup(anomalies, "anomalies")
