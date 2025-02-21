"""
-*- coding: utf-8 -*-
@Time : 2023/3/3 
@Author : liuyan
@function : 
"""
import json

import jsonpath
from deepdiff import DeepDiff
from deepdiff.helper import CannotCompare
from operator import itemgetter


# deepdiff自定义对比函数，对比trackid一致的数据
def compare_func(x, y, level):
    try:
        return x['trackid'] == y['trackid']
    except Exception:
        raise CannotCompare() from None


def diff_func(base, file_name):
    # 获取base_file中的所有trackid
    base_trackids = jsonpath.jsonpath(base, '$..trackid')
    compare_list = []

    diff = {}
    unique_trackids = set()
    q = []

    # 一行行读取存储的对比url
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            url_dic = eval(line)
            compare_list.append(url_dic)
            trackid = url_dic['trackid']
            adstyle = url_dic['adstyle']
            q.append('{}：{}上报'.format(adstyle, url_dic['path']))
            if trackid not in unique_trackids:
                unique_trackids.add(trackid)
                if trackid in base_trackids:
                    index = base_trackids.index(trackid)
                    ddiff = DeepDiff(base[index], url_dic, exclude_regex_paths="\['encd'\]",
                                     verbose_level=1, iterable_compare_func=compare_func).to_json()
                    if not ddiff:
                        if 'params_changed' not in diff:
                            diff['params_changed'] = []
                        diff['params_changed'].append({'trackid': trackid, 'detailed_diff': json.loads(ddiff)})
            else:
                if 'repeat_trackid' not in diff:
                    diff['repeat_trackid'] = []
                template = ''
                vp = ''
                if 'template' in url_dic:
                    template = url_dic['template']
                if 'vp' in url_dic:
                    vp = url_dic['vp']
                diff['repeat_trackid'].append({'trackid': trackid, 'adstyle': adstyle, 'path': url_dic['path'],
                                               'vp': vp, 'template': template})

    for index, trackid in enumerate(base_trackids):
        if trackid not in unique_trackids:
            if 'omitted_trackid' not in diff:
                diff['omitted_trackid'] = []
            template = ''
            vp = ''
            if 'template' in base[index]:
                template = base[index]['template']
            if 'vp' in base[index]:
                vp = base[index]['vp']
            diff['omitted_trackid'].append(
                    {'trackid': trackid, 'adstyle': base[index]['adstyle'], 'path': base[index]['path'],
                     'vp': vp, 'template': template})

    return {'diff': diff, 'sorted_compare_list': sorted(compare_list, key=itemgetter('trackid')), 'report_queue': q}

