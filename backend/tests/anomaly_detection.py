import os
import json
import redis
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import schedule
import time

# Conexão com o Redis
def connect_redis():
    try:
        redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
        return redis_client
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Conexão com o banco de dados PostgreSQL usando SQLAlchemy
def connect_db():
    try:
        engine = create_engine('postgresql://cypher:piswos@db:5432/sehenos-db')
        print('Conexão estabelecida com sucesso.')
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para processar pacotes do Redis e inserir no PostgreSQL
def process_redis_to_postgresql(redis_client, engine):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        metadata = MetaData()
        network_traffic = Table('network_traffic', metadata, autoload_with=engine)

        # Recuperar todos os pacotes armazenados no Redis
        while redis_client.llen('network_packets') > 0:
            packet_data = redis_client.rpop('network_packets')
            packet_data = json.loads(packet_data)  # Converter de string JSON para dict

            insert_stmt = network_traffic.insert().values(
                src_ip=packet_data['src_ip'],
                src_hostname=packet_data['src_hostname'],
                dst_ip=packet_data['dst_ip'],
                dst_hostname=packet_data['dst_hostname']
            )
            session.execute(insert_stmt)

        session.commit()
        print("Pacotes inseridos no PostgreSQL.")
    except Exception as e:
        print(f"Erro ao processar pacotes do Redis para PostgreSQL: {e}")
        session.rollback()
    finally:
        session.close()

# Função para rodar periodicamente e processar pacotes do Redis para o PostgreSQL
def job():
    redis_client = connect_redis()
    engine = connect_db()
    if redis_client and engine:
        process_redis_to_postgresql(redis_client, engine)

# Agendar o processamento de pacotes a cada 30 segundos
schedule.every(30).seconds.do(job)

def start_processing():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_processing()
