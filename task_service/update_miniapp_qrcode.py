import logging
import os
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from enum import Enum, unique


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00001": "Success"}
    PARAMETER_ERROR = {"B00001": "Upload file is empty"}

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


class UpdateMiniappQrcode(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def post(self):
        product = self.get_argument("product", 'product')
        channel = self.get_argument("channel", 'channel')
        env = self.get_argument("env", 'env')
        qrcode = self.request.files
        yield self.run(product, channel, env, qrcode)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, product, channel, env, qrcode):
        code = ResponseStatus.SUCCESS.get_code()
        msg = ResponseStatus.SUCCESS.get_msg()
        if qrcode == '' or qrcode.get('qrcode') is None or len(qrcode.get('qrcode')) == 0:
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            qrcode = qrcode.get('qrcode')[0]['body']
            temp_path = '/data/local/qa_service_tmp/qrcode/'
            file_name = product+"_"+channel+"_"+env
            with open(temp_path + file_name + ".png", "wb") as f:
                f.write(qrcode)
            f.close()
        self.write({
            "code": code,
            "message": msg
        })
