# coding=utf-8
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler
from enum import Enum, unique


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00000": "Success"}
    PARAMETER_ERROR = {"E00001": "Parameter is empty..."}

    def get_code(self):
        """
        根据枚举名称取状态码code
        :return: 状态码code
        """
        return list(self.value.keys())[0]

    def get_msg(self):
        """
        根据枚举名称取状态说明message
        :return: 状态说明message
        """
        return list(self.value.values())[0]


class DeleteRules(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        scene_id = self.get_argument("scene_id", '')
        yield self.run(scene_id)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, scene_id):
        # for local debug MysqlHandler:
        # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
        #                                 "qaplatform")
        qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165", "qaplatform")
        if scene_id == '':
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            qa_mysql_handler.delete("delete from pingback_rules where scene_id='" + scene_id + "'")
            code = ResponseStatus.SUCCESS.get_code()
            msg = ResponseStatus.SUCCESS.get_msg()
        self.write({
            "code": code,
            "msg": msg
        })
