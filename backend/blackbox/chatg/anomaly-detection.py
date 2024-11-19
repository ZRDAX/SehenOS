import os
import numpy as np
import pandas as pd
import redis
import time
import logging
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
from joblib import dump, load
import json
from collections import defaultdict
from sklearn.ensemble import IsolationForest  # Algoritmo de detecção de anomalias

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'./logs/anomaly_detection.log'
)

class NetworkAnomalyDetector:
    def __init__(self, redis_host='localhost', redis_port=6380):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_conn = None

        # Caminhos para modelos e scalers
        self.base_path = "./models/"
        self.model_path = os.path.join(self.base_path, 'autoencoder_model.h5')
        self.scaler_path = os.path.join(self.base_path, 'scaler.joblib')
        self.pca_path = os.path.join(self.base_path, 'pca.joblib')

        # Parâmetros do modelo
        self.threshold_percentile = 95
        self.anomaly_threshold = None
        self.training_window = 1000  # Número de amostras para treinar/atualizar o modelo

        # Estatísticas de baseline
        self.baseline_stats = defaultdict(lambda: {
            'mean': None,
            'std': None,
            'min': None,
            'max': None
        })

        # Inicialização
        self.initialize_components()

    def connect_redis(self):
        """Estabelece conexão com Redis com retry automático"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.redis_conn = redis.StrictRedis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=0,
                    decode_responses=True
                )
                self.redis_conn.ping()
                logging.info("Conexão com Redis estabelecida com sucesso")
                return True
            except redis.exceptions.ConnectionError as e:
                retry_count += 1
                logging.error(f"Tentativa {retry_count} de conexão com Redis falhou: {e}")
                time.sleep(2)

        logging.critical("Falha ao conectar ao Redis após todas as tentativas")
        return False

    def create_autoencoder(self, input_dim):
        """Cria um modelo autoencoder mais robusto com regularização"""
        input_layer = Input(shape=(input_dim,))

        # Encoder
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = BatchNormalization()(encoded)
        encoded = Dropout(0.2)(encoded)

        encoded = Dense(64, activation='relu')(encoded)
        encoded = BatchNormalization()(encoded)
        encoded = Dropout(0.2)(encoded)

        encoded = Dense(32, activation='relu')(encoded)
        encoded = BatchNormalization()(encoded)

        # Bottleneck
        bottleneck = Dense(16, activation='relu')(encoded)

        # Decoder
        decoded = Dense(32, activation='relu')(bottleneck)
        decoded = BatchNormalization()(decoded)

        decoded = Dense(64, activation='relu')(decoded)
        decoded = BatchNormalization()(decoded)
        decoded = Dropout(0.2)(decoded)

        decoded = Dense(128, activation='relu')(decoded)
        decoded = BatchNormalization()(decoded)
        decoded = Dropout(0.2)(decoded)

        output_layer = Dense(input_dim, activation='sigmoid')(decoded)

        autoencoder = Model(inputs=input_layer, outputs=output_layer)
        autoencoder.compile(optimizer='adam', loss='mse')

        return autoencoder

    def initialize_components(self):
        """Inicializa ou carrega componentes do modelo"""
        try:
            os.makedirs(self.base_path, exist_ok=True)

            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.load_model()
            else:
                self.autoencoder = None
                self.scaler = StandardScaler()
                self.pca = PCA(n_components=0.95)  # Mantém 95% da variância

            logging.info("Componentes inicializados com sucesso")

        except Exception as e:
            logging.error(f"Erro na inicialização dos componentes: {e}")
            raise

    def load_model(self):
        """Carrega modelo e componentes salvos"""
        try:
            self.autoencoder = load_model(self.model_path)
            self.scaler = load(self.scaler_path)
            self.pca = load(self.pca_path)
            logging.info("Modelo e componentes carregados com sucesso")
        except Exception as e:
            logging.error(f"Erro ao carregar modelo: {e}")
            self.autoencoder = None
            self.scaler = StandardScaler()
            self.pca = PCA(n_components=0.95)

    def save_model(self):
        """Salva modelo e componentes"""
        try:
            self.autoencoder.save(self.model_path)
            dump(self.scaler, self.scaler_path)
            dump(self.pca, self.pca_path)
            logging.info("Modelo e componentes salvos com sucesso")
        except Exception as e:
            logging.error(f"Erro ao salvar modelo: {e}")

    def extract_features(self, packet_data):
        """Extrai características relevantes dos pacotes"""
        features = {
            'bytes': float(packet_data.get('length', 0)),
            'ttl': float(packet_data.get('ttl', 0)),
            'protocol': float(packet_data.get('protocol', 0)),
            'src_port': float(packet_data.get('src_port', 0)),
            'dst_port': float(packet_data.get('dst_port', 0)),
            'packets_count': float(packet_data['connection_stats'].get('packet_count', 0)),
            'bytes_transferred': float(packet_data['connection_stats'].get('bytes_transferred', 0)),
            'unique_ports': float(len(packet_data['connection_stats'].get('ports_used', [])))
        }

        # Características derivadas
        features.update({
            'bytes_per_packet': features['bytes_transferred'] / max(1, features['packets_count']),
            'is_http': 1.0 if packet_data.get('protocol') == 'HTTP' else 0.0,
            'is_https': 1.0 if packet_data.get('protocol') == 'HTTPS' else 0.0,
            'is_dns': 1.0 if packet_data.get('protocol') == 'DNS' else 0.0,
            'is_known_service': 1.0 if packet_data.get('src_service', 'unknown') != 'unknown' or 
                                    packet_data.get('dst_service', 'unknown') != 'unknown' else 0.0
        })

        return features

    def update_baseline_stats(self, features_df):
        """Atualiza estatísticas de baseline para detecção de anomalias"""
        for column in features_df.columns:
            self.baseline_stats[column][' mean'] = features_df[column].mean()
            self.baseline_stats[column]['std'] = features_df[column].std()
            self.baseline_stats[column]['min'] = features_df[column].min()
            self.baseline_stats[column]['max'] = features_df[column].max()

    def detect_statistical_anomalies(self, features_df):
        """Detecta anomalias usando métodos estatísticos"""
        anomalies = []

        for idx, row in features_df.iterrows():
            anomaly_scores = {}

            for column in features_df.columns:
                if self.baseline_stats[column]['std'] > 0:
                    z_score = abs((row[column] - self.baseline_stats[column]['mean']) / 
                                self.baseline_stats[column]['std'])
                    anomaly_scores[column] = float(z_score)

            if any(score > 3 for score in anomaly_scores.values()):  # 3 desvios padrão
                anomalies.append({
                    'timestamp': idx,
                    'type': 'statistical',
                    'scores': anomaly_scores
                })

        return anomalies

    def process_data_batch(self, data_batch):
        """Processa um lote de dados para detecção de anomalias"""
        try:
            # Extrai características
            features_list = []
            timestamps = []

            for packet_data in data_batch:
                packet_dict = json.loads(packet_data)
                features = self.extract_features(packet_dict)
                features_list.append(features)
                timestamps.append(packet_dict['timestamp'])

            if not features_list:
                return []

            # Cria DataFrame
            features_df = pd.DataFrame(features_list, index=timestamps)

            # Atualiza estatísticas de baseline
            self.update_baseline_stats(features_df)

            # Normalização
            features_scaled = self.scaler.fit_transform(features_df)

            # Redução de dimensionalidade
            features_pca = self.pca.fit_transform(features_scaled)

            # Treina ou atualiza modelo se necessário
            if self.autoencoder is None:
                self.autoencoder = self.create_autoencoder(features_pca.shape[1])

                # Treina com early stopping
                early_stopping = EarlyStopping(monitor='val_loss', patience=5)
                self.autoencoder.fit(
                    features_pca, features_pca,
                    epochs=100,
                    batch_size=32,
                    validation_split=0.2,
                    callbacks=[early_stopping],
                    verbose=0
                )

                self.save_model()

            # Detecta anomalias
            predictions = self.autoencoder.predict(features_pca)
            mse = np.mean(np.power(features_pca - predictions, 2), axis=1)

            # Atualiza threshold se necessário
            if self.anomaly_threshold is None:
                self.anomaly_threshold = np.percentile(mse, self.threshold_percentile)

            # Combina diferentes métodos de detecção
            autoencoder_anomalies = [
                {
                    'timestamp': timestamp,
                    'type': 'autoencoder',
                    'score': float(score),
                    'threshold': float(self.anomaly_threshold)
                }
                for timestamp, score in zip(timestamps, mse)
                if score > self.anomaly_threshold
            ]

            statistical_anomalies = self.detect_statistical_anomalies(features_df)

            # Combina resultados
            all_anomalies = autoencoder_anomalies + statistical_anomalies

            # Adiciona contexto às anomalias
            for anomaly in all_anomalies:
                idx = timestamps.index(anomaly['timestamp'])
                anomaly['features'] = features_list[idx]

            return all_anomalies

        except Exception as e:
            logging.error(f"Erro no processamento do lote: {e}")
            return []

    def store_anomalies(self, anomalies):
        """Armazena anomalias detectadas no Redis"""
        try:
            if not self.redis_conn:
                if not self.connect_redis():
                    return

            for anomaly in anomalies:
                anomaly_json = json.dumps(anomaly)
                self.redis_conn.rpush("anomalies", anomaly_json)

            # Mantém apenas as últimas 1000 anomalias
            self.redis_conn.ltrim("anomalies", -1000, -1)

        except redis.exceptions.RedisError as e:
            logging.error(f"Erro ao armazenar anomalias no Redis: {e}")

    def create_anomaly_backup(self, anomalies):
        """Cria backup das anomalias detectadas"""
        if anomalies:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"./logs/anomainfo_{timestamp}.txt"

                with open(backup_path, "w") as file:
                    for anomaly in anomalies:
                        file.write(json.dumps(anomaly) + "\n")

                logging.info(f" Backup de anomalias criado: {backup_path}")

            except Exception as e:
                logging.error(f"Erro ao criar backup de anomalias: {e}")

    def run_detection(self):
        """Loop principal de detecção de anomalias"""
        if not self.connect_redis():
            return

        logging.info("Iniciando detecção de anomalias")

        while True:
            try:
                # Obtém pacotes do Redis
                packets = self.redis_conn.lrange("network_packets", 0, -1)

                if packets:
                    # Processa pacotes e detecta anomalias
                    anomalies = self.process_data_batch(packets)

                    if anomalies:
                        # Armazena e faz backup das anomalias
                        self.store_anomalies(anomalies)
                        self.create_anomaly_backup(anomalies)

                        logging.info(f"Detectadas {len(anomalies)} anomalias")

                    # Limpa pacotes processados
                    self.redis_conn.delete("network_packets")

                # Aguarda próximo ciclo
                time.sleep(60)  # Ajuste conforme necessidade

            except Exception as e:
                logging.error(f"Erro no ciclo de detecção: {e}")
                time.sleep(60)  # Aguarda antes de tentar novamente

if __name__ == "__main__":
    detector = NetworkAnomalyDetector()
    detector.run_detection()