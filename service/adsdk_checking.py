"""
-*- coding: utf-8 -*-
@Time : 2023/1/31 
@Author : liuyan
@function : 
"""

# coding=utf-8
import json
import logging
import tornado.web
import time
import os
from enum import Enum, unique
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.diff_handler import diff_func
from utils.mysql_handler import MysqlHandler
from operator import itemgetter
from urllib.parse import urlparse, parse_qs


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00000": "Success!"}
    MATCH_SUCCESS = {"A00001": "Congrats!All ads are reported consistently~ "}
    NOT_MATCH = {"B000001": "The reports are not matched! "}
    PARAMETER_ERROR = {"E00001": "Some parameter is missing..."}
    EMPTY_FILE_ERROR = {'E00002': "The uploaded file is empty."}
    FILE_TYPE_ERROR = {'E00003': 'Your file type is not supported.'}
    COMPARED_FILE_NOT_EXIST_ERROR = {"E00004": "This device's compared file is not exist,please start the task first."}
    COMPARED_FILE_IS_EMPTY_ERROR = {"E00005": "This device's compared file is empty,please start the task again."}

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


#获取compare_file的文件根路径
class FilePath:
    @staticmethod
    def get_file_path():
        path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        compare_file_dir = os.path.join(path_dir, 'compare_file')
        return compare_file_dir


class AdSdkChecking(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)
    @tornado.web.gen.coroutine
    def post(self):
        post_data = {}
        for key in self.request.arguments:
            post_data[key] = str(self.get_arguments(key)[0])
        # logging.info("Request parameter is: " + str(post_data))
        device_id = self.get_argument("device_id", '')
        task_type = self.get_argument("task_type", '')
        platform = self.get_argument("platform", '')
        auto_case_id = self.get_argument("auto_case_id", '')
        request_file = self.request.files
        yield self.run(device_id, task_type, platform, request_file, auto_case_id)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, device_id, task_type, platform, request_file, auto_case_id):
        data = {}
        mapping = {
            'open': '启动图',
            'oad': '前贴',
            'mad': '中插',
            'pad': '暂停',
            'flogo': '角标',
            'mp': '通栏'
        }
        if device_id == '' or task_type == '' or platform == '':
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        if task_type == 'start':
            compare_file_dir = FilePath().get_file_path()
            if not os.path.exists(compare_file_dir):
                os.makedirs(compare_file_dir)
            file_name = compare_file_dir + '/' + platform + '_' + device_id + '_create.txt'
            # 如果文件已存在，直接覆盖创建即可；设备id为唯一标识，同一设备不可能同时运行不同的任务
            with open(file_name, 'w'):
                code = ResponseStatus.SUCCESS.get_code()
                msg = ResponseStatus.SUCCESS.get_msg()
        elif task_type == 'end':
            if request_file.get('base_file') is None:
                code = ResponseStatus.PARAMETER_ERROR.get_code()
                msg = ResponseStatus.PARAMETER_ERROR.get_msg()
            else:
                base_file = request_file.get('base_file')[0]
                file_type_list = ['text/plain']
                if base_file['content_type'] not in file_type_list:
                    # logging.info("Uploaded file type is: " + base_file['content_type'])
                    code = ResponseStatus.FILE_TYPE_ERROR.get_code()
                    msg = ResponseStatus.FILE_TYPE_ERROR.get_msg()
                elif len(base_file['body']) == 0:
                    code = ResponseStatus.EMPTY_FILE_ERROR.get_code()
                    msg = ResponseStatus.EMPTY_FILE_ERROR.get_msg()
                else:
                    compare_file_dir = FilePath().get_file_path()
                    file_name = compare_file_dir + '/' + platform + '_' + device_id + '_create.txt'
                    if not os.path.exists(file_name):
                        # logging.info("Compared file is: " + file_name)
                        code = ResponseStatus.COMPARED_FILE_NOT_EXIST_ERROR.get_code()
                        msg = ResponseStatus.COMPARED_FILE_NOT_EXIST_ERROR.get_msg()
                    elif not os.path.getsize(file_name):
                        code = ResponseStatus.COMPARED_FILE_IS_EMPTY_ERROR.get_code()
                        msg = ResponseStatus.COMPARED_FILE_IS_EMPTY_ERROR.get_msg()
                    else:
                        base = base_file['body'].decode('utf-8').split('\n')
                        base = [i for i in base if i != '']
                        # 上报需要检验的字段列表，根据业务需求修改
                        param_list = ['path', 'plat', 'sver', 'vp', 'adstyle', 'p', 'posid', 'ac', 'ad', 'pt',
                                      'b', 'bk', 'instream', 'eventtype', 'err', 'ead', 'event', 'al', 'vid', 'tvid',
                                      'site', 'prot', 'sdkVersion', 'bt', 'template', 'adplat', 'displayType',
                                      'trackid']

                        # 处理上传的base_file文件，将具体每条url处理成字典形式
                        for index, url in enumerate(base):
                            base_url = {}
                            if isinstance(url, str):
                                # 获取当前url的path
                                path = url.split('?')[0].split('/')[-1]
                                query_params = parse_qs(urlparse(url).query)
                                for param in param_list:
                                    base_url[param] = query_params.get(param, [None])[0]
                                base_url['path'] = path

                                # 过滤值为空的参数
                                base_url = dict(filter(lambda item: item[1] != None, base_url.items()))
                                base[index] = base_url

                        sorted_base = sorted(base, key=itemgetter('trackid'))
                        diff = diff_func(sorted_base, file_name)
                        sorted_compare_list = diff['sorted_compare_list']

                        if diff['diff']:
                            code = ResponseStatus.NOT_MATCH.get_code()
                            msg = ResponseStatus.NOT_MATCH.get_msg()
                            data['diff'] = diff['diff']
                            compare_result = 'failed'
                        else:
                            compare_result = 'success'
                            code = ResponseStatus.MATCH_SUCCESS.get_code()
                            msg = ResponseStatus.MATCH_SUCCESS.get_msg()
                        data['report_queue'] = diff['report_queue']
                        # 线上环境
                        qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165", "qaplatform")
                        # 测试环境
                        # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165", "qaplatform")
                        scene_name = mapping[base[0]['adstyle']]
                        match_result = json.dumps(sorted_compare_list, separators=(',', ':'), ensure_ascii=False)
                        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace("\'", "\\'")
                        log_content = json.dumps(sorted_base, separators=(',', ':'), ensure_ascii=False)
                        platform = '2' if platform == 'iOS' else '1'
                        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        print(qa_mysql_handler.insert(
                            "insert into ad_pingback_result (scene_name,log_content,match_result,date_time,"
                            "compare_result, platform, data, auto_case_id) values('"  + scene_name +
                            "','" + log_content + "','" + match_result + "','" + date_time + "','" + compare_result +
                            "','" + platform + "','" + data + "','" + auto_case_id + "')"))

                        os.remove(file_name)
                        # 当前文件夹为空才能删除
                        try:
                            os.rmdir(compare_file_dir)
                        except OSError as e:
                            logging.error(e)
        self.write({
            "code": code,
            "msg": msg,
            "data": data
        })

