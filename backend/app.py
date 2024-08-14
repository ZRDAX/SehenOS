from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Conexão com o banco de dados PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="sehenos_db",
            user="sehenos",
            password="piswos",
            host="localhost"  # Nome do serviço no Docker Compose
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

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
        df = load_data(conn)  # Use a função load_data do script anterior
        conn.close()
        
        df_processed = preprocess_data(df)
        X_train, X_test = split_data(df_processed)
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_train)
        y_pred = model.predict(X_test)
        
        anomalies = X_test[y_pred == -1]
        anomalies_list = anomalies.tolist()

        # Convertendo para JSON
        anomalies_json = [{"src_ip": row[0], "dst_ip": row[1], "src_hostname": row[2], "dst_hostname": row[3]} for row in anomalies_list]
        return jsonify(anomalies_json)
    else:
        return jsonify({"error": "Não foi possível conectar ao banco de dados"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
