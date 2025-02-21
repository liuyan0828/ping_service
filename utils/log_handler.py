import json
from functools import reduce


def generate_base_rules(project, ping_back_log):
    """
    生成规则的函数，基于pingback日志生成规则

    Args:
        project (Project): 项目
        ping_back_log (list): pingback日志列表

    Returns:
        (dict, dict): 规则字典和规则结构字典

    """
    rules, rules_structure = {}, {}
    pv_log_list, ev_log_list, action_log_list = [], [], []
    for log in ping_back_log:
        log_type = log.get('track_type')
        if log_type == 'PV':
            pv_log_list.append(json.loads(log.get('log')))
        elif log_type == 'EV':
            ev_log_list.append(json.loads(log.get('log')))
        elif log_type == 'ACTION':
            # print(log.get('log'))
            action_log_list.append(json.loads(log.get('log')))
    rules['pv_rules'], rules_structure['pv_rules_structure'] = \
        generate_pv_base_rules(project, pv_log_list) if pv_log_list else (None, None)
    rules['ev_rules'], rules_structure['ev_rules_structure'] = \
        generate_ev_base_rules(project, ev_log_list) if ev_log_list else (None, None)
    rules['action_rules'], rules_structure['action_rules_structure'] = \
        generate_action_base_rules(project, action_log_list) if action_log_list else (None, None)
    return rules, rules_structure


def get_spm_code(spm_code, scope, start=0):
    """
    用于获取SPM码的函数

    Args:
        spm_code (str): SPM码字符串
        scope (int): 需要获取的SPM码的位数
        start (int): SPM码的起始位置

    Returns:
        (str): 获取到的SPM码

    """
    spm_result = spm_code
    if '.' in spm_code:
        code_list = spm_code.split('.')
        spm_result = '.'.join(code_list[start:(start + scope)])
    elif spm_code == '':
        spm_result = 'empty'
    return spm_result


def is_list_series(target_list):
    # AI优化版本，认为更简洁和易读，但也承认使用all()函数遍历会增加响应时长，但认为可忽略不计。
    return all(target_list[i] == target_list[i - 1] + 1 for i in range(1, len(target_list)))


def is_list_series_old(target_list):
    """
    判断一个列表是否是连续的数字序列
    :param target_list: 待判断的列表
    :return: 如果这个列表是连续的数字序列，返回True，否则返回False
    """
    for i in range(1, len(target_list)):
        if target_list[i] == target_list[i - 1] + 1:
            pass
        else:
            return False
    return True


def json_get_keys(ori_dict, result_list):
    # res为传入的json数据，循序找出每一个key
    for item in ori_dict:
        # print(type(res[str(item)]).__name__ == 'dict')
        # 如果这个key下对应的数据类型为dic，进入递归，如res["data"]，当循环到这个枚举值时候，就是进入了嵌套字典。
        if type(ori_dict[str(item)]).__name__ == 'dict':
            json_get_keys(ori_dict[str(item)], result_list)
        # 如果这个key下对应的数据类型为list，进入循序，如res["data"]["details"]，当循环到这个枚举值时候，就是进入了data下面的list中，我们用range来循换这个list，取出每一个list下面的元素，再自身调用递归。
        if type(ori_dict[str(item)]).__name__ == 'list' and type(ori_dict[str(item)][0]).__name__ == "dict":
            for i in range(len(ori_dict[str(item)])):
                json_get_keys(ori_dict[str(item)][i], result_list)
        # 众所周知，递归隐式的维护了一个栈，此时走到递归最下层，将结果append到result中。
        result_list.append(str(item))
    return result_list


