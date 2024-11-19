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

# Cria handlers
file_handler = FileHandler('logs/app.log')
stream_handler = StreamHandler()

# Define o formato para os handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Obtém o logger
logger = logging.getLogger(__name__)

# Adiciona os handlers ao logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Configurações
REDIS_HOST = 'localhost'
REDIS_PORT = 6380
PACKET_BACKUP_PATH = "packet_capture_backup.txt"
ANOMALY_BACKUP_PATH = "anomaly_detection_backup.txt"
SYSTEM_INFO_INTERVAL = 1  # segundos

# Conexão com o Redis
def connect_redis():
    try:
        r = redis.StrictRedis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=0, 
            decode_responses=True,
            socket_timeout=5
        )
        r.ping()  # Verifica se a conexão está ativa
        return r
    except redis.ConnectionError as e:
        logger.error(f"Erro ao conectar ao Redis: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao conectar ao Redis: {e}")
        return None

# Função para obter a temperatura da CPU no Linux
def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            temp = int(temp_file.read()) / 1000
        return temp
    except FileNotFoundError:
        logger.warning("Arquivo de temperatura da CPU não encontrado")
        return None
    except Exception as e:
        logger.error(f"Erro ao ler temperatura da CPU: {e}")
        return None

# Função para formatar pacotes de rede
def format_network_packet(packet_str):
    try:
        packet = json.loads(packet_str)
        return {
            "timestamp": packet.get("timestamp", datetime.now().isoformat()),
            "src_ip": packet.get("src_ip", "unknown"),
            "dst_ip": packet.get("dst_ip", "unknown"),
            "src_mac": packet.get("src_mac", "unknown"),
            "dst_mac": packet.get("dst_mac", "unknown"),
            "src_hostname": packet.get("src_hostname", "unknown"),
            "dst_hostname": packet.get("dst_hostname", "unknown"),
            "protocol": packet.get("protocol", "unknown"),
            "length": packet.get("length", 0),
            "connection_stats": packet.get("connection_stats", {})
        }
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar pacote: {e}")
        return None

