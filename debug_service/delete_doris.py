# coding=utf-8
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler


class DeleteDoris(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        props = self.get_argument("props", '')
        scene_id = self.get_argument("scene_id", '')
        if scene_id == '':
            yield self.run_by_props(props)
        else:
            yield self.run_by_scene_id(scene_id)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run_by_props(self, props):
        if props == '':
            data = 'props error'
        else:
            # doris_handler = MysqlHandler("10.11.138.55", 9030, "mediaai", "aimedia", "mediaai")
            # on_cloud_doris
            doris_handler = MysqlHandler("10.23.251.219", 9030, "mediaai_rw", "aiKimFPw1Qz1RTJw", "mediaai")
            try:
                doris_handler.delete("delete from dwd_shmm_group_test where props = '" + props + "'")
                data = "delete from dwd_shmm_group_test where props = '" + props + "'"
            except Exception as error_info:
                data = 'delete error'
        self.write({
            "data": data
        })

    @run_on_executor
    def run_by_scene_id(self, scene_id):
        doris_handler = MysqlHandler("10.23.251.219", 9030, "mediaai_rw", "aiKimFPw1Qz1RTJw", "mediaai")
        try:
            doris_handler.delete("delete from dwd_shmm_group_test where scene_id = '" + scene_id + "'")
            data = "delete from dwd_shmm_group_test where props = '" + scene_id + "'"
        except Exception as error_info:
            data = 'delete error'
        self.write({
            "data": data
        })
