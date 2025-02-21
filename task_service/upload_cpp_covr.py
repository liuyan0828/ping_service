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


class UploadCppCovr(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def post(self):
        biz_name = self.get_argument("biz_name", '')
        covr_file = self.request.files
        yield self.run(biz_name, covr_file)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, biz_name, covr_file):
        code = ResponseStatus.SUCCESS.get_code()
        msg = ResponseStatus.SUCCESS.get_msg()
        if biz_name == '' or covr_file.get('covr_file') is None or len(covr_file.get('covr_file')) == 0:
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            source = covr_file.get('covr_file')[0]['body']
            if os.path.isfile("/data/local/qa_service_tmp/cpp_coverage/"+biz_name+"_covr.info"):
                os.remove("/data/local/qa_service_tmp/cpp_coverage/"+biz_name+"_covr.info")
                logging.warning("Cpp covr file is exsit.")
                with open("/data/local/qa_service_tmp/cpp_coverage/"+biz_name+"_covr.info", "wb") as f:
                    f.write(source)
                f.close()
            else:
                with open("/data/local/qa_service_tmp/cpp_coverage/"+biz_name+"_covr.info", "wb") as f:
                    f.write(source)
                f.close()
        self.write({
            "code": code,
            "message": msg
        })
