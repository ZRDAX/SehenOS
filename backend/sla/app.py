from flask import Flask, jsonify, send_file, Response, request
import redis
import psutil
import os
import time
import json
from datetime import datetime
import logging
from logging import StreamHandler, FileHandler

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler = FileHandler('logs/app.log')
app.logger.addHandler(file_handler)

REDIS_HOST = 'localhost'
REDIS_PORT = 6380

def connect_redis():
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        r.ping()
        return r
    except redis.ConnectionError as e:
        app.logger.error(f"Erro ao conectar ao Redis: {e}")
        return None

@app.route('/api/packets', methods=['GET'])
def get_packets():
    redis_conn = connect_redis()
    if not redis_conn:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

    packets = redis_conn.lrange("processed_packets", 0, -1)
    return jsonify({"packets": [json.loads(packet) for packet in packets]})

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    redis_conn = connect_redis()
    if not redis_conn:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

    anomalies = redis_conn.lrange("anomalies", 0, -1)
    return jsonify({"anomalies": [json.loads(anomaly) for anomaly in anomalies]})

@app.route('/api/packet_backup', methods=['GET'])
def get_packet_backup():
    try:
        files = [f for f in os.listdir('./logs') if f.startswith('packet_capture_backup')]
        latest_backup = max(files, key=os.path.getctime)
        return send_file(f'./logs/{latest_backup}', as_attachment=True)
    except Exception as e:
        app.logger.error(f"Erro ao enviar arquivo de backup: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/anomaly_backup', methods=['GET'])
def get_anomaly_backup():
    try:
        files = [f for f in os.listdir('./logs') if f.startswith('anomaly_backup')]
        latest_backup = max(files, key=os.path.getctime)
        return send_file(f'./logs/{latest_backup}', as_attachment=True)
    except Exception as e:
        app.logger.error(f"Erro ao enviar arquivo de backup: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/system_info', methods=['GET'])
def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory": {
            "total": memory.total,
            "used": memory.used,
            "free": memory.available
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
