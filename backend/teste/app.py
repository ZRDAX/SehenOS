from flask import Flask, jsonify, send_file, Response, request
import redis
import psutil
import subprocess
import os
import time
import json  # Import necessário para formatação JSON em get_system_info

app = Flask(__name__)

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(host='localhost', port=6380, db=0, decode_responses=True)
        return r
    except Exception as e:
        print(f"Erro ao conectar ao Redis: {e}")
        return None

# Função para obter a temperatura da CPU no Linux
def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            temp = int(temp_file.read()) / 1000  # Conversão para Celsius
        return temp
    except FileNotFoundError:
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
        return jsonify([json.loads(anomaly) for anomaly in anomalies])
    else:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

# Endpoint para listar os pacotes do Redis
@app.route('/api/packets', methods=['GET'])
def get_packets():
    redis_conn = connect_redis()
    if redis_conn:
        packets = redis_conn.lrange("network_packets", 0, -1)
        
        parsed_packets = []
        for packet in packets:
            try:
                parsed_packet = json.loads(packet)  # Tenta decodificar como JSON
                parsed_packets.append(parsed_packet)
            except json.JSONDecodeError:
                # Se não estiver em JSON, adiciona como string crua para evitar erro
                parsed_packets.append({"raw_data": packet})

        return jsonify(parsed_packets)
    else:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

# Endpoint para informações de sistema (CPU, RAM, Temperatura)
@app.route('/api/system_info', methods=['GET'])
def get_system_info():
    def generate():
        while True:
            # Uso de CPU
            cpu_usage = psutil.cpu_percent(interval=1)

            # Temperatura da CPU (em Linux)
            cpu_temp = get_cpu_temp()

            # Memória RAM
            memory_info = psutil.virtual_memory()

            # Informações formatadas em JSON
            system_info = {
                "cpu_usage": f"{cpu_usage}%",
                "cpu_temperature": f"{cpu_temp} °C" if cpu_temp is not None else "Temperatura indisponível",
                "total_memory": f"{memory_info.total / (1024 ** 3):.2f} GB",
                "used_memory": f"{memory_info.used / (1024 ** 3):.2f} GB"
            }

            # Enviar dados como evento JSON
            yield f"data: {json.dumps(system_info)}\n\n"
            time.sleep(1)  # Pausa antes da próxima atualização

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
