import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder

# Conectar ao PostgreSQL
DATABASE_URL = 'postgresql://sehenos:piswos@localhost:5432/swiredb'
engine = create_engine(DATABASE_URL)

# Extrair os dados do banco de dados
def load_data():
    query = "SELECT * FROM network_logs"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# Pré-processar os dados
def preprocess_data(df):
    df = df.fillna('unknown')
    
    le_mac_src = LabelEncoder()
    df['MAC_src'] = le_mac_src.fit_transform(df['MAC_src'])
    
    le_mac_dst = LabelEncoder()
    df['MAC_dst'] = le_mac_dst.fit_transform(df['MAC_dst'])
    
    le_ip_src = LabelEncoder()
    df['IP_src'] = le_ip_src.fit_transform(df['IP_src'])
    
    le_ip_dst = LabelEncoder()
    df['IP_dst'] = le_ip_dst.fit_transform(df['IP_dst'])
    
    le_fqdn = LabelEncoder()
    df['FQDN'] = le_fqdn.fit_transform(df['FQDN'])
    
    return df

# Carregar e pré-processar os dados
df = load_data()
df_preprocessed = preprocess_data(df)
print(df_preprocessed.head())

# Salvar o DataFrame pré-processado em um arquivo CSV para uso posterior
df_preprocessed.to_csv('preprocessed_data.csv', index=False)
