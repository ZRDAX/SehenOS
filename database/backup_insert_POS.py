import psycopg2

# Conexão com o PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos-db",
            user="cypher",
            password="piswos",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para enviar os dados do .txt para o banco de dados
def send_to_postgres(filename, table):
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            with open(filename, "r") as file:
                for line in file:
                    data = eval(line.strip())  # Transformar string em dict
                    cur.execute(
                        f"INSERT INTO {table} (src_ip, dst_ip) VALUES (%s, %s);",
                        (data["src_ip"], data["dst_ip"])
                    )
            conn.commit()
        except Exception as e:
            print(f"Erro ao inserir dados no banco de dados: {e}")
        finally:
            cur.close()
            conn.close()

if __name__ == "__main__":
    send_to_postgres("packet_capture_backup.txt", "network_traffic")
    send_to_postgres("anomaly_detection_backup.txt", "anomalies")
