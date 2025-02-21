# coding=utf-8
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler


class GetDoris(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        scale = self.get_argument("scale", '')
        like = self.get_argument("like", '')
        yield self.run(scale, like)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, scale, like):
        if scale == '':
            scale = '*'
        # doris_handler = MysqlHandler("10.11.138.55", 9030, "mediaai", "aimedia", "mediaai")
        # on_cloud_doris
        doris_handler = MysqlHandler("10.23.251.219", 9030, "mediaai_rw", "aiKimFPw1Qz1RTJw", "mediaai")
        if like == '':
            doris_info = doris_handler.get_all_obj("select " + scale + " from dwd_shmm_group_test",
                                                   "dwd_shmm_group_test")
        else:
            doris_info = doris_handler.get_all_obj("select " + scale + " from dwd_shmm_group_test where props like '%"
                                                   + like + "%'", "dwd_shmm_group_test")
        self.write({
            "data": doris_info
        })
