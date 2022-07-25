from django.conf import settings

from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()

        serialized_list = []
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            # rpush可以直接把一串数据都push进去，而不要用for循环，不然多次访问数据库会浪费
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()

        # if exists in cache, take out and return
        if conn.exists(key):
            # cache hit
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_data in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects

        # cache miss
        cls._load_objects_to_cache(key, queryset)

        # 转为list是因为要保持返回类型的统一。因为redis里面的数据是list的形式
        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        if not conn.exists(key):
            # if key does not exist in cache, load data from database
            # and do not use push to append to cache
            cls._load_objects_to_cache(key, queryset)
            return
        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1) # 0-199

    @classmethod
    def get_count_key(cls, obj, attr):
        # this function works for both likes_count and comments_count
        # so we use attr to distinguish likes_count and comments_count
        return '{}.{}:{}'.format(obj.__class__.__name__, attr, obj.id)

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if conn.exists(key):
            # incr(key) will get the value, increase by 1 and return the new value
            return conn.incr(key)

        # set the attr with related key
        # back fill cache from db
        # obj.refresh_from_db() will reload data from db,
        # 不执行+1操作，因为必须保证调用incr_count之前obj.attr已经+1过了
        # 不能保证调用者会在调用本函数前更新最新数据，所以在这个函数内部写refresh，以防调用者没有使用更新过的数据
        obj.refresh_from_db()
        conn.set(key, getattr(obj, attr))
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)


    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if conn.exists(key):
            return conn.decr(key)

        # obj.refresh_from_db() will reload data from db,
        # 不执行 -1 操作，因为必须保证调用 decr_count 之前 obj.attr 已经 -1 过了
        obj.refresh_from_db()
        conn.set(key, getattr(obj, attr))
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        count = conn.get(key)
        if count is not None:
            return int(count)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        return count
