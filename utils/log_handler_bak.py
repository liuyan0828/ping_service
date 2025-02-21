import json
from functools import reduce


def generate_base_rules(project, ping_back_log, mode):
    """
    生成规则的函数，基于pingback日志生成规则

    Args:
        project (Project): 项目
        ping_back_log (list): pingback日志列表
        mode (str): 日志模式，=prod生产模式，不兼容任何错误

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
            action_log_list.append(json.loads(log.get('log')))
    rules['pv_rules'], rules_structure['pv_rules_structure'] = \
        generate_pv_base_rules(project, pv_log_list) if pv_log_list else (None, None)
    rules['ev_rules'], rules_structure['ev_rules_structure'] = \
        generate_ev_base_rules(project, ev_log_list, mode) if ev_log_list else (None, None)
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
    if '.' in spm_code:
        code_list = spm_code.split('.')
        spm_result = '.'.join(code_list[start:(start + scope)])
    else:
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
        try:
            rules_structure_list = []
            # 获取spmpre和spmcnt的a、b码
            if platform == 'PC' or platform == 'Wap':
                spm_pre = get_spm_code(pv_list[i]['spmPre'], scope=3)
                spm_cnt = get_spm_code(pv_list[i]['spmCnt'], scope=3)
            elif platform == 'miniapp':
                try:
                    spm_pre = get_spm_code(pv_list[i]['pv_modules']['spm_pre'], scope=3)
                except KeyError:
                    spm_pre = 'empty'
                spm_cnt = get_spm_code(pv_list[i]['pv_modules']['spm_cnt'], scope=3)
            if spm_pre + '->' + spm_cnt in pv_base_rules.keys():
                # 如果该路径规则存在，则该路径出现次数+1
                pv_base_rules[spm_pre + '->' + spm_cnt] = pv_base_rules[spm_pre + '->' + spm_cnt] + 1
            else:
                # 如果该路径规则不用存在，则该路径加入到规则字典
                pv_base_rules[spm_pre + '->' + spm_cnt] = 1
                # 获取该路径规则所包含的字段，用于后续验证
                pv_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                    json_get_keys(pv_list[i], rules_structure_list)
        except KeyError:
            # 说明日志存在不可解析的状况，将标识置为true，并将不能解析的完整日志加入返回结果
            have_bad_log = True
            bad_log['pv_' + str(i)] = pv_list[i]
    if have_bad_log is True:
        return None, bad_log
    else:
        return pv_base_rules, pv_base_rule_structure


def generate_ev_base_rules(platform, ev_list, mode='prod'):
    """
    生成EV规则的函数，基于EV日志生成规则

    Args:
        platform (str): 平台
        ev_list (list): EV日志列表
        mode (str): prod or any string: prod=正式模式，不兼容任何不可解析数据;其他=调试模式，兼容一些不可解析的情况

    Returns:
        (dict, dict): 规则字典和规则结构字典

    """
    ev_temp_rules, ev_base_rules, ev_base_rule_structure = {}, {}, {}
    # 增加字段记录是否有基础规则出错及详细错误
    have_bad_log = False
    bad_log = {}

    for i in range(len(ev_list)):
        rules_structure_list = []
        if platform == 'PC' or platform == 'Wap':
            spm_pre = get_spm_code(ev_list[i]['evArgumentLst']['spmPre'], scope=3)
            spm_cnt = get_spm_code(ev_list[i]['evArgumentLst']['spmCnt'], scope=3)
            spm_cnt_d = get_spm_code(ev_list[i]['evArgumentLst']['spmCnt'], start=3, scope=1)
        elif platform == 'miniapp':
            try:
                spm_pre = get_spm_code(ev_list[i]['exp_info']['spm_pre'], scope=3)
            except KeyError:
                spm_pre = 'empty'
            spm_cnt = get_spm_code(ev_list[i]['exp_info']['spm_cnt'], scope=3)
            spm_cnt_d = get_spm_code(ev_list[i]['exp_info']['spm_cnt'], start=3, scope=1)
        if mode == 'prod':
            try:
                if spm_pre + '->' + spm_cnt in ev_temp_rules.keys():
                    ev_temp_rules[spm_pre + '->' + spm_cnt].append(int(spm_cnt_d))
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = sorted(ev_temp_rules[spm_pre + '->' + spm_cnt])
                else:
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = [int(spm_cnt_d)]
                    ev_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                        json_get_keys(ev_list[i], rules_structure_list)
            except ValueError:
                have_bad_log = True
                bad_log['ev_' + str(i)] = ev_list[i]
        else:
            # 跳过了spmcnt为空的情况，通常spmcnt不可能为空，
            try:
                if spm_pre + '->' + spm_cnt in ev_temp_rules.keys() and spm_cnt != 'empty':
                    ev_temp_rules[spm_pre + '->' + spm_cnt].append(int(spm_cnt_d))
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = sorted(ev_temp_rules[spm_pre + '->' + spm_cnt])
                elif spm_pre + '->' + spm_cnt not in ev_temp_rules.keys() and spm_cnt != 'empty':
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = [int(spm_cnt_d)]
                    ev_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                        json_get_keys(ev_list[i], rules_structure_list)
                elif spm_pre + '->' + spm_cnt in ev_temp_rules.keys() and spm_cnt_d == 'empty':
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = [ev_temp_rules[spm_pre + '->' + spm_cnt][0] + 1]
                else:
                    ev_temp_rules[spm_pre + '->' + spm_cnt] = [1]
                    ev_base_rule_structure[spm_pre + '->' + spm_cnt + '_structure'] = \
                        json_get_keys(ev_list[i], rules_structure_list)
            except ValueError:
                have_bad_log = True
                bad_log['ev_' + str(i)] = ev_list[i]
    # 判断d码出现多少次，是否连续
    if have_bad_log is False:
        for key1 in ev_temp_rules.keys():
            sub_value = {}
            for i in range(len(set(ev_temp_rules[key1]))):
                count = ev_temp_rules[key1].count(list(set(ev_temp_rules[key1]))[i])
                if str(count) not in sub_value.keys():
                    sub_value[str(count)] = [list(set(ev_temp_rules[key1]))[i]]
                else:
                    sub_value[str(count)].append(list(set(ev_temp_rules[key1]))[i])
            for key2 in list(sub_value.keys()):
                if len(sub_value[key2]) > 1:
                    if is_list_series(sub_value[key2]):
                        sub_value[str(key2) + '_is__series'] = True
                    else:
                        sub_value[str(key2) + '_is__series'] = False
                else:
                    sub_value[str(key2) + '_is__series'] = True
                sub_value[key2] = list(set(sub_value[key2]))
            ev_base_rules[key1] = sub_value
    if have_bad_log is True:
        return None, bad_log
    else:
        return ev_base_rules, ev_base_rule_structure


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
        try:
            rules_structure_list = []
            if platform == 'PC' or platform == 'Wap':
                spm_cnt = get_spm_code(action_list[i]['spmCnt'], scope=3)
                a_code = action_list[i]['acode']
            elif platform == 'miniapp':
                spm_cnt = get_spm_code(action_list[i]['action_info']['spm_cnt'], scope=3)
                a_code = action_list[i]['action_info']['acode']
            if spm_cnt + '->' + a_code in action_base_rules.keys():
                action_base_rules[spm_cnt + '->' + a_code] = action_base_rules[spm_cnt + '->' + a_code] + 1
            else:
                action_base_rules[spm_cnt + '->' + a_code] = 1
                action_base_rule_structure[spm_cnt + '->' + a_code + '_structure'] = \
                    json_get_keys(action_list[i], rules_structure_list)
        except KeyError:
            have_bad_log = True
            bad_log['action_' + str(i)] = action_list[i]
    if have_bad_log is True:
        return None, bad_log
    else:
        return action_base_rules, action_base_rule_structure


def get_log_difference(base_pingback_log, test_pingback_log):
    """
    get the different data bewtten two dicts objects
    return :result = first - second

    """
    assert isinstance(base_pingback_log, dict)
    assert isinstance(test_pingback_log, dict)
    different_data = {}
    update_key = set(base_pingback_log).intersection(set(test_pingback_log))
    insert_key = set(base_pingback_log).difference(set(test_pingback_log))
    delete_key = set(test_pingback_log).difference(set(base_pingback_log))

    # update data item which are both on first and second and Not equal values
    for k in update_key:
        if isinstance(base_pingback_log[k], dict):
            result = get_log_difference(base_pingback_log[k], test_pingback_log[k])
            if len(result) > 0:
                different_data[k] = result
        elif base_pingback_log[k] != test_pingback_log[k]:
            different_data[k] = base_pingback_log[k]
            # insert new item from first
    for k in insert_key:
        different_data[k] = base_pingback_log[k]
    # delete data
    for k in delete_key:
        different_data[k] = None
    return different_data


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
