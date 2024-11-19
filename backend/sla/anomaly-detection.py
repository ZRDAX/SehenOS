import os
import numpy as np
import pandas as pd
import redis
import time
import logging
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from joblib import dump, load
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'./logs/anomaly_detection.log'
)

class NetworkAnomalyDetector:
    def __init__(self, redis_host='localhost', redis_port=6380):
        self.redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.autoencoder = self.create_autoencoder(16)  # Número de features esperado
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        self.isolation_forest = IsolationForest(contamination=0.01)
        self.anomaly_threshold = None
        self.last_backup_time = time.time()
        self.backup_interval = 7200  # 2 horas

    def create_autoencoder(self, input_dim):
        input_layer = Input(shape=(input_dim,))
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = BatchNormalization()(encoded)
        encoded = Dropout(0.2)(encoded)
        bottleneck = Dense(16, activation='relu')(encoded)
        decoded = Dense(128, activation='relu')(bottleneck)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)
        autoencoder = Model(inputs=input_layer, outputs=decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        return autoencoder

    def process_data_batch(self, data_batch):
        features_list = [json.loads(packet) for packet in data_batch]
        features_df = pd.DataFrame(features_list)
        features_scaled = self.scaler.fit_transform(features_df)
        features_pca = self.pca.fit_transform(features_scaled)

        predictions = self.autoencoder.predict(features_pca)
        mse = np.mean(np.power(features_pca - predictions, 2), axis=1)

        if self.anomaly_threshold is None:
            self.anomaly_threshold = np.percentile(mse, 95)

        autoencoder_anomalies = mse > self.anomaly_threshold
        isolation_anomalies = self.isolation_forest.fit_predict(features_scaled) == -1

        anomalies = features_df[autoencoder_anomalies | isolation_anomalies]
        self.store_anomalies(anomalies)

        if time.time() - self.last_backup_time >= self.backup_interval:
            self.create_backup(anomalies)
            self.redis_conn.delete("network_packets")
            self.last_backup_time = time.time()

    def store_anomalies(self, anomalies):
        for _, anomaly in anomalies.iterrows():
            self.redis_conn.rpush("anomalies", anomaly.to_json())

    def create_backup(self, anomalies):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"./logs/anomaly_backup_{timestamp}.json"
        anomalies.to_json(backup_path, orient="records", lines=True)
        logging.info(f"Backup de anomalias criado: {backup_path}")

    def run_detection(self):
        while True:
            packets = self.redis_conn.lrange("network_packets", 0, -1)
            if packets:
                self.process_data_batch(packets)
            time.sleep(60)

if __name__ == "__main__":
    detector = NetworkAnomalyDetector()
    detector.run_detection()
