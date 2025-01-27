import logging

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/home/zrdax/SehenOS/backend/logs/system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()
