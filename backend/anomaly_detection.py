import pandas as pd
import psycopg2
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos_db",
            user="sehenos",
            password="yourpassword",
            host="db"  # Nome do serviço no Docker Compose
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Carregamento dos dados do banco de dados
def load_data(conn):
    query = "SELECT src_ip, dst_ip, src_hostname, dst_hostname FROM network_traffic;"
    df = pd.read_sql_query(query, conn)
    return df

# Pré-processamento dos dados
def preprocess_data(df):
    # Label Encoding para IPs e Hostnames
    label_encoder = LabelEncoder()
    df['src_ip'] = label_encoder.fit_transform(df['src_ip'])
    df['dst_ip'] = label_encoder.fit_transform(df['dst_ip'])
    df['src_hostname'] = label_encoder.fit_transform(df['src_hostname'])
    df['dst_hostname'] = label_encoder.fit_transform(df['dst_hostname'])
    
    # Normalização
    df = df.fillna(0)
    return df

# Divisão dos dados em conjuntos de treinamento e teste
def split_data(df):
    X = df.values
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    return X_train, X_test

# Função principal para executar o pipeline de ML
def main():
    conn = connect_db()
    if conn:
        df = load_data(conn)
        conn.close()
        
        df_processed = preprocess_data(df)
        X_train, X_test = split_data(df_processed)
        
        # Treinamento e detecção de anomalias com Isolation Forest
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_train)
        y_pred = model.predict(X_test)
        
        # Análise com Rede Neural (opcional)
        nn_model = Sequential([
            Dense(64, input_dim=X_train.shape[1], activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        nn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        nn_model.fit(X_train, y_pred, epochs=10, batch_size=32, verbose=1)
        
        # Análise de resultados
        anomalies = X_test[y_pred == -1]
        print(f"Anomalias detectadas: {len(anomalies)}")

if __name__ == "__main__":
    main()
