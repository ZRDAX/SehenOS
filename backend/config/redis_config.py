import redis
from app.config import Config

def get_redis_connection():
    """
    Inicializa e retorna a conexão com o Redis.
    """
    return redis.StrictRedis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB
    )

redis_client = get_redis_connection()
