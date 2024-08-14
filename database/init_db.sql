CREATE TABLE network_traffic (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_ip VARCHAR(45),
    src_hostname VARCHAR(255),
    dst_ip VARCHAR(45),
    dst_hostname VARCHAR(255)
);

-- Conceder permissões ao usuário
GRANT INSERT, SELECT ON TABLE network_traffic TO sehenos;

-- Verificar sequência padrão
ALTER SEQUENCE network_traffic_id_seq OWNED BY network_traffic.id;
GRANT USAGE, SELECT ON SEQUENCE network_traffic_id_seq TO sehenos;

