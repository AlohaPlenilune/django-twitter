import redis
from django.conf import settings

#

class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # use singleton mode, only create one connection in the global
        if cls.conn:
            return cls.conn
        # if there hasn't been any connection, create one
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        # clear all keys in redis, for testing purpose
        if not settings.TESTING:
            raise Exception('You can not flush redis in production environment!')
        conn = cls.get_connection()
        conn.flushdb()