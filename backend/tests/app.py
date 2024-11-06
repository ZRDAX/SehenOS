#backend/app.py
import os
from flask import Flask, request, jsonify
import psycopg2
import subprocess
import redis
import json

app = Flask(__name__)

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos-db",
            user="cypher",
            password="piswos",
            host="localhost",  # Nome do serviço no Docker Compose
            port="5432"  # porta do postgresql
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    
# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None
    
# Endpoint para listar pacotes do Redis
@app.route('/api/redis_packets', methods=['GET'])
def get_redis_packets():
    r = connect_redis()
    if r:
        keys = r.keys("packet:*")
        packets = []
        for key in keys:
            packet = r.get(key)
            if packet:
                packets.append(json.loads(packet))
        return jsonify(packets)
    else:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

# Endpoint para listar os pacotes capturados
@app.route('/api/packets', methods=['GET'])
def get_packets():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM network_traffic;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Formatando os resultados para JSON
        packets = [
            {"id": row[0], "timestamp": row[1], "src_ip": row[2], "src_hostname": row[3],
            "dst_ip": row[4], "dst_hostname": row[5]}
            for row in rows
        ]
        return jsonify(packets)
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

# Endpoint para listar as anomalias detectadas
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM anomalies;")
            rows = cur.fetchall()
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return jsonify({"error": "Erro ao executar a query"}), 500
        finally:
            cur.close()
            conn.close()

        # Corrigido para usar a lista 'rows'
        anomalies = [
            {"id": row[0], "timestamp": row[1], "src_ip": row[2], "src_hostname": row[3],
            "src_mac": row[4], "dst_ip": row[5], "dst_hostname": row[6], "dst_mac": row[7]}
            for row in rows
        ]
        return jsonify(anomalies)
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
