# coding=utf-8
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.redis_handler import RedisHandler


class GetRedis(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        yield self.run()
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self):
        # redis_handler = RedisHandler(host='mpt.zw.redis.sohucs.com', password='40e43a76767944c38527cdf45f2f45d5',
        #                              port=22035)
        # on_cloud_redis
        redis_handler = RedisHandler(host='10.23.195.68', password='cUeI7W8t$GKQ', port=6379)
        redis_info = redis_handler.get_redis_task()
        self.write({
            "data": redis_info
        })