# 验证功能
# base = [{'path': 'pvlog', 'vp': 's', 'p': 'oad1,oad2,oad3,oad4,oad5', 'adstyle': 'oad', 'al': '9790439', 'vid': '8281981', 'tvid': '411907916', 'plat': '6', 'sver': '9.8.00', 'adplat': '3', 'prot': 'vast', 'sdkVersion': 'tv8.4.73-track-SNAPSHOT', 'bt': '20230213', 'site': '1', 'encd': 'z4EeFDlyqwjciGjl84gEgmgS27ywRSciL9%2FBipl6JzBNAxCQ3CaDITpqkpXL2G1Bv4SOVo5rx7CAnONbCU7owIX4rH4smAlw5zStwxp%2B80pGiFMbapyJxlY1R1hvkwHR3IvwhseVomVtCqn3is%2BK8j55UiBKaLeyNZCEj1I5RQX1SduEDecXNprjYI3Oa2IlscRtO%2BMvECADPOi5gxy0sZKXy5cWxBQg7zWfGZFuZydYVRegbisNc57KSJVsjB3m5Sc7vPSREpKxkfH5IQx91Pi2udfc%2BGw4WcDbm2SmP5KwvdR9F%2BEKIfuiSrGh3BYJB8zKdnUnAkyQn0tNbgbU0LO%2BolOoen2fN7nKgdkcCdwEt2jT2ubu%2FmAMtJxr6ZlmjYTS1zu9F57I5n8RnrN0tZlrceOvEXToGLeUxQI8wEcyRAZURmG3gZiCuSY2ww%2Bh67mAs1tr41UeFuCAfxQymQaRqWUgwI9fmBkufK8RS%2B3JzMdI0L23kgSnwUSivvITMwIwBf6KIJCrIRSvDDqInf3LDXYlu0vAW8vTkBodbs8BYk18UtidcrPTJI6eGOM89o5bzlzMyINQ%2BIUJGKVsBMRY17MpFPgJZWufNxoTCxpUr3yOiKDTZnCYQrEgzGFM48DiZ%2FfIN3Yer7%2FNO7W3C2W4RrQyifWr2CkfDtZZeRGaRKZNYCbzbFgS8%2B8fNEEqfAethQz8hqrjCfq6r1XZxDO2Y4wnIhA%2BO1InbEfcV%2BA4So5tPHmI7re0MGMrB5N5Zxt1ONElrpG44N46QelMj3g8Sbj8m3mj7szOz4qjk%2B%2FFSbM8HZatT5y1xUp%2F%2BipSFWQHWI4cq7tqodTZqu22lwPpvAcVQtNSV0jVJWzF7f50rD9BTOtDAGiIndWSb0wLrlJ%2F9SSxqzHyK%2B0F3bwytUvHmw3ZJEktgki77H5gaoGOwKZmqC%2F28gBEknvJL8TKaJnLAsTq1tgLe0%2BQK9g7%2FM%2BSB2Lz502Aym9wHkVLkvB4JRn2SXGWG1H9KWFM2UguQpjmJWbVWsRAXR5srAvjHg%3D%3D', 'trackid': 'd5e8a5b6-a358-49cd-9923-2f2394d830c3'}, {'path': 'pvlog', 'p': 'oad1,oad2,oad3,oad4,oad5', 'adstyle': 'oad', 'al': '9790439', 'vid': '8281979', 'tvid': '411907917', 'plat': '6', 'sver': '9.8.00', 'adplat': '3', 'prot': 'vast', 'sdkVersion': 'tv8.4.73-track-SNAPSHOT', 'bt': '20230213', 'site': '1', 'encd': 'sxVoZEG%2BjK3m3xJk3OPDzgdilY9kA9hCtrXPYB1UMPEIzlDULUSaVwC%2Bo%2F1t6%2B7b%2FkwIr9RtSq2aCoN%2FvGTcsmX8trSXdRo5EB7hM%2B4TxzqDPlXQQHTdh%2FAOqkXR2YOf5VfHK1DAonddzw0vbBDC6RgP3YWqrKkhQkGdRmxwOTRbyeP7e0iwC7nPVgPEfEJ9AaJlVSDvGS0N%2FSLiIJekoNnODnIzV86NAgJkcySCTdEHXkLd6jUBjjwYaxQoktJa7zhuKHqt%2FFAQkGDhiHj%2F2VYIrE82DJpvzMgfKZ2L9UJbOI73qt4Ork6g1QGXfRUnn%2FuFHdTCdXKJJGM7qik%2FJPu8A805RS01ok0rt77mpV5ljm9LNSvXWKnaS3z6cyCY0Bxb32qSGct%2BrAW1gxdvri8F7mCaid%2Fl6HjPu1vMzeYquWu93llzYALMtGgxDQY%2FDc1hFOmmpc2V48T4YMjPn8B%2BztFoA03RelhR8rqNMFuE%2BhLKouZPxLdwkPZDS94nvoABWKAa7IuXv4uVqONCOMRCPoSCZJHWOnaPBhkXfraSlnC2qRyJdU8Je%2BoI9Gv4HXTBLUP1vB2zKJ86qwT09PMbkbsTe9yE%2B0kiy6FNG8Gh7TlA1ks244rZldLjmQH1LOhNTBAhgIsxCJdB1dgk4vdWv96dBL%2F7f%2FYPvyCEp4nWmbaF%2F5wurVIXqe8JnBg5o%2BorWPrBUfKZXPrKFOxmK3BbJrfycNQnPh6SXJMHKOSgUW09gOZv%2FafhbIHc8Ju2plNWXq7i8iOtL7FehfASk2Yo62Ea2OjS0rJTX2vYL1NcXZ3HZs%2FHJIVRmauWWeM1SFyjlx586D26M3iuD5bUoZI7tpWpZlLkFSGfczV9AHtLPFF9nUMH3k6TPzdczppQ9L3VglWQb85pVHSxPFI%2F%2FvaP934yp7erUX0vhvVhSM0%2F00QtOKV%2FcL7I2iONyDJU5k703CcZ4YR5dXdGlXNOmRkgyqJ18SAyumPbVIIGPu%2F8UNhouyEbxYUSW3iy5rhe5COL%2FqLy%2BY%2BH98lRNDAyZQ%3D%3D', 'trackid': 'f4f2bb00-b1a8-4e66-8800-a20a4d553a72'}, {'path': 'pvlog', 'vp': 's', 'p': 'op', 'posid': 'op_aphone_1', 'adstyle': 'oad', 'plat': '6', 'sver': '9.8.00', 'adplat': '3', 'prot': 'json', 'sdkVersion': 'tv8.4.73-track-SNAPSHOT', 'bt': '20230213', 'encd': '1%2FsvMs0xnRvTyWWkrOQYVfRz9GALdoJ9NVdkNU99aShsNchfvwdIv89PgupfE3C6mQsRX9aWCqsW%2BFZCzs9iTeAfrYeZkrPXRdOgJEbutRfzOF1OCcZkw12z5vEzjc4dpyq5wB4gLgQ4Ctzk46loif97j%2F6nmk%2FVWKlki2n%2F8HSmvBv58b9NUJHEiCrlyTsrWh0%2B3vwE2NbN5%2B10Qs3m5i09HGLsJlBbb5nzlgo03cxVq6zJTrY7bmDbxha7JalU1a9dDLer36CLcnXCAr2psAMT4f422wWeinxid09kwXlADNtDCY59oBZGalYhFx0QYOnLGE4GEJXOumv7YcXjiidlz%2BkHcefP5jkRUHFRAaV91W6bGq41RCixcxbzyWkoWtEQ%2FELXcT10j32SND8HRQHiz3KOYtUTgjMHqIDnRYsaqN9KG%2Fuqke0pcXt%2FBFJtawPB%2FFrl5S0uBFx3xarV%2BdN2Wda5572zyth6Xh3Y3Sj7vNU7z7osMpASH5eW%2Bk80igpIO5fZkm9SPMlGPxM8Vmxpj5RSq2UfU8Z4%2FqpFYFPbehwZLt9lvVVEOAvyDHhe5iV0l62nJUgRNASsUGITUdiY33MpAA%2Fev%2BlZuYlHgVKL9shMOJ45FbCch9zrTBvJNtdc4XO7%2Fg9z0LIJ%2F0akbfYUEekis5KvfZv9PQOHel4CtmvvSSp4Dz9GV%2Fcg2aYZMq45IteQIst8AqYxVuKmooAfvkVdnPg59xi56dipRXvzcaGNCPD5DgDFHPoM8qf6B0zk8Xwu4JYsXdbwzZxyxV8B6mbnmdxHyEOMaLo41k%2BtGeQIDtjjLBYYitQIx1EziXNh5s6iXgR2dkzUlgbWtceKfsKQ6Xjnb%2BrEoEOucOmg0Ck4QpQ4fLT8pmkP2Tb9q8vxE1zbNhEnLRizcAbvQ6rd5BKxSHr4MMg%2BbydhvH9gLlm4RKy91gaEudWzQMvElj2lZmRRzsB5lQ%2FJrbpDReHha2WZfMw2fGav%2FySjaHd4WYo0C61IzBf4XcnEP5fLenHNm3rC3byzexPFTGB2DA%3D%3D', 'displayType': '0', 'trackid': 'ac73e619-b332-46bf-b8a9-086672afc8fd'}, {'path': 'pvlog', 'vp': 's', 'p': 'op', 'posid': 'op_aphone_1', 'adstyle': 'oad', 'plat': '6', 'sver': '9.8.00', 'adplat': '3', 'prot': 'json', 'sdkVersion': 'tv8.4.73-track-SNAPSHOT', 'bt': '20230213', 'encd': 'L2V5XzafErWweJfFVK2TbO2%2BZztjjncbS%2BlGvX3zJbVBPGxA5A632IAzWzPVvgPlLGIrTp5SZ0u%2FvrznWOgzgcMWBDo6t47MMGF88dfJeOssocllroVRMScHSTiUd1N5qnJCGmgC4Nh4r8eQWykp1WQYy7HHSXEkEwOVMuTE1nyzV4Dg6Yh4fjy5LjWg7Z8W5C%2Fd3OCIR9li34VXa2HfzHNVCd50r5XervgElGSZsSmw6%2F5rXoQkAnZNvV%2FQzX2a0rYtQs1g1e7o9p83xgAYC0Zmc%2F82nP%2Bi4ehoW9iN1bGzC2iAS9DIIkn8Tunppot9zCmDVT%2B81hGnfNiLZVKQ2BWyiHHr5Jh67b3YOgmbZv%2BmgY0pkYhTlboJAEUGpbzn8DFPhNDNfDgF%2FpOf6TseNMGeHK3t6KpFU%2B1G4vomSxVCAq1w4sBYqE%2BU7%2FrUp9WUhxsWhMHDlRS1RQg2pTMZhGoWXcg2YgvVs6BX6pyaqYFssQRMtT5DC2VfnDOzDXZF2KjLvEsKniQq04CN3I5Oa4uO1ffrhSbv0rRryAfHHiav3BdU5F1JT1Bs1wotqtpibc%2FigLvsUDbYKgDdBTzylDu01U6fUw0wJcXOdUpyknuu4HdXJKd0Rnm5HuPZlMUzrNUoZYe2PFlm9Huf2sQV3Ni85nQYY%2FnVbCw%2BG7oe1g9Ai%2B4RWRx0m%2FlQrR4TA6Ylc%2BU6YwGKjlQuZ60RxmPIUx98PVNUkjN5Rm9QUy%2BCFlXAvtPuV8%2FFAm7Ei40BHZ3WxbOJY4HV4snKF1I8VTuhcIAfGWmageqh%2FFbB0iVBND4wOGkZg%2FRfuI%2Fj%2F38OES5gGk%2B6It5dV%2BAAEIkwVmYruMSUGOmA%2BAguJGezHvHhAI%2Ftba%2BNdBJZEC%2By8VmSeN5kLYJmR8r%2Fbo7F0rzlLyQxxEfEZ2jaw%2FO7H5aXguHPBTR58Mi6WRhN13kfO3IHEmWrM1N1C9XPfyEakp0hkyR17LXb9hHtYKd1lXSrTdJZmWv77gtx3pjyKsiDckkzQgGdJRxWrDj%2BP6Lf5SgWhmDzUg%3D%3D', 'displayType': '0', 'trackid': '4fdb0345-c599-4c3f-af57-760c8cce0e31'}]
# file_name = '/Users/liuyan/Desktop/跟git杠上/pingback_service/compare_file/iOS_5A0F443F-8044-4987-A636-F7863BC810F0_create.txt'
#
# print(diff_func(base, file_name))