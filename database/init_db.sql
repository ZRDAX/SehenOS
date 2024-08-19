CREATE TABLE network_traffic (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_ip VARCHAR(45),
    src_hostname VARCHAR(255),
    src_mac VARCHAR(60),
    dst_ip VARCHAR(45),
    dst_hostname VARCHAR(255),
    dst_mac VARCHAR(60)
);

CREATE TABLE anomalies ( 
    id SERIAL PRIMARY KEY, 
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    src_ip VARCHAR(45), 
    dst_ip VARCHAR(45), 
    src_hostname VARCHAR(255), 
    dst_hostname VARCHAR(255),
    src_mac VARCHAR(60),
    dst_mac VARCHAR(60) 
);

-- Conceder permissões ao usuário
GRANT ALL PRIVILEGES ON TABLE network_traffic TO cypher;
GRANT ALL PRIVILEGES ON TABLE anomalies TO cypher;

GRANT ALL PRIVILEGES ON SEQUENCE network_traffic_id_seq TO cypher;
GRANT ALL PRIVILEGES ON SEQUENCE anomalies_id_seq TO cypher;


