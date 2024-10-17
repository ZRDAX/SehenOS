#backend/app.py
import os
import time
from flask import Flask, request, jsonify, Response
from flask_bcrypt import Bcrypt
import psycopg2
import psutil
import subprocess

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos-db",
            user="cypher",
            password="piswos",
            host="localhost",  # Nome do serviço no Docker Compose
            port="5432"  # porta do PostgreSQL
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para obter a temperatura da CPU no Linux
def get_cpu_temp():
    try:
        temp = subprocess.run(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE)
        return int(temp.stdout) / 1000  # Conversão para Celsius
    except Exception as e:
        return None

# Endpoint para autenticação
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = %s;", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result and bcrypt.check_password_hash(result[0], password):
                return jsonify({'message': 'Login bem-sucedido'}), 200
            else:
                return jsonify({'message': 'Credenciais inválidas'}), 401
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return jsonify({"error": "Erro ao executar a query"}), 500
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

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

        anomalies = [
            {"id": row[0], "timestamp": row[1], "src_ip": row[2], "src_hostname": row[3],
            "src_mac": row[4], "dst_ip": row[5], "dst_hostname": row[6], "dst_mac": row[7]}
            for row in rows
        ]
        return jsonify(anomalies)
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500

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

            # Enviar dados como evento
            yield f"data: {jsonify(system_info).get_data(as_text=True)}\n\n"
            time.sleep(1)  # Pausa antes da próxima atualização

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
