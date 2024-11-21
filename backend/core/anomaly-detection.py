import redis
import json
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime
from models.anomaly_models import load_models
from models.preprocessing import preprocess_data
from app.config import Config
from config.redis_config import redis_client
import logging
import os

logging.basicConfig(level=logging.INFO)

# Buscar pacotes do Redis
def fetch_packets():
    packets = redis_client.lrange("network_packets", 0, -1)
    redis_client.delete("network_packets")
    return [json.loads(packet) for packet in packets]

# Detectar anomalias
def detect_anomalies(models, data):
    isolation_forest, autoencoder, pca = models

    isolation_preds = isolation_forest.predict(data)  # -1 indica anomalia
    reconstruction = autoencoder.predict(data)
    reconstruction_error = ((data - reconstruction) ** 2).mean(axis=1)

    reconstruction_anomalies = reconstruction_error > 0.05  # Limiar
    isolation_anomalies = isolation_preds == -1

    combined_anomalies = isolation_anomalies | reconstruction_anomalies
    return isolation_preds, reconstruction_error, combined_anomalies

# Salvar anomalias detectadas no Redis
def save_anomalies(df, isolation_preds, reconstruction_error):
    df["isolation_anomaly"] = isolation_preds == -1
    df["reconstruction_error"] = reconstruction_error
    df["reconstruction_anomaly"] = reconstruction_error > 0.05
    anomalies = df[(df["isolation_anomaly"]) | (df["reconstruction_anomaly"])]

    for anomaly in anomalies.to_dict(orient="records"):
        if "timestamp" in anomaly:
            anomaly["timestamp"] = str(anomaly["timestamp"])
        try:
            redis_client.rpush("network_anomalies", json.dumps(anomaly))
        except Exception as e:
            logging.error(f"Erro ao salvar anomalia no Redis: {e}")
            logging.debug(f"Anomalia: {anomaly}")

    logging.info(f"{len(anomalies)} anomalias detectadas e salvas no Redis.")

# Gerenciamento de backup de anomalias
def save_backup():
    backup_dir = Config.BACKUP_DIR
    os.makedirs(backup_dir, exist_ok=True)

    anomalies = redis_client.lrange("network_anomalies", 0, -1)
    redis_client.delete("network_anomalies")

    backup_file = os.path.join(backup_dir, f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(backup_file, "w") as f:
        json.dump([json.loads(anomaly) for anomaly in anomalies], f)
    logging.info(f"Backup salvo em: {backup_file}")

# Processar pacotes continuamente
def process_packets(models):
    while True:
        packets = fetch_packets()
        if packets:
            logging.info(f"Processando {len(packets)} pacotes...")
            df, scaled_data = preprocess_data(packets)

            isolation_preds, reconstruction_error, combined_anomalies = detect_anomalies(models, scaled_data)
            save_anomalies(df, isolation_preds, reconstruction_error)
        else:
            logging.info("Nenhum pacote para processar.")
        time.sleep(5)

if __name__ == "__main__":
    logging.info("Carregando modelos...")
    models = load_models()

    if models[0] is None:
        logging.error("Erro ao carregar modelos. Verifique se foram treinados e salvos corretamente.")
    else:
        try:
            # Teste inicial dos modelos
            sample_data = np.random.rand(10, 7)
            detect_anomalies(models, sample_data)
            logging.info("Modelos testados com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao testar os modelos: {e}")

        # Iniciar threads
        threading.Thread(target=save_backup, daemon=True).start()
        threading.Thread(target=process_packets, args=(models,), daemon=True).start()

        # Manter o programa ativo
        while True:
            time.sleep(1)
