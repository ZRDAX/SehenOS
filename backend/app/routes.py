from flask import Flask, Blueprint, jsonify, request
from redis import Redis
from blacklist_whitelist import update_blacklist, update_whitelist
from system_info import get_system_info
from config.redis_config import redis_client
import os
import json
import subprocess
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_blueprint = Blueprint('api', __name__)
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)


# |-------------------------↓ CAPT/ANOM ↓----------------------------------|

# Endpoint para pacotes capturados
@api_blueprint.route('/packets', methods=['GET'])
def get_packets():
    packets = redis_client.lrange("network_packets", 0, -1)
    return jsonify([json.loads(packet) for packet in packets])

# Endpoint para anomalias detectadas
@api_blueprint.route('/anomalies', methods=['GET'])
def get_anomalies():
    anomalies = redis_client.lrange("network_anomalies", 0, -1)
    return jsonify([json.loads(anomaly) for anomaly in anomalies])

# |-------------------------↓  LIST  ↓-------------------------------------|

# Endpoint para editar a blacklist
@api_blueprint.route('/blacklist_edit', methods=['POST'])
def edit_blacklist():
    data = request.json
    action = data.get("action")  # 'add' ou 'remove'
    ip = data.get("ip")

    if not ip:
        return jsonify({"status": "error", "message": "IP não fornecido."}), 400

    try:
        update_blacklist(ip, action)
        return jsonify({"status": "success", "message": f"IP {action}ed com sucesso na blacklist."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
# Endpoint para editar a whitelist
@api_blueprint.route('/whitelist_edit', methods=['POST'])
def edit_whitelist():
    data = request.json
    action = data.get("action")  # 'add' ou 'remove'
    ip = data.get("ip")

    if not ip:
        return jsonify({"status": "error", "message": "IP não fornecido."}), 400

    try:
        update_whitelist(ip, action)
        return jsonify({"status": "success", "message": f"IP {action}ed com sucesso na whitelist."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# |-------------------------↓ SISTEMA ↓------------------------------------|

# Endpoint para informações do sistema
@api_blueprint.route('/system_info', methods=['GET'])
def get_system_info_endpoint():
    return jsonify(get_system_info())

# Endpoint para limpar dados
@api_blueprint.route('/clear_data', methods=['POST'])
def clear_data():
    redis_client.flushdb()
    return jsonify({"status": "success", "message": "Dados limpos."})

# Endpoint para desligar o sistema
@api_blueprint.route('/shutdown_sys', methods=['POST'])
def shutdown_system():
    try:
        subprocess.run(['sudo', 'shutdown', 'now'], check=True)
        return jsonify({"status": "success", "message": "Sistema será desligado."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint para reiniciar o sistema
@api_blueprint.route('/reboot_sys', methods=['POST'])
def reboot_system():
    try:
        subprocess.run(['sudo', 'reboot'], check=True)
        return jsonify({"status": "success", "message": "Sistema será reiniciado."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# |-------------------------↓ BACKUPS ↓------------------------------------|

# Endpoint para backups de pacotes
@api_blueprint.route('/list_packet_backup', methods=['GET'])
def list_packet_backup():
    try:
        backup_files = [f for f in os.listdir(Config.BACKUP_DIR) if f.startswith('packets')]
        return jsonify({"backups": backup_files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint para backups de anomalias
@api_blueprint.route('/list_anomaly_backup', methods=['GET'])
def list_anomaly_backup():
    try:
        backup_files = [f for f in os.listdir(Config.BACKUP_DIR) if f.startswith('anomalies')]
        return jsonify({"backups": backup_files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
#        |-------------↓ MANUAL-BACKUPS ↓--------|
    
# Endpoint para salvar backup manualmente de pacotes
@api_blueprint.route('/save_packet_backup', methods=['POST'])
def manual_save_packet_backup():
    try:
        backup_file = save_packet_backup()
        return jsonify({"status": "success", "backup_file": backup_file})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint para salvar backup manualmente de anomalias
@api_blueprint.route('/save_anomaly_backup', methods=['POST'])
def manual_save_anomaly_backup():
    try:
        backup_file = save_anomaly_backup()
        return jsonify({"status": "success", "backup_file": backup_file})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Inicializar a aplicação Flask e registrar o blueprint
app = Flask(__name__)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    logger.info("Iniciando aplicação Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)