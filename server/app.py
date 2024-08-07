from flask import Flask, jsonify, request
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

# Configurar a conexão com o PostgreSQL
DATABASE_URL = 'postgresql://sehenos:piswos@localhost:5432/swiredb'
engine = create_engine(DATABASE_URL)

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Endpoint para obter todos os logs de rede
@app.route('/api/logs', methods=['GET'])
def get_logs():
    query = "SELECT * FROM network_logs"
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient='records')

# Endpoint para obter um log específico por ID
@app.route('/api/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    query = f"SELECT * FROM network_logs WHERE id = {log_id}"
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    if df.empty:
        return jsonify({'error': 'Log not found'}), 404
    return df.to_json(orient='records')

# Endpoint para obter resultados de anomalias
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    query = "SELECT * FROM network_logs WHERE Intrusion != 'unknown'"
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
