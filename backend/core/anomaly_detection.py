import pandas as pd
import redis
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import time
import threading

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Pré-processamento dos dados
def preprocess_data(df):
    if df.empty:
        raise ValueError("O DataFrame está vazio após o carregamento.")

    label_encoders = {}
    for column in ['src_ip', 'dst_ip', 'src_mac', 'dst_mac', 'src_hostname', 'dst_hostname']:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column].astype(str))
        label_encoders[column] = le

    df = df.fillna(0)
    return df, label_encoders

# Função principal para executar o pipeline de ML
def detect_anomalies():

    # Treinamento e detecção de anomalias com Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    y_pred = model.predict(X_test)

    anomalies_indices = [i for i, pred in enumerate(y_pred) if pred == -1]
    print(f"Anomalias detectadas: {len(anomalies_indices)}")

    redis_conn = connect_redis()
    if redis_conn:
        for idx in anomalies_indices:
            redis_conn.rpush("anomalies", str(df.iloc[idx].to_dict()))

# Função para criar arquivos .txt a cada 5 horas
def create_backup_file():
    while True:
        time.sleep(5 * 60 * 60)  # 5 horas
        redis_conn = connect_redis()
        if redis_conn:
            anomalies = redis_conn.lrange("anomalies", 0, -1)
            with open("anomaly_detection_backup.txt", "w") as file:
                file.write("\n".join(anomalies))
            redis_conn.delete("anomalies")

# Executar detecção de anomalias em um thread separado
threading.Thread(target=detect_anomalies).start()
threading.Thread(target=create_backup_file).start()