def generate_pv_base_rules(platform, pv_list):
    """
    生成PV规则的函数，基于PV日志生成规则

    Args:
        platform (str): 平台
        pv_list (list): PV日志列表

    Returns:
        (dict, dict): 规则字典和规则结构字典

    """
    pv_base_rules, pv_base_rule_structure = {}, {}
    # 增加字段记录是否有基础规则出错及详细错误
    have_bad_log = False
    bad_log = {}
    for i in range(len(pv_list)):
        # 进行一些基础的key是否存在，value是否可解析的校验
        try:
            rules_structure_list = []
            # 获取spm_pre和spm_cnt的a、b码
            if platform == 'PC' or platform == 'Wap':
                spm_pre = get_spm_code(pv_list[i]['spmPre'], scope=3)
                spm_cnt = get_spm_code(pv_list[i]['spmCnt'], scope=3)
                scm_pre = pv_list[i]['scmCnt']
                if scm_pre[0] == '1':
                    scm_pre = 'have'
                else:
                    scm_pre = get_spm_code(scm_pre, scope=2)
                if pv_list[i]['vstCookie'] == '':
                    raise ValueError("vstCookie(SUV) is empty...")
                if spm_cnt == pv_list[i]['spmCnt'] or spm_cnt == 'empty':
                    raise ValueError("spm_cnt is empty or can not be parsed...")
            elif platform == 'miniapp':
                try:
                    spm_pre = get_spm_code(pv_list[i]['pv_modules']['spm_pre'], scope=3)
                except KeyError:
                    spm_pre = 'empty'
                try:
                    scm_pre = pv_list[i]['pv_modules']['scm_pre']
                except KeyError:
                    scm_pre = ''
                spm_cnt = get_spm_code(pv_list[i]['pv_modules']['spm_cnt'], scope=3)
                if spm_cnt == pv_list[i]['pv_modules']['spm_cnt'] or spm_cnt == 'empty':
                    raise ValueError("spm_cnt is empty or can not be parsed...")
            # 埋点信息数据汇总
            if spm_pre + '->' + spm_cnt in pv_base_rules.keys():
                # 如果该路径规则存在，则该路径出现次数+1
                pv_base_rules[spm_pre + '->' + spm_cnt] = pv_base_rules[spm_pre + '->' + spm_cnt] + 1
            else:
                # 如果该路径规则不用存在，则该路径加入到规则字典
                pv_base_rules[spm_pre + '->' + spm_cnt] = 1
                # 获取该路径规则所包含的字段，用于后续验证
                pv_base_rules[spm_pre + '->' + spm_cnt + '-scm_pre'] = scm_pre
                pv_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                    json_get_keys(pv_list[i], rules_structure_list)
        except (KeyError, ValueError):
            # 说明日志存在不可解析的状况，将标识置为true，并将不能解析的完整日志加入返回结果
            have_bad_log = True
            bad_log['pv_' + str(i)] = pv_list[i]
    if have_bad_log is True:
        return None, bad_log
    else:
        return pv_base_rules, pv_base_rule_structure


