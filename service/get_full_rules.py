# coding=utf-8
import json
from abc import ABC
from concurrent.futures.thread import ThreadPoolExecutor
import tornado.web
from tornado.concurrent import run_on_executor
from utils.log_handler import result_conclude
from utils.mysql_handler import MysqlHandler


class GetFullRules(tornado.web.RequestHandler, ABC):
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
        pv_rules = qa_mysql_handler.get_all_obj(
            "select rule from pingback_rules where scene_id = '" + scene_id + "' and rule_type='pv'",
            "pingback_rules", "rule")
        ev_rules = qa_mysql_handler.get_all_obj(
            "select rule from pingback_rules where scene_id = '" + scene_id + "' and rule_type='ev'",
            "pingback_rules", "rule")
        action_rules = qa_mysql_handler.get_all_obj(
            "select rule from pingback_rules where scene_id = '" + scene_id + "' and rule_type='action'",
            "pingback_rules", "rule")
        full_rules = {'pv_rules': None, 'ev_rules': None, 'action_rules': None}
        if len(pv_rules) > 0:
            temp_pv = {}
            for i in range(len(pv_rules)):
                for key, value in json.loads(pv_rules[i]['rule']).items():
                    temp_pv[key] = value
            full_rules['pv_rules'] = temp_pv
        if len(ev_rules) > 0:
            temp_ev = {}
            for j in range(len(ev_rules)):
                for key, value in json.loads(ev_rules[j]['rule']).items():
                    temp_ev[key] = value
            full_rules['ev_rules'] = temp_ev
        if len(action_rules) > 0:
            temp_action = {}
            for k in range(len(action_rules)):
                for key, value in json.loads(action_rules[k]['rule']).items():
                    temp_action[key] = value
            full_rules['action_rules'] = temp_action
        conclusion = result_conclude("test_rules", full_rules)
        self.write({
            "full_rules": full_rules,
            "conclusion": conclusion
        })
