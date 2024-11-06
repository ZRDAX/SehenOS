import pandas as pd
import redis
import time
from threading import Thread
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

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

    df_original = df.copy()

    # Label Encoding para IPs, Hostnames e MACs
    for column in ['src_ip', 'dst_ip', 'src_hostname', 'dst_hostname', 'src_mac', 'dst_mac']:
        df[column] = df[column].astype('category').cat.codes

    df = df.fillna(0)
    return df, df_original

# Construindo o modelo de rede neural
def build_nn_model(input_shape):
    model = Sequential([
        Input(shape=(input_shape,)),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid'),
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Função para detectar anomalias
def detect_anomalies(X):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    y_pred = model.predict(X)
    anomalies_indices = [i for i, pred in enumerate(y_pred) if pred == -1]
    return anomalies_indices

# Função para criar um arquivo .txt das anomalias e limpar o buffer Redis
def create_anomaly_backup(redis_conn):
    while True:
        # Executa a cada 2 horas (7200 segundos)
        #time.sleep(2 * 60 * 60)
        time.sleep(6 * 60) # 6 minutos para teste
        anomalies = redis_conn.lrange("anomalies", 0, -1)
        with open("logs/anomaly_detection_backup.txt", "w") as file:
            file.write("\n".join(anomalies))
        # Limpar o buffer Redis após criar o arquivo .txt
        redis_conn.delete("anomalies")
        print("Backup das anomalias criado e buffer Redis limpo.")

# Função principal para executar o pipeline de ML continuamente
def main():
    # Conectar ao Redis
    redis_conn = connect_redis()
    if not redis_conn:
        print("Não foi possível conectar ao Redis.")
        return

    # Iniciar a thread para criação periódica de backup
    backup_thread = Thread(target=create_anomaly_backup, args=(redis_conn,))
    backup_thread.daemon = True  # Daemoniza a thread para encerrá-la quando o programa principal terminar
    backup_thread.start()

    while True:
        # Carregar dados do Redis
        data = redis_conn.lrange("network_packets", 0, -1)
        if not data:
            print("Nenhum dado encontrado no buffer Redis.")
            time.sleep(5)  # Esperar alguns segundos antes de verificar novamente
            continue

        # Criar DataFrame a partir dos dados do Redis
        df = pd.DataFrame([eval(item) for item in data], columns=[
            'src_ip', 'dst_ip', 'src_hostname', 'dst_hostname', 'src_mac', 'dst_mac'
        ])

        try:
            df_processed, df_original = preprocess_data(df)
            X = df_processed.values

            # Detecção de anomalias
            anomalies_indices = detect_anomalies(X)
            print(f"Anomalias detectadas: {len(anomalies_indices)}")

            # Salvar as anomalias no buffer Redis
            for idx in anomalies_indices:
                original_data = df_original.iloc[idx].to_dict()
                redis_conn.rpush("anomalies", str(original_data))

            # Treinamento da rede neural (não é essencial, mas incluído para manter o script completo)
            nn_model = build_nn_model(X.shape[1])
            y = (IsolationForest(contamination=0.1).fit(X).predict(X) == -1).astype(int)
            nn_model.fit(X, y, epochs=10, batch_size=32, verbose=0)

        except Exception as e:
            print(f"Erro durante o processamento: {e}")

        # Pausa breve antes de repetir a detecção
        time.sleep(5)

if __name__ == "__main__":
    main()