def generate_ev_base_rules(platform, ev_list):
    """
    生成EV规则的函数，基于EV日志生成规则

    Args:
        platform (str): 平台
        ev_list (list): EV日志列表

    Returns:
        (dict, dict): 规则字典和规则结构字典

    """
    ev_temp_rules, ev_base_rules, ev_base_rule_structure = {}, {}, {}
    # 增加字段记录是否有基础规则出错及详细错误
    have_bad_log = False
    bad_log = {}
    for i in range(len(ev_list)):
        # 进行一些基础的key是否存在，value是否可解析的校验
        try:
            rules_structure_list = []
            if platform == 'PC' or platform == 'Wap':
                spm_pre = get_spm_code(ev_list[i]['evArgumentLst']['spmPre'], scope=3)
                spm_cnt = get_spm_code(ev_list[i]['evArgumentLst']['spmCnt'], scope=3)
                spm_cnt_d = get_spm_code(ev_list[i]['evArgumentLst']['spmCnt'], start=3, scope=1)
                scm_cnt = ev_list[i]['evArgumentLst']['scmCnt']
                if scm_cnt[0] == '1':
                    scm_cnt = 'have'
                else:
                    scm_cnt = get_spm_code(scm_cnt, scope=2)
                if ev_list[i]['vstCookie'] == '':
                    raise ValueError("vstCookie(SUV) is empty...")
                if spm_cnt == ev_list[i]['evArgumentLst']['spmCnt'] or spm_cnt == 'empty':
                    raise ValueError("spm_cnt is empty or can not be parsed...")
            elif platform == 'miniapp':
                try:
                    spm_pre = get_spm_code(ev_list[i]['exp_info']['spm_pre'], scope=3)
                except KeyError:
                    spm_pre = 'empty'
                try:
                    scm_cnt = ev_list[i]['pv_modules']['scm_cnt']
                except KeyError:
                    scm_cnt = ''
                spm_cnt = get_spm_code(ev_list[i]['exp_info']['spm_cnt'], scope=3)
                spm_cnt_d = int(get_spm_code(ev_list[i]['exp_info']['spm_cnt'], start=3, scope=1))
                if ev_list[i]['device_info']['SUV'] == '':
                    raise ValueError
                if spm_cnt == ev_list[i]['exp_info']['spm_cnt'] or spm_cnt == 'empty':
                    raise ValueError("spm_cnt is empty or can not be parsed...")
            # 埋点信息数据汇总
            if spm_pre + '->' + spm_cnt in ev_temp_rules.keys():
                ev_temp_rules[spm_pre + '->' + spm_cnt].append(spm_cnt_d)
                ev_temp_rules[spm_pre + '->' + spm_cnt] = sorted(ev_temp_rules[spm_pre + '->' + spm_cnt])
            else:
                ev_temp_rules[spm_pre + '->' + spm_cnt + '-scm_cnt'] = scm_cnt
                ev_temp_rules[spm_pre + '->' + spm_cnt] = [spm_cnt_d]
                ev_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                    json_get_keys(ev_list[i], rules_structure_list)
        except (KeyError, ValueError):
            have_bad_log = True
            bad_log['ev_' + str(i)] = ev_list[i]
    # 判断d码出现多少次，是否连续
    if have_bad_log is False:
        for key1 in ev_temp_rules.keys():
            sub_value = {}
            if '-scm_cnt' in key1:
                ev_base_rules[key1] = ev_temp_rules[key1]
                # scm_cnt存在包含suv情况，需添加截取策略
            else:
                for i in range(len(set(ev_temp_rules[key1]))):
                    count = ev_temp_rules[key1].count(list(set(ev_temp_rules[key1]))[i])
                    if str(count) not in sub_value.keys():
                        sub_value[str(count)] = [list(set(ev_temp_rules[key1]))[i]]
                    else:
                        sub_value[str(count)].append(list(set(ev_temp_rules[key1]))[i])
                for key2 in list(sub_value.keys()):
                    if platform == 'PC' or platform == 'Wap':
                        pass
                        sub_value[key2] = sorted(list(set(sub_value[key2])))
                    else:
                        if len(sub_value[key2]) > 1:
                            if is_list_series(sub_value[key2]):
                                sub_value[str(key2) + '_is__series'] = True
                            else:
                                sub_value[str(key2) + '_is__series'] = False
                        else:
                            sub_value[str(key2) + '_is__series'] = True
                        sub_value[key2] = sorted(list(set(sub_value[key2])))
                ev_base_rules[key1] = sub_value
        return ev_base_rules, ev_base_rule_structure
    else:
        return None, bad_log


def generate_action_base_rules(platform, action_list):
    """
    生成ACTION规则的函数，基于ACTION日志生成规则

    Args:
        platform (str): 平台
        action_list (list): ACTION日志列表

    Returns:
        (dict, dict): 规则字典和规则结构字典

    """
    action_base_rules, action_base_rule_structure = {}, {}
    # 增加字段记录是否有基础规则出错及详细错误
    have_bad_log = False
    bad_log = {}
    for i in range(len(action_list)):
        # 进行一些基础的key是否存在，value是否可解析的校验
        try:
            rules_structure_list = []
            if platform == 'PC' or platform == 'Wap':
                spm_cnt = get_spm_code(action_list[i]['spmCnt'], scope=3)
                a_code = action_list[i]['acode']
                if action_list[i]['vstCookie'] == '':
                    raise ValueError("vstCookie(SUV) is empty...")
            elif platform == 'miniapp':
                spm_cnt = get_spm_code(action_list[i]['action_info']['spm_cnt'], scope=3)
                a_code = action_list[i]['action_info']['acode']
            # 埋点信息数据汇总
            if spm_cnt + '->' + a_code in action_base_rules.keys():
                action_base_rules[spm_cnt + '->' + a_code] = action_base_rules[spm_cnt + '->' + a_code] + 1
            else:
                action_base_rules[spm_cnt + '->' + a_code] = 1
                action_base_rule_structure[spm_cnt + '->' + a_code + '_structure'] = \
                    json_get_keys(action_list[i], rules_structure_list)
        except (KeyError, ValueError):
            have_bad_log = True
            bad_log['action_' + str(i)] = action_list[i]
    if have_bad_log is True:
        return None, bad_log
    else:
        return action_base_rules, action_base_rule_structure


