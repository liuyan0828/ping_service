import tornado.ioloop
import tornado.web
from py_eureka_client import eureka_client
from tornado.options import define, options
from debug_service.clean_redis import CleanRedis
from debug_service.get_doris import GetDoris
from debug_service.delete_doris import DeleteDoris
from debug_service.get_redis import GetRedis
from service.adsdk_compare import AdSdkCompare
from service.adsdk_delete_rule import AdSdkDeleteRule
from service.adsdk_get_rules import AdSdkGetRules
from service.delete_rules import DeleteRules
from service.get_full_rules import GetFullRules
from service.get_rules_structure import GetRuleStructures
from service.get_scene import GetScenes
from task_service.jenkins_trigger import JenkinsTrigger, JenkinsStatus
from service.pingback_task import PingBackTask
from service.adsdk_checking import AdSdkChecking
from service.adsdk_record import ReportAPI
from task_service.update_miniapp_qrcode import UpdateMiniappQrcode
from task_service.upload_cpp_covr import UploadCppCovr

tornado.options.parse_command_line()


def make_app():
    return tornado.web.Application([
        (r"/qa_service/pingback_task", PingBackTask),
        (r"/qa_service/get_scenes", GetScenes),
        (r"/qa_service/get_full_rules", GetFullRules),
        (r"/qa_service/get_rule_structures", GetRuleStructures),
        (r"/qa_service/delete_rules", DeleteRules),
        (r"/qa_service/debug/get_doris", GetDoris),
        (r"/qa_service/debug/delete_doris", DeleteDoris),
        (r"/qa_service/debug/get_redis", GetRedis),
        (r"/qa_service/debug/clean_redis", CleanRedis),
        (r"/qa_service/ad_sdk/compare", AdSdkCompare),
        (r"/qa_service/ad_sdk/get_rules", AdSdkGetRules),
        (r"/qa_service/ad_sdk/delete_rule", AdSdkDeleteRule),
        (r"/qa_service/ad_sdk/checking", AdSdkChecking),
        (r"/qa_service/task/jenkins_trigger", JenkinsTrigger),
        (r"/qa_service/task/jenkins_status", JenkinsStatus),
        (r"/qa_service/task/upload_cpp_covr", UploadCppCovr),
        (r"/qa_service/task/update_miniapp_qrcode", UpdateMiniappQrcode),
        (r"/qa_service/ad_pingback/goto", ReportAPI),
        (r"/qa_service/ad_pingback/av", ReportAPI),
        (r"/qa_service/ad_pingback/pv", ReportAPI),
        (r"/qa_service/ad_pingback/pvlog", ReportAPI),


    ])


if __name__ == "__main__":
    eureka_client.init(eureka_server='http://10.33.4.44:17100/eureka/',
                       eureka_basic_auth_user='sonic',
                       eureka_basic_auth_password='sonic',
                       app_name='qa_pingback_service',
                       instance_host="10.33.4.44",
                       instance_port=8813)
    app = make_app()
    app.listen(8813)
    url = ""
    tornado.ioloop.IOLoop.current().start()
