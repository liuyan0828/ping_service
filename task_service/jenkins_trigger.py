from datetime import datetime
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from enum import Enum, unique
import requests


@unique
class ResponseStatus(Enum):
    SUCCESS = {"2000": "Success"}
    PARAMETER_ERROR = {"2001": "Job name missing or job not exsit..."}

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


class JenkinsTrigger(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def post(self):
        param_dict = {}
        for key in self.request.arguments:
            param_dict[key] = str(self.get_arguments(key)[0])
        yield self.run(param_dict)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, param_dict):
        code = ResponseStatus.SUCCESS.get_code()
        msg = ResponseStatus.SUCCESS.get_msg()
        task_id = None
        if not ('job_name' in param_dict):
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            param = ''
            job_name = param_dict['job_name']
            del param_dict['job_name']
            if len(param_dict) == 1 and 'DEVOPS_IMAGE_VERSION' in param_dict:
                job_url = 'http://10.33.4.44:8080/jenkins/job/' + job_name + '/build?'
            elif len(param_dict) > 0:
                job_url = 'http://10.33.4.44:8080/jenkins/job/' + job_name + '/buildWithParameters?'
            else:
                job_url = 'http://10.33.4.44:8080/jenkins/job/' + job_name + '/build?'
            for key in param_dict:
                param = param + str(key) + '=' + str(param_dict[key]) + '&'
            trigger = requests.session()
            trigger.auth = ('admin', '118ae0b1027e59baf59fd4c49852d5df69')
            queue_response = trigger.post(job_url + param)
            print(job_url + param)
            print(queue_response.status_code)
            if queue_response.status_code != 201:
                code = ResponseStatus.PARAMETER_ERROR.get_code()
                msg = ResponseStatus.PARAMETER_ERROR.get_msg()
            else:
                try:
                    next_build_number = requests.get('http://10.33.4.44:8080/jenkins/job/' + job_name +
                                                     '/api/json?pretty=true').json()['nextBuildNumber']
                    task_id = job_name + '---' + str(next_build_number)
                except KeyError:
                    code = ResponseStatus.PARAMETER_ERROR.get_code()
                    msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        self.write({
            "code": code,
            "message": msg,
            "task_id": task_id
        })


class JenkinsStatus(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        param_dict = {}
        for key in self.request.arguments:
            param_dict[key] = str(self.get_arguments(key)[0])
        yield self.run(param_dict)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, param_dict):
        code = ResponseStatus.SUCCESS.get_code()
        msg = ResponseStatus.SUCCESS.get_msg()
        data = {}
        if not ('task_id' in param_dict):
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        elif len(param_dict['task_id'].split('---')) != 2:
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            job_name, build_number = param_dict['task_id'].split('---')
            build_result = requests.get(
                'http://10.33.4.44:8080/jenkins/job/' + job_name + '/' + build_number + '/api/json?pretty=true')
            if build_result.status_code != 200:
                data['task_id'] = param_dict['task_id']
                test_case = {'name': job_name, 'desc': '', 'comment': '', 'result': 'pending', 'start_time': '',
                             'end_time': ''}
                test_cases = [test_case]
                data['test_cases'] = test_cases
                data['start_time'] = ''
                data['end_time'] = ''
                data['task_url'] = ''
            else:
                try:
                    data['task_id'] = param_dict['task_id']
                    start_time = (datetime.fromtimestamp(build_result.json()['timestamp'] // 1000)
                                  .strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])
                    test_case = {'name': job_name, 'desc': '', 'comment': ''}
                    if build_result.json()['result'] == 'SUCCESS':
                        test_case['result'] = 'success'
                        end_time = (datetime.fromtimestamp(
                            (build_result.json()['timestamp'] + build_result.json()['duration']) // 1000).
                                    strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])
                    elif build_result.json()['result'] == 'FAILURE':
                        test_case['result'] = 'failed'
                        end_time = (datetime.fromtimestamp(
                            (build_result.json()['timestamp'] + build_result.json()['duration']) // 1000).
                                    strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])
                    elif build_result.json()['result'] == 'ABORTED':
                        test_case['result'] = 'aborted'
                        end_time = (datetime.fromtimestamp(
                            (build_result.json()['timestamp'] + build_result.json()['duration']) // 1000).
                                    strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])
                    elif build_result.json()['result'] == 'UNSTABLE':
                        test_case['result'] = 'unstable'
                        end_time = (datetime.fromtimestamp(
                            (build_result.json()['timestamp'] + build_result.json()['duration']) // 1000).
                                    strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])
                    else:
                        test_case['result'] = 'running'
                        end_time = ''
                    test_case['start_time'] = start_time
                    test_case['end_time'] = end_time
                    test_cases = [test_case]
                    data['test_cases'] = test_cases
                    data['start_time'] = start_time
                    data['end_time'] = end_time
                    data['task_url'] = 'http://10.33.4.44:8080/jenkins/job/' + job_name + '/' + build_number
                except KeyError:
                    code = ResponseStatus.PARAMETER_ERROR.get_code()
                    msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        self.write({
            "code": code,
            "message": msg,
            "data": data
        })
