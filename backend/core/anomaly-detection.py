import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        engine = create_engine('postgresql://cypher:piswos@localhost:5432/sehenos-db')
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Carregamento dos dados do banco de dados
def load_data(engine):
    query = "SELECT src_ip, dst_ip, src_hostname, dst_hostname, src_mac, dst_mac FROM network_traffic;"
    df = pd.read_sql_query(query, engine)
    return df

# Pré-processamento dos dados
def preprocess_data(df):
    if df.empty:
        raise ValueError("O DataFrame está vazio após o carregamento.")

    df_original = df.copy()

    # Label Encoding para IPs e Hostnames
    for column in ['src_ip', 'dst_ip', 'src_hostname', 'dst_hostname', 'src_mac', 'dst_mac']:       
        df[column] = df[column].astype('category').cat.codes

    # Normalização
    df = df.fillna(0)
    return df, df_original

# Divisão dos dados em conjuntos de treinamento e teste
def split_data(df):
    if len(df) > 1:
        X = df.values
        X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
        return X_train, X_test
    else:
        print("O conjunto de dados é muito pequeno para dividir em treinamento e teste.")
        return None, None

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

# Inserir anomalias no banco de dados
def insert_anomalies(engine, anomalies_indices, df_original):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        metadata = MetaData()
        metadata.reflect(bind=engine)
        anomalies_table = Table('anomalies', metadata, autoload_with=engine)

        # Inserir cada linha anômala no banco de dados
        for idx in anomalies_indices:
            original_data = df_original.iloc[idx]

            insert_stmt = anomalies_table.insert().values(
                src_ip=original_data['src_ip'],
                dst_ip=original_data['dst_ip'],
                src_hostname=original_data['src_hostname'],
                dst_hostname=original_data['dst_hostname'],
                src_mac=original_data['src_mac'],
                dst_mac=original_data['dst_mac']
            )
            session.execute(insert_stmt)

        session.commit()
        print(f"Anomalias inseridas: {len(anomalies_indices)}")
    except Exception as e:
        print(f"Erro ao inserir anomalias no banco de dados: {e}")
        session.rollback()
    finally:
        session.close()

# Função principal para executar o pipeline de ML
def main():
    engine = connect_db()
    if engine:
        df = load_data(engine)

        if df.empty:
            print("O DataFrame está vazio. Nenhum dado foi carregado.")
            return

        df_processed, df_original = preprocess_data(df)
        X_train, X_test = split_data(df_processed)

        if X_train is None or X_test is None:
            print("Não foi possível dividir os dados em conjuntos de treinamento e teste.")
            return

        # Treinamento e detecção de anomalias com Isolation Forest
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_train)
        y_pred = model.predict(X_test)

        # Análise de resultados
        anomalies_indices = [i for i, pred in enumerate(y_pred) if pred == -1]
        print(f"Anomalias detectadas: {len(anomalies_indices)}")

        # Inserir anomalias no banco de dados
        insert_anomalies(engine, anomalies_indices, df_original)
        
        # Treinamento da rede neural
        nn_model = build_nn_model(X_train.shape[1])
        y_train = (model.predict(X_train) == -1).astype(int).ravel()  # Criação de rótulos fictícios
        nn_model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

if __name__ == "__main__":
    main()
