import psycopg2

# Estabelecendo a conexão
conn = psycopg2.connect(
    dbname="sehenos-db",
    user="cypher",
    password="piswos",
    host="db",  # Nome do serviço no Docker Compose
    port="5432"
)

# Criando um cursor
cur = conn.cursor()

# Executando uma consulta SQL
cur.execute("SELECT * FROM network_traffic;")

# Obtendo os resultados
rows = cur.fetchall()

# Iterando sobre os resultados
for row in rows:
    print(row)
    
# Fechando o cursor e a conexão
cur.close()
conn.close()