# coding=utf-8
import json
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
import logging
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler
from enum import Enum, unique


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00000": "Success!"}
    INTERNAL_ERROR = {"E00001": "Internal error..."}

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


class AdSdkGetRules(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        yield self.run()
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, ):
        data = None
        try:
            # for local debug MysqlHandler:
            # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
            #                                                     "qaplatform")
            qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165",
                                            "qaplatform")
            data = qa_mysql_handler.get_all_obj("select scene_id,scene_name,platform,log_content from adsdk_log where "
                                                "is_base='true'", "adsdk_log", "scene_id", "scene_name", "platform",
                                                "log_content")
            for i in range(len(data)):
                data[i]['log_content'] = json.loads(data[i]['log_content'])
            code = ResponseStatus.SUCCESS.get_code()
            msg = ResponseStatus.SUCCESS.get_msg()
        except Exception as error_log:
            logging.error(error_log)
            code = ResponseStatus.INTERNAL_ERROR.get_code()
            msg = ResponseStatus.INTERNAL_ERROR.get_msg()
        self.write({
            "code": code,
            "msg": msg,
            "data": data
        })
