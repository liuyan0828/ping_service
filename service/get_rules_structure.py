# coding=utf-8
import json
import tornado.web
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from utils.mysql_handler import MysqlHandler


class GetRuleStructures(tornado.web.RequestHandler, ABC):
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
        pv_rule_structures = qa_mysql_handler.get_all_obj(
            "select rule_structure from pingback_rules where scene_id = '" + scene_id + "' and rule_type='pv'",
            "pingback_rules", "rule_structure")
        ev_rule_structure = qa_mysql_handler.get_all_obj(
            "select rule_structure from pingback_rules where scene_id = '" + scene_id + "' and rule_type='ev'",
            "pingback_rules", "rule_structure")
        action_rule_structure = qa_mysql_handler.get_all_obj(
            "select rule_structure from pingback_rules where scene_id = '" + scene_id + "' and rule_type='action'",
            "pingback_rules", "rule_structure")
        rule_structure = {'pv_rules_structure': None, 'ev_rules_structure': None, 'action_rules_structure': None}
        if len(pv_rule_structures) > 0:
            temp_pv = {}
            for i in range(len(pv_rule_structures)):
                for key, value in json.loads(pv_rule_structures[i]['rule_structure']).items():
                    temp_pv[key] = value
            rule_structure['pv_rules_structure'] = temp_pv
        if len(ev_rule_structure) > 0:
            temp_ev = {}
            for j in range(len(ev_rule_structure)):
                for key, value in json.loads(ev_rule_structure[j]['rule_structure']).items():
                    temp_ev[key] = value
            rule_structure['ev_rules_structure'] = temp_ev
        if len(action_rule_structure) > 0:
            temp_action = {}
            for k in range(len(action_rule_structure)):
                for key, value in json.loads(action_rule_structure[k]['rule_structure']).items():
                    temp_action[key] = value
            rule_structure['action_rules_structure'] = temp_action
        self.write(
            rule_structure
        )
