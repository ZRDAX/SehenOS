from flask import Flask, jsonify, send_file
import redis

app = Flask(__name__)

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Endpoint para baixar o arquivo .txt do packet_capture
@app.route('/api/packet_backup', methods=['GET'])
def get_packet_backup():
    try:
        return send_file("packet_capture_backup.txt", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para baixar o arquivo .txt do anomaly_detection
@app.route('/api/anomaly_backup', methods=['GET'])
def get_anomaly_backup():
    try:
        return send_file("anomaly_detection_backup.txt", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para listar as anomalias do Redis
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    redis_conn = connect_redis()
    if redis_conn:
        anomalies = redis_conn.lrange("anomalies", 0, -1)
        return jsonify([eval(anomaly) for anomaly in anomalies])
    else:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

# Endpoint para listar os pacotes do Redis
@app.route('/api/packets', methods=['GET'])
def get_packets():
    redis_conn = connect_redis()
    if redis_conn:
        packets = redis_conn.lrange("network_packets", 0, -1)
        return jsonify([eval(packet) for packet in packets])
    else:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
