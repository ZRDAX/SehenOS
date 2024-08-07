from sqlalchemy import create_engine

DATABASE_URL = 'postgresql://sehenos:piswos@localhost:5432/swiredb'

engine = create_engine(DATABASE_URL)

# Teste de conexão
try:
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("Conexão bem-sucedida:", result.fetchone())
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)
