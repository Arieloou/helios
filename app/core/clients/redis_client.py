# core/redis_client.py

import redis.asyncio as redis
import json
import time

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    async def set_cache(self, key: str, value: dict, expiration_seconds: int = 300):
        """Guarda un dato en Redis con un tiempo de expiración."""
        # Convertimos el diccionario/lista de Python a un string de JSON
        value_json = json.dumps(value)
        await self.redis.set(key, value_json, ex=expiration_seconds)

    async def get_cache(self, key: str):
        """Obtiene un dato de Redis si existe."""
        result = await self.redis.get(key)
        if result:
            return json.loads(result) # Convertimos el JSON de vuelta a Python
        return None

    async def add_to_blocklist(self, user_id: str, ttl_seconds: int):
        """
        Marca que todos los tokens emitidos ANTES de ahora quedan inválidos.
        ttl_seconds debe ser >= la vida máxima de un refresh token,
        para no acumular claves para siempre.
        """
        key = f"user:{user_id}:tokens_invalid_before"
        await self.redis.set(key, str(int(time.time())), ex=ttl_seconds)

    async def is_issued_before_invalidation(self, user_id: str, issued_at: int) -> bool:
        """True si el token (según su claim 'iat') fue emitido antes de la revocación masiva."""
        key = f"user:{user_id}:tokens_invalid_before"
        invalid_before = await self.redis.get(key)
        if invalid_before and issued_at < int(invalid_before):
            return True
        return False