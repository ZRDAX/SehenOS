CREATE TABLE IF NOT EXISTS network_traffic (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_ip VARCHAR(15),
    src_hostname VARCHAR(255),
    dst_ip VARCHAR(15),
    dst_hostname VARCHAR(255)
);
