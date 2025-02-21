# coding=utf-8
import json
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
import logging
from tornado.concurrent import run_on_executor
from utils.log_handler import ad_log_match, remove_list_dict_duplicate
from utils.mysql_handler import MysqlHandler
from enum import Enum, unique
import time


@unique
class ResponseStatus(Enum):
    UPLOAD_BASE = {"A00000": "Base upload success!"}
    MATCH_SUCCESS = {"A00001": "Compare match!"}
    UPDATE_BASE = {"A00002": "Update base success!"}
    NOT_MATCH = {"W00001": "Match failure..."}
    NO_BASE = {"W00002": "No base log(s)..."}
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


class AdSdkCompare(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def post(self):
        post_data = {}
        for key in self.request.arguments:
            post_data[key] = str(self.get_arguments(key)[0])
        logging.info("Request parameter is: " + str(post_data))
        scene_id = self.get_argument("scene_id", '')
        scene_name = self.get_argument("scene_name", '')
        is_base = self.get_argument("is_base", 'false')
        request_file = self.request.files
        yield self.run(scene_id, scene_name, is_base, request_file)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, scene_id, scene_name, is_base, request_file):
        data = None
        if scene_id == '' or scene_name == '' or request_file.get('sdk_log') is None:
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            try:
                log_dict = json.loads(request_file.get('sdk_log')[0]['body'].decode('utf-8').
                                      replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', ''))
                platform = log_dict['plat']
                if is_base == 'true':
                    for i in range(len(log_dict['methodList'])):
                        if 'st' in log_dict['methodList'][i] or 'params' in log_dict['methodList'][i]:
                            try:
                                del log_dict['methodList'][i]['st']
                                del log_dict['methodList'][i]['params']
                            except KeyError:
                                pass
                    log_dict['methodList'] = remove_list_dict_duplicate(log_dict['methodList'])
                    base_log = json.dumps(log_dict['methodList'], separators=(',', ':'), ensure_ascii=False)
                    # for local debug MysqlHandler:
                    # qa_mysql_handler = MysqlHandler("10.19.43.154", 3306, "herla_backend", "Qa_platform|8165",
                    #                                                     "qaplatform")
                    qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165",
                                                    "qaplatform")
                    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    db_base_log = qa_mysql_handler.get_all_obj(
                        "select log_content from adsdk_log where scene_id = '" + scene_id + "' and platform ='" +
                        platform + "' and is_base = 'true'", "adsdk_log", "log_content")
                    if len(db_base_log) == 0:
                        # 日志存入数据库
                        qa_mysql_handler.insert("insert into adsdk_log (scene_id,scene_name,is_base,log_content,"
                                                "date_time,platform) values('" + scene_id + "','" + scene_name + "','" +
                                                is_base + "','" + base_log + "','" + date_time + "','" + platform + "')"
                                                )
                        code = ResponseStatus.UPLOAD_BASE.get_code()
                        msg = ResponseStatus.UPLOAD_BASE.get_msg()
                    else:
                        qa_mysql_handler.update("update adsdk_log set log_content='" + base_log + "' where scene_id='" +
                                                scene_id + "' and platform='" + platform + "' and is_base='true'")
                        code = ResponseStatus.UPDATE_BASE.get_code()
                        msg = ResponseStatus.UPDATE_BASE.get_msg()
                else:
                    # for local debug MysqlHandler:
                    # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
                    #                                                     "qaplatform")
                    # 取基础规则
                    qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165",
                                                    "qaplatform")
                    base_log = qa_mysql_handler.get_all_obj(
                        "select log_content from adsdk_log where scene_id = '" + scene_id + "' and platform = '" +
                        platform + "' and is_base = 'true'", "adsdk_log", "log_content")
                    if len(base_log) == 0:
                        code = ResponseStatus.NO_BASE.get_code()
                        msg = ResponseStatus.NO_BASE.get_msg()
                    else:
                        base_log = json.loads(base_log[0]['log_content'])
                        test_log = log_dict['methodList']
                        # 调用ad对比
                        data = ad_log_match(base_log, test_log)
                        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        match_result = json.dumps(data['warning_list'], separators=(',', ':'))
                        for i in range(len(data['warning_list'])):
                            base_log.remove(data['warning_list'][i])
                        log_content = json.dumps(base_log, separators=(',', ':'), ensure_ascii=False)
                        if len(data['warning_list']) == 0:
                            compare_result = 'success'
                        else:
                            compare_result = 'failed'
                        qa_mysql_handler.insert(
                            "insert into adsdk_log (scene_id,scene_name,is_base,match_result,date_time,log_content,"
                            "compare_result, platform) values('" + scene_id + "','" + scene_name + "','" + is_base +
                            "','" + match_result + "','" + date_time + "','" + log_content + "','" + compare_result +
                            "','" + platform + "')")
                        if not data['warning_list']:
                            code = ResponseStatus.MATCH_SUCCESS.get_code()
                            msg = ResponseStatus.MATCH_SUCCESS.get_msg()
                        else:
                            code = ResponseStatus.NOT_MATCH.get_code()
                            msg = ResponseStatus.NOT_MATCH.get_msg()
            except Exception as error_log:
                logging.error(error_log)
                code = ResponseStatus.INTERNAL_ERROR.get_code()
                msg = ResponseStatus.INTERNAL_ERROR.get_msg()
        self.write({
            "code": code,
            "msg": msg,
            "data": data
        })