def ad_log_match(base_log_list, test_log_list):
    verbose_info = {}
    warning_list = []
    for i in range(0, len(test_log_list)):
        if 'st' in test_log_list[i] or 'params' in test_log_list[i]:
            try:
                del test_log_list[i]['st']
                del test_log_list[i]['params']
            except KeyError:
                pass
        if test_log_list[i]['className'] + '-' + test_log_list[i]['method'] in verbose_info:
            verbose_info[test_log_list[i]['className'] + '-' + test_log_list[i]['method']] = \
                verbose_info[test_log_list[i]['className'] + '-' + test_log_list[i]['method']] + 1
        else:
            verbose_info[test_log_list[i]['className'] + '-' + test_log_list[i]['method']] = 1
    for i in range(0, len(base_log_list)):
        if 'st' in base_log_list[i] or 'params' in base_log_list[i]:
            try:
                del base_log_list[i]['st']
                del base_log_list[i]['params']
            except KeyError:
                pass
        if base_log_list[i] in test_log_list or base_log_list[i] in warning_list:
            pass
        else:
            warning_list.append(base_log_list[i])
    return {'warning_list': warning_list, 'verbose_info': verbose_info}


def remove_list_dict_duplicate(list_dict_data):
    return reduce(lambda x, y: x if y in x else x + [y], [[], ] + list_dict_data)


def get_log_difference(base_pingback_log, test_pingback_log):
    different_data = {}
    update_key = set(base_pingback_log).intersection(set(test_pingback_log))
    absence_key = set(base_pingback_log).difference(set(test_pingback_log))
    additional_key = set(test_pingback_log).difference(set(base_pingback_log))
    for key in update_key:
        if base_pingback_log[key] != test_pingback_log[key]:
            different_data[key] = {}
            different_data[key]["base_value"] = base_pingback_log[key]
            different_data[key]["test_value"] = test_pingback_log[key]
    for key in absence_key:
        different_data[key] = {}
        different_data[key]["only_base"] = base_pingback_log[key]
    for key in additional_key:
        different_data[key] = {}
        different_data[key]["only_test"] = test_pingback_log[key]
    return different_data