# Endpoint para baixar o arquivo de backup dos pacotes
@app.route('/api/packet_backup', methods=['GET'])
def get_packet_backup():
    try:
        if not os.path.exists(PACKET_BACKUP_PATH):
            return jsonify({"error": "Arquivo de backup não encontrado"}), 404
        return send_file(PACKET_BACKUP_PATH, as_attachment=True)
    except Exception as e:
        logger.error(f"Erro ao enviar arquivo de backup de pacotes: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para baixar o arquivo de backup das anomalias
@app.route('/api/anomaly_backup', methods=['GET'])
def get_anomaly_backup():
    try:
        if not os.path.exists(ANOMALY_BACKUP_PATH):
            return jsonify({"error": "Arquivo de backup não encontrado"}), 404
        return send_file(ANOMALY_BACKUP_PATH, as_attachment=True)
    except Exception as e:
        logger.error(f"Erro ao enviar arquivo de backup de anomalias: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para listar as anomalias do Redis
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    redis_conn = connect_redis()
    if not redis_conn:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

    try:
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        anomaly_type = request.args.get('type')  # Filtro por tipo de anomalia

        start = (page - 1) * per_page
        end = start + per_page - 1

        # Obtém as anomalias com paginação
        anomalies = redis_conn.lrange("anomalies", start, end)
        total_anomalies = redis_conn.llen("anomalies")

        # Processa as anomalias
        processed_anomalies = []
        for anomaly in anomalies:
            try:
                anomaly_data = json.loads(anomaly)
                
                # Filtro por tipo de anomalia
                if anomaly_type and anomaly_data.get('type') != anomaly_type:
                    continue
                
                processed_anomalies.append(anomaly_data)
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar anomalia: {e}")
                continue

        return jsonify({
            "anomalies": processed_anomalies,
            "total": total_anomalies,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_anomalies + per_page - 1) // per_page
        })

    except Exception as e:
        logger.error(f"Erro ao recuperar anomalias: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para listar os pacotes do Redis
@app.route('/api/packets', methods=['GET'])
def get_packets():
    redis_conn = connect_redis()
    if not redis_conn:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

    try:
        # Chaves de pacotes
        packet_keys = ["network_packets", "processed_packets"]
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        start = (page - 1) * per_page
        end = start + per_page - 1

        # Processa os pacotes
        processed_packets = []
        total_packets = 0

        for key in packet_keys:
            if redis_conn.exists(key):
                packets = redis_conn.lrange(key, start, end)
                total_packets += redis_conn.llen(key)

                for packet in packets:
                    formatted_packet = format_network_packet(packet)
                    if formatted_packet:
                        processed_packets.append(formatted_packet)

        return jsonify({
            "packets": processed_packets,
            "total": total_packets,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_packets + per_page - 1) // per_page
        })

    except Exception as e:
        logger.error(f"Erro ao recuperar pacotes: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para estatísticas do sistema
@app.route('/api/system_info', methods=['GET'])
def get_system_info():
    def generate():
        while True:
            try:
                # Uso de CPU
                cpu_usage = psutil.cpu_percent(interval=1)

                # Temperatura da CPU
                cpu_temp = get_cpu_temp()

                # Informações de memória
                memory = psutil.virtual_memory()

                # Estatísticas do Redis
                redis_conn = connect_redis()
                redis_stats = {
                    "total_packets": redis_conn.llen("network_packets") if redis_conn else 0,
                    "total_anomalies": redis_conn.llen("anomalies") if redis_conn else 0
                }

                # Informações do sistema
                system_info = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu": {
                        "usage": f"{cpu_usage}%",
                        "temperature": f"{cpu_temp:.1f}°C" if cpu_temp is not None else "N/A"
                    },
                    "memory": {
                        "total": f"{memory.total / (1024**3):.2f}GB",
                        "used": f"{memory.used / (1024**3):.2f}GB",
                        "percent": f"{memory.percent}%"
                    },
                    "redis_stats": redis_stats
                }

                yield f"data: {json.dumps(system_info)}\n\n"
                time.sleep(SYSTEM_INFO_INTERVAL)

            except Exception as e:
                logger.error(f"Erro ao gerar informações do sistema: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                time.sleep(SYSTEM_INFO_INTERVAL)

    return Response(generate(), mimetype='text/event-stream')

# Endpoint para sumário do sistema
@app.route('/api/system_summary', methods=['GET'])
def get_system_summary():
    try:
        redis_conn = connect_redis()
        if not redis_conn:
            return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

        # Coleta todas as informações relevantes
        summary = {
            "system_status": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_temperature": get_cpu_temp()
            },
            "network_status": {
                "total_packets_captured": redis_conn.llen("network_packets"),
                "total_anomalies_detected": redis_conn.llen("anomalies")
            },
            "backup_status": {
                "packet_backup_exists": os.path.exists(PACKET_BACKUP_PATH),
                "anomaly_backup_exists": os.path.exists(ANOMALY_BACKUP_PATH)
            },
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(summary)

    except Exception as e:
        logger.error(f"Erro ao gerar sumário do sistema: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint para limpar dados do Redis
@app.route('/api/clear_data', methods=['POST'])
def clear_redis_data():
    redis_conn = connect_redis()
    if not redis_conn:
        return jsonify({"error": "Não foi possível conectar ao Redis"}), 500

    try:
        # Chaves a serem limpas
        keys_to_clear = [
            "network_packets", 
            "processed_packets", 
            "anomalies"
        ]

        for key in keys_to_clear:
            redis_conn.delete(key)

        return jsonify({
            "status": "success", 
            "message": "Dados limpos com sucesso"
        })

    except Exception as e:
        logger.error(f"Erro ao limpar dados do Redis: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Iniciando aplicação Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)