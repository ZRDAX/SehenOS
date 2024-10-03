#backend/app.py
import os
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import psycopg2

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        #db_host = os.getenv('DB_HOST', 'localhost')
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
