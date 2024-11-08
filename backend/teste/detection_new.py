import os
import numpy as np
import pandas as pd
import redis
import time
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense
from joblib import dump, load

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Carregar ou criar o modelo Autoencoder
def create_autoencoder(input_dim):
    input_layer = Input(shape=(input_dim,))
    encoder = Dense(14, activation="relu")(input_layer)
    encoder = Dense(7, activation="relu")(encoder)
    decoder = Dense(14, activation="relu")(encoder)
    decoder = Dense(input_dim, activation="sigmoid")(decoder)
    autoencoder = Model(inputs=input_layer, outputs=decoder)
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder

# Função principal de detecção de anomalias
def detect_anomalies():
    r = connect_redis()
    if not r:
        print("Falha na conexão com o Redis. Finalizando.")
        return

    # Parâmetros do modelo e do scaler
    autoencoder_model_path = 'autoencoder_model.h5'
    scaler_path = 'scaler.gz'

    # Inicialização do modelo e scaler
    if os.path.exists(autoencoder_model_path) and os.path.exists(scaler_path):
        print("Carregando modelo e scaler existentes.")
        autoencoder = load_model(autoencoder_model_path)
        scaler = load(scaler_path)
    else:
        print("Inicializando novo modelo e scaler.")
        autoencoder = None
        scaler = MinMaxScaler()

    # Intervalo para criação de arquivo de backup
    txt_interval = 360  # 6 min para teste
    last_txt_save = time.time()

    while True:
        # Carregar dados do Redis a partir de uma lista
        data = []
        list_key = "network_packets"  # Nome da chave de lista

        try:
            list_length = r.llen(list_key)  # Verificar quantos itens estão na lista
            if list_length > 0:
                packet_list = r.lrange(list_key, 0, -1)  # Pegar todos os pacotes da lista

                for packet_str in packet_list:
                    packet = eval(packet_str)  # Converte string de volta para dict
                    data.append([
                        packet.get("src_ip"),
                        packet.get("dst_ip"),
                        packet.get("src_mac"),
                        packet.get("dst_mac")
                    ])
            else:
                print("Lista 'network_packets' está vazia.")

        except Exception as e:
            print(f"Erro ao acessar a lista '{list_key}': {e}")
            continue

        if not data:
            print("Nenhum dado no Redis para analisar.")
            time.sleep(60)
            continue

        # Pré-processamento dos dados
        df = pd.DataFrame(data, columns=["src_ip", "dst_ip", "src_mac", "dst_mac"])
        df = pd.get_dummies(df, columns=["src_ip", "dst_ip", "src_mac", "dst_mac"])

        # Ajuste de scaler e treino do autoencoder
        if not autoencoder:
            print("Treinando novo modelo de Autoencoder.")
            data_scaled = scaler.fit_transform(df)
            autoencoder = create_autoencoder(data_scaled.shape[1])
            autoencoder.fit(data_scaled, data_scaled, epochs=50, batch_size=32, shuffle=True)
            autoencoder.save(autoencoder_model_path)
            dump(scaler, scaler_path)
        else:
            data_scaled = scaler.transform(df)

        # Previsão e detecção de anomalias
        predictions = autoencoder.predict(data_scaled)
        mse = np.mean(np.power(data_scaled - predictions, 2), axis=1)
        threshold = 0.01  # Ajuste com base na sua aplicação
        anomalies = df[mse > threshold]

        # Exibir anomalias detectadas
        if not anomalies.empty:
            print(f"Anomalias detectadas: {len(anomalies)}")
            print(anomalies)

        # Criar backup em .txt a cada intervalo
        current_time = time.time()
        if current_time - last_txt_save >= txt_interval:
            txt_filename = f"anomalies_backup_{int(current_time)}.txt"
            anomalies.to_csv(txt_filename, index=False)
            last_txt_save = current_time
            print(f"Backup das anomalias salvo em {txt_filename}")
            # Limpeza do buffer Redis após backup
            r.delete(list_key)
            print("Buffer Redis limpo.")
            
        # Pausa entre execuções para não sobrecarregar
        time.sleep(300)

if __name__ == "__main__":
    detect_anomalies()
