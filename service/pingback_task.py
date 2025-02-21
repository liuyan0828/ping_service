# coding=utf-8
import json
import logging
import tornado.web
import time
from enum import Enum, unique
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.log_handler import result_conclude
from utils.redis_handler import RedisHandler
from utils.mysql_handler import MysqlHandler
from utils import log_handler


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00000": "Success!"}
    MATCH_SUCCESS = {"A00001": "MATCH!"}
    MATCH_FAILURE = {"B00001": "Match failure..."}
    PARAMETER_ERROR = {"E00001": "Some parameter is missing..."}
    BAD_LOG_ERROR = {"E00002": "Ping_back log have bad case(s)..."}
    UNIQUE_VALUE_INUSE = {"E00003": "--(unique value) is already in use..."}
    TASK_NOT_EXIST = {"E00004": "This task is already end or never start..."}
    INTERNAL_ERROR = {"E00005": "Meet some internal error..."}

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


class PingBackTask(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        post_data = {}
        for key in self.request.arguments:
            post_data[key] = str(self.get_arguments(key)[0])
        logging.info("Request parameter is: " + str(post_data))
        script_id = self.get_argument("script_id", '')
        scene_id = self.get_argument("scene_id", '')
        unique_key = self.get_argument("unique_key", '')
        unique_value = self.get_argument("unique_value", '')
        task_type = self.get_argument("task_type", '')
        yield self.run(script_id, scene_id, unique_key, unique_value, task_type)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, script_id, scene_id, unique_key, unique_value, task_type):
        # 初始化变量值
        code = ResponseStatus.SUCCESS.get_code()
        msg = ResponseStatus.SUCCESS.get_msg()
        data, test_rules, result_conclusion, test_rules_conclusion = None, None, {}, {}
        # 判断参数是否完整
        if script_id == '' or scene_id == '' or unique_key == '' or unique_value == '' or task_type == '':
            code = ResponseStatus.PARAMETER_ERROR.get_code()
            msg = ResponseStatus.PARAMETER_ERROR.get_msg()
        else:
            redis_handler = RedisHandler(host='10.23.195.68', password='cUeI7W8t$GKQ', port=6379)
            # 判断redis key，以符合星盘要求
            if 'PC' in scene_id or 'Wap' in scene_id:
                redis_key = "group_test:pc_wap"
            else:
                redis_key = "group_test:app_mini"
            # 判断任务类型
            if task_type == 'start':
                # 如果存在相同任务，返回对应错误
                if redis_handler.is_unique_value_exist(redis_key, unique_value):
                    code = ResponseStatus.UNIQUE_VALUE_INUSE.get_code()
                    msg = unique_value + ResponseStatus.UNIQUE_VALUE_INUSE.get_msg()
                # 如果不存在相同任务，创建任务至redis，并返回创建成功
                else:
                    expire_time = int(time.time()) + 86400
                    value_dict = {'script_id': script_id, 'scene_id': scene_id, 'unique_key': unique_key,
                                  'unique_value': unique_value, 'expire_time': str(expire_time)}
                    try:
                        redis_handler.add_task(redis_key, str(value_dict))
                        code = ResponseStatus.SUCCESS.get_code()
                        msg = ResponseStatus.SUCCESS.get_msg() + " " + task_type
                    except Exception as error_info:
                        code = ResponseStatus.INTERNAL_ERROR.get_code()
                        msg = ResponseStatus.INTERNAL_ERROR.get_msg()
                        logging.warning(error_info)
            elif task_type == 'end':
                # 获取本次任务再redis中键值
                project = scene_id.split("_")[0]
                project = "miniapp" if "mini" in project or "app" in project else project
                value_dict = {'script_id': script_id, 'scene_id': scene_id, 'unique_key': unique_key,
                              'unique_value': unique_value}
                redis_value = redis_handler.get_full_value(redis_key, value_dict)
                logging.info("redis_value is: " + json.dumps(redis_value))
                # redis中存在对应键值，即存在该任务
                if redis_value is None:
                    code = ResponseStatus.TASK_NOT_EXIST.get_code()
                    msg = ResponseStatus.TASK_NOT_EXIST.get_msg()
                # 如果redis不存在该键值，返回任务不存在
                else:
                    code = ResponseStatus.SUCCESS.get_code()
                    msg = ResponseStatus.SUCCESS.get_msg() + " " + task_type
                    data = {}
                    # 获取doris埋点日志
                    doris_handler = MysqlHandler("10.23.251.219", 9030, "mediaai_rw", "aiKimFPw1Qz1RTJw", "mediaai")
                    doris_info = doris_handler.get_all_obj("select track_type, log from "
                                                           "dwd_shmm_group_test where props like '%" + unique_value +
                                                           "%'", "dwd_shmm_group_test", "track_type", "log")
                    # 根据doris日志生成测试规则
                    test_rules, test_rules_structure = log_handler.generate_base_rules(project, doris_info)
                    # 判断是否存在bad case，如果存在，给code赋值，用做标记
                    for key in test_rules:
                        if test_rules[key] is None and 'pv' in key:
                            code = ResponseStatus.BAD_LOG_ERROR.get_code()
                            msg = ResponseStatus.BAD_LOG_ERROR.get_msg()
                            data['pv_bad_log'] = test_rules_structure['pv_rules_structure']
                            '''
                            elif test_rules[key] is None and 'ev' in key:
                                code = ResponseStatus.BAD_LOG_ERROR.get_code()
                                msg = ResponseStatus.BAD_LOG_ERROR.get_msg()
                                data['ev_bad_log'] = test_rules_structure['ev_rules_structure']
                            elif test_rules[key] is None and 'action' in key:
                                code = ResponseStatus.BAD_LOG_ERROR.get_code()
                                msg = ResponseStatus.BAD_LOG_ERROR.get_msg()
                                data['action_bad_log'] = test_rules_structure['action_rules_structure']
                            '''
                    # 没有出现bad case
                    if code == ResponseStatus.SUCCESS.get_code():
                        # 从数据库中取基础规则
                        # for local debug MysqlHandler:
                        # qa_mysql_handler = MysqlHandler("10.33.4.44", 3306, "herla_backend", "Qa_platform|8165",
                        #                                "qaplatform")
                        qa_mysql_handler = MysqlHandler("localhost", 3306, "root", "Qa_platform|8165",
                                                        "qaplatform")
                        base_pv_rules = qa_mysql_handler.get_all_obj(
                            "select rule from pingback_rules where scene_id = '" + scene_id + "' and rule_type='pv'",
                            "pingback_rules", "rule")
                        base_ev_rules = qa_mysql_handler.get_all_obj(
                            "select rule from pingback_rules where scene_id = '" + scene_id + "' and rule_type='ev'",
                            "pingback_rules", "rule")
                        base_action_rules = qa_mysql_handler.get_all_obj(
                            "select rule from pingback_rules where scene_id = '" + scene_id +
                            "' and rule_type='action'", "pingback_rules", "rule")
                        # 如果当前场景id没有基础规则，则将测试数据生成的规则存入规则数据库：
                        if len(base_pv_rules) == 0 and len(base_ev_rules) == 0 and len(base_action_rules) == 0:
                            for key in test_rules.keys():
                                if test_rules[key] is not None:
                                    rule_type = key.split('_')[0]
                                    for sub_key in test_rules[key].keys():
                                        if isinstance(test_rules[key][sub_key], int):
                                            base_rule = "{\"" + sub_key + "\":" + str(test_rules[key][sub_key]) + "}"
                                        else:
                                            base_rule = "{\"" + sub_key + "\":" + json.dumps(
                                                test_rules[key][sub_key]) + "}"
                                        if 'scm_' in sub_key:
                                            base_rule_structure = ""
                                        else:
                                            base_rule_structure = "{\"" + sub_key + "_structure\":" + json.dumps(
                                                test_rules_structure[key + "_structure"][sub_key + "_structure"]) + "}"
                                        qa_mysql_handler.insert("insert into pingback_rules "
                                                                "(scene_id,rule,rule_type,rule_structure) values('" +
                                                                scene_id + "','" + base_rule + "','" + rule_type +
                                                                "','" + base_rule_structure + "')")
                        # 当前场景id存在至少一类基础规则：
                        else:
                            # 获取全部基础规则
                            base_rules = {}
                            if len(base_pv_rules) > 0:
                                temp_pv = {}
                                for i in range(len(base_pv_rules)):
                                    for key, value in json.loads(base_pv_rules[i]['rule']).items():
                                        temp_pv[key] = value
                                base_rules['pv_rules'] = temp_pv
                            if len(base_ev_rules) > 0:
                                temp_ev = {}
                                for j in range(len(base_ev_rules)):
                                    for key, value in json.loads(base_ev_rules[j]['rule']).items():
                                        temp_ev[key] = value
                                base_rules['ev_rules'] = temp_ev
                            if len(base_action_rules) > 0:
                                temp_action = {}
                                for k in range(len(base_action_rules)):
                                    for key, value in json.loads(base_action_rules[k]['rule']).items():
                                        temp_action[key] = value
                                base_rules['action_rules'] = temp_action
                            # 如果基础规则与测试规则完全一致，返回成功
                            if base_rules == test_rules:
                                code = ResponseStatus.MATCH_SUCCESS.get_code()
                                msg = ResponseStatus.MATCH_SUCCESS.get_msg()
                            # 如果基础规则与测试规则不一致，调用get_log_difference，产生对比差异数据
                            else:
                                code = ResponseStatus.MATCH_FAILURE.get_code()
                                msg = ResponseStatus.MATCH_FAILURE.get_msg()
                                if 'pv_rules' in base_rules:
                                    data['pv_rules'] = log_handler.get_log_difference(base_rules['pv_rules'],
                                                                                      test_rules['pv_rules'])
                                    result_conclusion['pv_rules'] = result_conclude("result", data['pv_rules'],
                                                                                    'pv')['conclusion']
                                if 'ev_rules' in base_rules:
                                    data['ev_rules'] = log_handler.get_log_difference(base_rules['ev_rules'],
                                                                                      test_rules['ev_rules'])
                                    result_conclusion['ev_rules'] = result_conclude("result", data['ev_rules'],
                                                                                    'ev')['conclusion']
                                if 'action_rules' in base_rules:
                                    data['action_rules'] = log_handler.get_log_difference(base_rules['action_rules'],
                                                                                          test_rules['action_rules'])
                                    result_conclusion['action_rules'] = result_conclude("result", data['action_rules'],
                                                                                        'action')['conclusion']
                        test_rules_conclusion = result_conclude("test_rules", test_rules)
                    # 清理doris缓存
                    expire_time = json.loads(redis_value.replace('\'', '"'))['expire_time']
                    doris_props = json.dumps({'unique_value': unique_value, 'unique_key': unique_key,
                                              'scene_id': scene_id, 'expire_time': expire_time,
                                              'script_id': script_id}, separators=(',', ':'))
                    logging.info("doris_props is: " + doris_props)
                    doris_handler.delete("delete from dwd_shmm_group_test where props = '" + doris_props + "'")
                    # 清理redis缓存
                    redis_handler.remove_task(redis_key, redis_value)
        logging.info(json.dumps({
            "code": code,
            "msg": msg
        }))
        self.write({
            "code": code,
            "msg": msg,
            "data": data,
            "result_conclusion": result_conclusion,
            "test_rules_conclusion": test_rules_conclusion
        })
