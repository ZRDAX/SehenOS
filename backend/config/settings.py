import os

# Configuração da URL remota para blacklist
REMOTE_BLACKLIST_URL = os.getenv(
    "REMOTE_BLACKLIST_URL",
    "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset"
)

# Parâmetros de ambiente
ENV = os.getenv("ENV", "development")  # 'development' ou 'production'

