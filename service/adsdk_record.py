"""
-*- coding: utf-8 -*-
@Time : 2023/2/1 
@Author : liuyan
@function : 
"""
# coding=utf-8
import json
import logging
import tornado.web
import time
import base64
import os
from urllib.parse import unquote
from enum import Enum, unique
from concurrent.futures.thread import ThreadPoolExecutor
from abc import ABC
from tornado.concurrent import run_on_executor
from service.adsdk_checking import FilePath
from utils.Xxtea_handler import Xxtea


@unique
class ResponseStatus(Enum):
    SUCCESS = {"A00000": "Success!"}
    FILE_NOT_EXIST = {"B00001": "The original file is not exist,please start the task first"}
    DECRYPT_FAIL = {"B00002": "The encd param is not successfully decrypted, please try again"}
    FILE_ERROR = {"B00003": "Write failed!"}

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


class ReportAPI(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(max_workers=30)

    @tornado.web.gen.coroutine
    def get(self):
        post_data = {}
        for key in self.request.arguments:
            post_data[key] = str(self.get_arguments(key)[0])
        # logging.info("Request parameter is: " + str(post_data))
        plat = self.get_argument("plat", '')
        sver = self.get_argument("sver", '')
        vp = self.get_argument("vp", '')
        adstyle = self.get_argument("adstyle", '')
        p = self.get_argument("p", '')
        posid = self.get_argument("posid", '')
        encd = self.get_argument("encd", '')
        ac = self.get_argument("ac", '')
        ad = self.get_argument("ad", '')
        pt = self.get_argument("pt", '')
        b = self.get_argument("b", '')
        bk = self.get_argument("bk", '')
        instream = self.get_argument("instream", '')
        eventtype = self.get_argument("eventtype", '')
        err = self.get_argument("err", '')
        ead = self.get_argument("ead", '')
        event = self.get_argument("event", '')
        al = self.get_argument("al", '')
        vid = self.get_argument("vid", '')
        tvid = self.get_argument("tvid", '')
        site = self.get_argument("site", '')
        prot = self.get_argument("prot", '')
        sdkVersion = self.get_argument("sdkVersion", '')
        bt = self.get_argument("bt", '')
        template = self.get_argument("template", '')
        adplat = self.get_argument("adplat", '')
        displayType = self.get_argument("displayType", '')
        trackid = self.get_argument("trackid", '')
        yield self.run(plat, sver, vp, adstyle, p, posid, encd, ac, ad, pt, b, bk, instream, eventtype, err, ead, event,
                       al, vid, tvid, site, prot, sdkVersion, bt, template, adplat, displayType, trackid)
        self.set_header("Content-Type", "application/json")

    @run_on_executor
    def run(self, plat, sver, vp, adstyle, p, posid, encd, ac, ad, pt, b, bk, instream, eventtype, err, ead, event, al,
            vid, tvid, site, prot, sdkVersion, bt, template, adplat, displayType, trackid):
        path = self.request.path.strip('/')
        param_list = {'path':path, 'plat': plat, 'sver': sver, 'vp': vp, 'adstyle': adstyle, 'p': p, 'posid': posid, 'ac': ac,
                                'ad': ad, 'pt': pt, 'b': b, 'bk': bk, 'instream': instream, 'eventtype': eventtype, 'err': err, 'ead': ead,
                                'event': event, 'al': al, 'vid': vid, 'tvid': tvid, 'site': site, 'prot': prot, 'sdkVersion': sdkVersion,
                                'bt': bt, 'template': template, 'adplat': adplat, 'displayType': displayType, 'trackid': trackid}
        # 过滤值为空的参数
        param_dict = dict(filter(lambda item: item[1] != '', param_list.items()))
        # 获取该设备的platform
        platform = ''
        if plat == '3':
            platform = 'iOS'
        elif plat == '6':
            platform = 'Android'
        # 反转义encd
        r_encd = unquote(unquote(encd))
        # 解密encd
        try:
            res = bytes(r_encd.encode())
            xxtea = Xxtea()
            k = u"Adp201609203059Y"
            key = k.encode("ascii")
            # data = str(xxtea.decrypt(base64.b64decode(res), key).decode()).split('&')
            # try to fix AttributeError: 'str' object has no attribute 'decode'
            data = str(xxtea.decrypt(base64.b64decode(res), key)).split('&')
        except Exception as e:
            code = ResponseStatus.DECRYPT_FAIL.get_code()
            msg = ResponseStatus.DECRYPT_FAIL.get_msg()
            raise Exception("转换失败：{}".format(e))
        # 取设备的唯一标识 分端取
        if platform == 'iOS':
            for s in data:
                if s.find('deviceid=') != -1:
                    device_id = s[9:]
        elif platform == 'Android':
            for s in data:
                if s.find('AndroidID=') != -1:
                    device_id = s[10:]
        base_file_dir = FilePath().get_file_path()
        file_name = base_file_dir + '/' + platform + '_' + device_id + '_create.txt'
        if not os.path.exists(file_name):
            # logging.info("file_name is: " + file_name)
            code = ResponseStatus.FILE_NOT_EXIST.get_code()
            msg = ResponseStatus.FILE_NOT_EXIST.get_msg()
        else:
            try:
                with open(file_name, 'a') as file:
                    file.write(str(param_dict))
                    file.write('\n')
                code = ResponseStatus.SUCCESS.get_code()
                msg = ResponseStatus.SUCCESS.get_msg()
            except Exception:
                code = ResponseStatus.FILE_ERROR.get_code()
                msg = ResponseStatus.FILE_ERROR.get_msg()
        self.write({
            "code": code,
            "msg": msg,
            "data": data,
        })
