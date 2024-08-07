import re
import pandas as pd
from sqlalchemy import create_engine

# Definir expressões regulares para extrair informações
regex_mac = re.compile(r'MACo: ([0-9A-Fa-f:]{17}), MACd: ([0-9A-Fa-f:]{17})')
regex_ip = re.compile(r'IPo: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}), IPd: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
regex_fqdn = re.compile(r'FQDN: ([^\s,]+)')
regex_intrusion = re.compile(r'Intrusion: ([^,]+)')

# Função para processar o arquivo de log e retornar um DataFrame
def process_logs(file_path):
    data = []
    
    with open(file_path, 'r') as file:
        logs = file.readlines()
    
    for line in logs:
        mac_match = regex_mac.search(line)
        ip_match = regex_ip.search(line)
        fqdn_match = regex_fqdn.search(line)
        intrusion_match = regex_intrusion.search(line)
        
        entry = {}
        
        if mac_match:
            mac_src, mac_dst = mac_match.groups()
            entry['MAC_src'] = mac_src
            entry['MAC_dst'] = mac_dst
        
        if ip_match:
            ip_src, ip_dst = ip_match.groups()
            entry['IP_src'] = ip_src
            entry['IP_dst'] = ip_dst
        
        if fqdn_match:
            fqdn = fqdn_match.group(1)
            entry['FQDN'] = fqdn
        
        if intrusion_match:
            intrusion = intrusion_match.group(1)
            entry['Intrusion'] = intrusion
        
        if entry:
            data.append(entry)
    
    df = pd.DataFrame(data)
    return df

# Caminho para o arquivo de log
log_file_path = 'logs\LogsGET.txt'

# Processar os logs e obter o DataFrame
df = process_logs(log_file_path)

# Configuração do banco de dados PostgreSQL
DATABASE_URL = 'postgresql://sehenos:piswos@localhost:5432/swiredb'
engine = create_engine(DATABASE_URL)

# Inserir os dados no banco de dados
with engine.connect() as conn:
    df.to_sql('network_logs', conn, if_exists='append', index=False)
