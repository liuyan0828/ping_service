# coding=utf-8
import redis


class RedisHandler:
    def __init__(self, host, port, password, db=0, decode_responses=True):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.decode_responses = decode_responses

    def add_task(self, key, value):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        conn.rpush(key, value)
        pool.disconnect()

    def remove_task(self, key, value):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        conn.lrem(key, 0, value)
        pool.disconnect()

    def get_full_value(self, key, redis_dict):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        result = conn.lrange(key, 0, -1)
        pool.disconnect()
        for i in range(len(result)):
            if redis_dict['script_id'] in result[i] and redis_dict['scene_id'] in result[i] \
                    and redis_dict['unique_value'] in result[i]:
                return result[i]
            else:
                pass
        return None

    def is_unique_value_exist(self, key, unique_value):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        result = conn.lrange(key, 0, -1)
        pool.disconnect()
        if len(result) == 0:
            return False
        else:
            for i in range(len(result)):
                if unique_value in result[i]:
                    return True
                else:
                    pass
            return False

    def get_redis_task(self):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        pc_wap_list = conn.lrange("group_test:pc_wap", 0, -1)
        app_mini_list = conn.lrange("group_test:app_mini", 0, -1)
        pool.disconnect()
        return {"pc_wap": pc_wap_list, "app_mini": app_mini_list}

    def clean_redis(self):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password,
                                    db=self.db, decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        pc_wap_list = conn.lrange("group_test:pc_wap", 0, -1)
        for i in range(0, len(pc_wap_list)):
            conn.lrem("group_test:pc_wap", 0, pc_wap_list[i])
        app_mini_list = conn.lrange("group_test:app_mini", 0, -1)
        for j in range(0, len(app_mini_list)):
            conn.lrem("group_test:app_mini", 0, app_mini_list[j])
        pool.disconnect()
        return True
