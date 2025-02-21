# coding=utf-8
from abc import ABC
from concurrent.futures.thread import ThreadPoolExecutor
import tornado.web
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler


class GetScenes(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        yield self.run()
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self):
        scenes_list = []
        # for local debug MysqlHandler:
        # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
        #                                 "qaplatform")
        qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165", "qaplatform")
        scene_id_sql_info = qa_mysql_handler.get_all_obj("select distinct scene_id from pingback_rules",
                                                         "pingback_rules", "scene_id")
        for i in range(len(scene_id_sql_info)):
            scenes_list.append(scene_id_sql_info[i]['scene_id'])
        self.write({
            "data": scenes_list
        })
