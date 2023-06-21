import json
import logging
import os

import colorlog
import pandas as pd
import requests


def txt2pd(file, split_str='\t'):
    with open(file, "r", encoding='utf-8') as f:
        list2 = []
        for line in f:
            if not line.startswith("#") and len(line.replace('\n', '').replace(' ', '')) > 0:
                dict2 = {}
                split = line.split(split_str)
                for i in range(len(split)):
                    dict2[i] = split[i].replace('\n', '')
                list2.append(dict2)
        pd_from_txt = pd.DataFrame(list2)
        return pd_from_txt


def choose_env():
    env_df = txt2pd('env.txt1')
    str1 = '请选择环境:\n'
    for i in range(len(env_df)):
        key = env_df.iloc[i, 0]
        desc = env_df.iloc[i, 1] + "\n"
        str1 = str1 + f'{key} = {desc}'
    code2 = input(str1)
    return env_df.loc[(env_df[0] == code2)]


def do_get_test(url_prefix, header, interface_df, i):
    uri = interface_df.iloc[i, 2]
    param_str = interface_df.iloc[i, 3]
    url = url_prefix + uri + "?" + param_str
    assert_res = interface_df.iloc[i, 4]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    header_dict = eval(header)
    headers.update(header_dict)
    response = requests.get(url, headers=headers)
    data = response.text
    assert_dict = eval(assert_res)
    data_dict = json.loads(data)
    check_result = check_dict(assert_dict, data_dict)
    if check_result:
        log.info(f'{uri}  {param_str}  验证通过')
    else:
        log.warning(f'{uri}  {param_str}  验证不通过')


class LogConf(object):
    logger = logging.getLogger('logger_name')

    def __init__(self):
        log_colors_config = {
            'DEBUG': 'green',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        # 输出到控制台
        console_handler = logging.StreamHandler()
        # 输出到文件
        file = os.path.basename(__file__)
        log_dir = os.path.join("./Log")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        relative_path_name = 'Log/' + file[:file.rfind('.')] + '.log'
        file_handler = logging.FileHandler(filename=relative_path_name, mode='a', encoding='utf8')

        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        self.logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.INFO)

        # 日志输出格式
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S'
        )
        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config
        )
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        # 重复日志问题：
        # 1、防止多次addHandler；
        # 2、loggername 保证每次添加的时候不一样；
        # 3、显示完log之后调用removeHandler
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

        console_handler.close()
        file_handler.close()


# 获取匹配结果
def check_dict(assert_dict, data_dict):
    for key, value in assert_dict.items():
        if key not in data_dict or data_dict[key] != value:
            return False
    return True


def do_post_test(url_prefix, header, interface_df, i):
    uri = interface_df.iloc[i, 2]
    param_str = interface_df.iloc[i, 3]
    param_dict = json.loads(param_str)
    url = url_prefix + uri
    assert_res = interface_df.iloc[i, 4]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    header_dict = eval(header)
    headers.update(header_dict)
    response = requests.post(url, headers=headers, json=param_dict)
    data = response.text
    assert_dict = eval(assert_res)
    data_dict = json.loads(data)
    check_result = check_dict(assert_dict, data_dict)
    if check_result:
        log.info(f'{uri}  {param_str}  验证通过')
    else:
        log.warning(f'{uri}  {param_str}  验证不通过')


def do_put_test():
    pass


def do_delete_test():
    pass


# 获取接口列表
def get_interface_list(interface_list_location):
    interface_df = txt2pd(interface_list_location)
    return interface_df


def test_interface_list(env_df):
    interface_list_location = env_df.iloc[0, 5]
    interface_df = get_interface_list(interface_list_location)
    url_prefix = env_df.iloc[0, 3]
    header = env_df.iloc[0, 4]
    for i in range(len(interface_df)):
        request_type = interface_df.iloc[i, 0]
        if request_type == 'get':
            do_get_test(url_prefix, header, interface_df, i)
        elif request_type == 'post':
            do_post_test(url_prefix, header, interface_df, i)
        elif request_type == 'put':
            do_put_test()
        elif request_type == 'delete':
            do_delete_test()
        else:
            log.warning('配置错误，请重新配置' + interface_df.iloc[i])


# 简易单元测试，支持自定义配置环境，url，token，断言结果（只支持一种）
# 使用前请修改env.txt里面的token值
if __name__ == '__main__':
    log = LogConf().logger
    env_df1 = choose_env()
    test_interface_list(env_df1)
