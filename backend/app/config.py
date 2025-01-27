import os

class Config:
    # Configurações Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6380))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    # Caminhos de arquivos
    BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
    BLACKLIST_FILE = os.getenv("BLACKLIST_FILE", "/home/zrdax/SehenOS/backend/list/blacklist.txt")  
    WHITELIST_FILE = os.getenv("WHITELIST_FILE", "/home/zrdax/SehenOS/backend/list/whitelist.txt")

    # Logs
    LOG_FILE = os.getenv("LOG_FILE", "/home/zrdax/SehenOS/backend/logs/system.log")

    # Modo de depuração
    DEBUG = bool(os.getenv("DEBUG", True))