def result_conclude(data_type, data, pingback_type=''):
    # 处理测试埋点汇总
    if data_type == "test_rules":
        conclusion = {}
        for key in data:
            if "pv_" in key and data[key] is not None:
                conclusion['pv_rules'] = []
                # pv_rules结点下各key为xxx->xxx，表示一条规则
                for rule_key in data[key]:
                    # key中包含-scm_pre表示一条scm日志，无需做处理
                    if "-scm_pre" not in rule_key:
                        item = "由 " + rule_key.split('->')[0] + " 到 " + rule_key.split('->')[1] + " 的PV，上报：" + \
                               str(data[key][rule_key]) + "次"
                        # 处理该key的推荐信息，即key-scm_pre这个key的数据
                        if data[key][rule_key + "-scm_pre"] != "" and data[key][rule_key + "-scm_pre"] != "empty":
                            item = item + "，推荐来源为：" + data[key][rule_key + "-scm_pre"]
                        else:
                            pass
                        conclusion['pv_rules'].append(item)
            elif "ev_" in key and data[key] is not None:
                conclusion['ev_rules'] = []
                for rule_key in data[key]:
                    # 一条规则key中不包含-scm_cnt，则表示这是一条非不涉及scm的ev
                    if "-scm_cnt" not in rule_key:
                        item_count = 0
                        message = ''
                        # 在d码出现次数key中循环
                        for d_count in data[key][rule_key]:
                            if "_is__series" not in d_count:
                                # 计算出现 d_count 次的d码有多少个
                                item_count = item_count + (int(d_count) * len(data[key][rule_key][d_count]))
                                # 拼接一部分message
                                message = message + str(d_count) + " 次的d码有：" + str(
                                    data[key][rule_key][d_count]) + "，"
                                # 部分产品线校验d码是否连续
                                try:
                                    if data[key][rule_key][d_count + "_is__series"]:
                                        message = message + "这些d码是连续的；"
                                    else:
                                        message = message + "这些d码不是连续的；"
                                # pc/wap不校验d码是否连续，所以不在x_is__series这个key
                                except KeyError:
                                    pass
                        item = (rule_key.split('->')[1] + " 曝光 " + str(item_count) + " 条数据，他们由 "
                                + rule_key.split('->')[0] + " 转化而来，其中出现 " + message)
                        if data[key][rule_key + '-scm_cnt'] == 'have':
                            item = item + "这些数据曝光有scm推荐值。"
                        elif data[key][rule_key + '-scm_cnt'] == 'empty' or data[key][rule_key + '-scm_cnt'] == '':
                            item = item + "这些数据曝光没有scm推荐值。"
                        else:
                            item = item + "这些数据曝光由 " + data[key][rule_key + '-scm_cnt'] + " 推荐而来。"
                        conclusion['ev_rules'].append(item)
            elif "action_" in key and data[key] is not None:
                conclusion['action__rules'] = []
                for rule_key in data[key]:
                    item = "在 " + rule_key.split('->')[0] + " 页面，上报点击事件：" + rule_key.split('->')[
                        1] + ' ，共计' + str(data[key][rule_key]) + "次"
                    conclusion['action__rules'].append(item)
        return conclusion
    # 处理对比结果汇总
    elif data_type == "result":
        conclusion_list = []
        if pingback_type == 'pv':
            for key in data:
                item = ''
                if "base_value" in data[key] and "-scm_pre" not in key:
                    item = ("由 " + key.split('->')[0] + " 到 " + key.split('->')[1] + " 的PV，在基准规则中上报 " +
                            str(data[key]["base_value"]) + " 次，然而在测试记录中上报了 " + str(
                                data[key]["test_value"]) + " 次")
                elif "base_value" in data[key] and "-scm_pre" in key:
                    item = ("由 " + key.split('->')[0] + " 到 " + key.split('->')[1].replace('-scm_pre', '') +
                            " 的PV，在基准规则中由 " + str(data[key]["base_value"]) + " 推荐而来，然而在测试记录中由 " +
                            str(data[key]["test_value"]) + " 推荐而来")
                elif 'only_base' in data[key] and "-scm_pre" not in key:
                    item = ("由 " + key.split('->')[0] + " 到 " + key.split('->')[1] + " 的PV，仅在基准规则中上报 " +
                            str(data[key]["only_base"]) + " 次，然而在测试记录中没有该PV。")
                elif 'only_test' in data[key] and "-scm_pre" not in key:
                    item = ("由 " + key.split('->')[0] + " 到 " + key.split('->')[1] + " 的PV，在基准规则中不存在，仅在测试记录中上报 " +
                            str(data[key]["only_test"]) + " 次。")
                if item != '':
                    conclusion_list.append(item)
        elif pingback_type == 'ev':
            for key in data:
                if "base_value" in data[key] and "-scm_cnt" not in key:
                    item_count = 0
                    message = ''
                    # 在d码出现次数key中循环
                    for d_count in data[key]["base_value"]:
                        if "_is__series" not in d_count:
                            # 计算出现 d_count 次的d码有多少个
                            item_count = item_count + (int(d_count) * len(data[key]["base_value"][d_count]))
                            # 拼接一部分message
                            message = message + str(d_count) + " 次的d码有：" + str(
                                data[key]["base_value"][d_count]) + "，"
                            # 部分产品线校验d码是否连续
                            try:
                                if data[key]["base_value"][d_count + "_is__series"]:
                                    message = message + "这些d码是连续的；"
                                else:
                                    message = message + "这些d码不是连续的；"
                            # pc/wap不校验d码是否连续，所以不存在x_is__series这个key
                            except KeyError:
                                pass
                    item = "基准规则中：" + key.split('->')[1] + " 曝光 " + str(item_count) + " 条数据，他们由 " + \
                           key.split('->')[0] + " 转化而来，其中出现 " + message
                    item_count = 0
                    message = ''
                    for d_count in data[key]["test_value"]:
                        if "_is__series" not in d_count:
                            # 计算出现 d_count 次的d码有多少个
                            item_count = item_count + (int(d_count) * len(data[key]["test_value"][d_count]))
                            # 拼接一部分message
                            message = message + str(d_count) + " 次的d码有：" + str(
                                data[key]["test_value"][d_count]) + "，"
                            # 部分产品线校验d码是否连续
                            try:
                                if data[key]["test_value"][d_count + "_is__series"]:
                                    message = message + "这些d码是连续的；"
                                else:
                                    message = message + "这些d码不是连续的；"
                            # pc/wap不校验d码是否连续，所以不在x_is__series这个key
                            except KeyError:
                                pass
                    item_test = ("而在测试数据中：" + key.split('->')[1] + " 曝光 " + str(
                        item_count) + " 条数据，他们由 " + key.split('->')[0] + " 转化而来，其中出现 " + message)
                    conclusion_list.append(item + item_test)
                elif "base_value" in data[key] and "-scm_cnt" in key:
                    if data[key]["base_value"] == 'have':
                        item = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                               key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，存在推荐策略。"
                    elif data[key]["base_value"] == 'empty' or data[key]["base_value"] == '':
                        item = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                               key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，不存在推荐策略。"
                    else:
                        item = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                               key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，推荐策略为 " + data[key][
                                   "base_value"] + " "
                    if data[key]["test_value"] == 'have':
                        item_test = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                                    key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，存在推荐策略。"
                    elif data[key]["test_value"] == 'empty' or data[key]["test_value"] == '':
                        item_test = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                                    key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，不存在推荐策略。"
                    else:
                        item_test = "由 " + key.replace('-scm_cnt', '').split('->')[0] + "转化，" + \
                                    key.replace('-scm_cnt', '').split('->')[1] + "区块的数据曝光，推荐策略为 " + \
                                    data[key]["test_value"] + " "
                    conclusion_list.append("在基准规则中，" + item + "而在测试数据中，" + item_test)
                elif "only_base" in data[key] and "-scm_cnt" not in key:
                    item_count = 0
                    message = ''
                    # 在d码出现次数key中循环
                    for d_count in data[key]["only_base"]:
                        if "_is__series" not in d_count:
                            # 计算出现 d_count 次的d码有多少个
                            item_count = item_count + (int(d_count) * len(data[key]["only_base"][d_count]))
                            # 拼接一部分message
                            message = message + str(d_count) + " 次的d码有：" + str(
                                data[key]["only_base"][d_count]) + "，"
                            # 部分产品线校验d码是否连续
                            try:
                                if data[key]["only_base"][d_count + "_is__series"]:
                                    message = message + "这些d码是连续的；"
                                else:
                                    message = message + "这些d码不是连续的；"
                            # pc/wap不校验d码是否连续，所以不在x_is__series这个key
                            except KeyError:
                                pass
                    item = (key.split('->')[1] + " 曝光 " + str(item_count) + " 条数据，他们由 " + key.split('->')[0] +
                            " 转化而来，其中出现 " + message + "这条规则仅在基准数据中出现，测试记录中不存在该类数据。")
                    conclusion_list.append(item)
                elif "only_test" in data[key] and "-scm_cnt" not in key:
                    item_count = 0
                    message = ''
                    # 在d码出现次数key中循环
                    for d_count in data[key]["only_test"]:
                        if "_is__series" not in d_count:
                            # 计算出现 d_count 次的d码有多少个
                            item_count = item_count + (int(d_count) * len(data[key]["only_test"][d_count]))
                            # 拼接一部分message
                            message = message + str(d_count) + " 次的d码有：" + str(
                                data[key]["only_test"][d_count]) + "，"
                            # 部分产品线校验d码是否连续
                            try:
                                if data[key]["only_test"][d_count + "_is__series"]:
                                    message = message + "这些d码是连续的；"
                                else:
                                    message = message + "这些d码不是连续的；"
                            # pc/wap不校验d码是否连续，所以不在x_is__series这个key
                            except KeyError:
                                pass
                    item = (key.split('->')[1] + " 曝光 " + str(item_count) + " 条数据，他们由 " + key.split('->')[0] +
                            " 转化而来，其中出现 " + message + "这条规则仅在测试数据中出现，基准数据中不存在该类数据。")
                    conclusion_list.append(item)
        elif pingback_type == 'action':
            for key in data:
                if "base_value" in data[key]:
                    item = ("基础规则中，在 " + key.split('->')[0] + " 页面，上报点击事件：" + key.split('->')[1] + ' ，共计' +
                            str(data[key]["base_value"]) + "次，然而在测试记录中该点击事件上报："+str(data[key]["test_value"])+"次")
                elif 'only_base' in data[key]:
                    item = ("在 " + key.split('->')[0] + " 页面，上报点击事件：" + key.split('->')[1] + ' ，共计' +
                            str(data[key]["only_base"]) + "次，仅在基准规则中出现，然而在测试记录中没有该上报。")
                elif 'only_test' in data[key]:
                    item = ("在 " + key.split('->')[0] + " 页面，上报点击事件：" + key.split('->')[1] + ' ，共计' +
                            str(data[key]["only_test"]) + "次，仅在测试记录中出现，然而在基准规则中没有该上报。")
                conclusion_list.append(item)
        return {"conclusion": conclusion_list}
