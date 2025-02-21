# coding=utf-8
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
import logging
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler
from enum import Enum, unique


@unique
class ResponseStatus(Enum):
    DELETE_SUCCESS = {"A00000": "Delete success!"}
    PARAMETER_ERROR = {"E00001": "Parameter error..."}
    INTERNAL_ERROR = {"E00002": "Internal error..."}

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


class AdSdkDeleteRule(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        scene_id = self.get_argument("scene_id", '')
        platform = self.get_argument("platform", '')
        yield self.run(scene_id, platform)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, scene_id, platform):
        if scene_id == '' or platform == '':
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            try:
                # for local debug MysqlHandler:
                # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
                #                                                     "qaplatform")
                qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165",
                                                "qaplatform")
                qa_mysql_handler.delete("delete from adsdk_log where scene_id='" + scene_id + "' and platform='"
                                        + platform + "'")
                code = ResponseStatus.DELETE_SUCCESS.get_code()
                msg = ResponseStatus.DELETE_SUCCESS.get_msg()
            except Exception as error_log:
                logging.error(error_log)
                code = ResponseStatus.INTERNAL_ERROR.get_code()
                msg = ResponseStatus.INTERNAL_ERROR.get_msg()
        self.write({
            "code": code,
            "msg": msg+" scene_id: "+scene_id+", platfrom: "+platform
        })
