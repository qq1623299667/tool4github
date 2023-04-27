import logging
import os
import sys
import time

import colorlog
import pandas as pd
import paramiko
import pymysql
from subprocess import Popen, PIPE, STDOUT


def exec_multi_win_cmd(commands, cwd=None):
    if cwd:
        process = Popen(["cmd"], shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT, cwd=cwd)
    else:
        process = Popen(["cmd"], shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    outs, errs = process.communicate(commands.encode("gbk"))
    content = [z.strip() for z in outs.decode("gbk").split("\n") if z]
    return content


def ping(ip):
    commands = (
        f'ping {ip}\n'
    )
    content = exec_multi_win_cmd(commands=commands)
    for item in content:
        if '请求超时' in item:
            return False
    return True


def txt2pd(file, split_str='\t'):
    with open(file, "r", encoding='utf-8', errors='ignore') as f:
        list2 = []
        for line in f:
            dict2 = {}
            split = line.split(split_str)
            for i in range(len(split)):
                dict2[i] = split[i].replace('\n', '')
            list2.append(dict2)
        pd_from_txt = pd.DataFrame(list2)
        return pd_from_txt


def get_ssh(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host["host"], username=host["ssh_user"], password=host["ssh_pwd"])
    return ssh


def ssh_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf8")
    return out


def get_pass_by_ip(servers_df, ip):
    row_server = servers_df.loc[servers_df[0] == ip]
    user = row_server.iloc[0, 1]
    password = row_server.iloc[0, 2]
    return user, password


def monitor_log_count(servers_df, logs_df):
    log.info('开始监控服务器的日志数量')
    for i in range(len(logs_df)):
        ip = logs_df.iloc[i, 0]
        user, password = get_pass_by_ip(servers_df, ip)
        path = logs_df.iloc[i, 1]
        host = {
            "host": ip,
            "ssh_user": user,
            "ssh_pwd": password,
        }
        ssh = get_ssh(host)
        cmd = f'''
            cd {path}
            ls | wc -l
        '''
        out = ssh_command(ssh, cmd)
        count = out.replace('\n', '')
        log.info(f'{ip} {path} 目录一共有日志 {count} 个')


def monitor_error_log(servers_df, logs_df):
    log.info('开始监控系统异常日志')
    for i in range(len(logs_df)):
        row_log = logs_df.iloc[i]
        ip = row_log.iloc[0]
        path = row_log.iloc[1]
        log_file = row_log.iloc[2]
        service = row_log.iloc[3]
        row_server = servers_df.loc[servers_df[0] == ip]
        host = {
            "host": ip,
            "ssh_user": row_server.iloc[0].iloc[1],
            "ssh_pwd": row_server.iloc[0].iloc[2],
        }
        ssh = get_ssh(host)
        cmd = f'''
            tac {path}{log_file} | grep ' ERROR ' -m 100
        '''
        out = ssh_command(ssh, cmd)
        if out:
            list1 = []
            split = out.split('\n')
            for item1 in split:
                list1.append(item1)
            if list1:
                log.info(f'{ip} {service}服务发现异常')
                for item2 in list1:
                    log.info(item2)


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


class DBMysql(object):
    def __init__(self, database='cloud_user', host=None, user=None, password=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self._conn = pymysql.connect(host=self.host, user=self.user,
                                     password=self.password, db=database, port=port)

    # 关闭数据库
    def close(self):
        if self._conn is not None:
            self._conn.close()

    # 查询
    def query(self, sql, *params):
        cursor = self._conn.cursor()
        cursor.execute(sql, *params)
        result = cursor.fetchall()
        cursor.close()
        return result

    # 增删改
    def edit(self, sql, *params):
        cursor = self._conn.cursor()
        cursor.execute(sql, *params)
        self._conn.commit()
        cursor.close()

    # 批量入库
    def batch_insert(self, sql, values):
        cursor = self._conn.cursor()
        cursor.executemany(sql, values)
        self._conn.commit()
        cursor.close()


def common_query(sql_df, config_df, param_dict=None, db=None):
    sql = sql_df.iloc[0, 2]
    if param_dict:
        for key, value in param_dict.items():
            sql = sql.replace('{' + key + '}', value)
    if not db:
        db = sql_df.iloc[0, 1]
    host = config_df.iloc[0, 2]
    user = config_df.iloc[0, 4]
    password = config_df.iloc[0, 5]
    port = int(config_df.iloc[0, 3])
    db_mysql = DBMysql(database=db, host=host, user=user, password=password, port=port)
    result = db_mysql.query(sql)
    result_pd = pd.DataFrame(result)
    return result_pd


def monitor_mysql_latest_time(mysql_sql_df2, mysql_pass_df2, last_time_df2):
    for i in range(len(last_time_df2)):
        db = last_time_df2.iloc[i, 0]
        table = last_time_df2.iloc[i, 1]
        time_column = last_time_df2.iloc[i, 2]
        param_dict = {
            'time_column': time_column,
            'table': table,
        }
        latest_time_df = common_query(mysql_sql_df2, mysql_pass_df2, param_dict, db=db)
        log.info(f'{db} {table} 最新的 {time_column} 是: ' + str(latest_time_df[0][0]))


def choose_program_and_env():
    env_df = txt2pd('env.txt')
    dict1 = {}
    str1 = '请输入需要选择的环境:\n'
    for i in range(len(env_df)):
        key = env_df.iloc[i, 0]
        value = env_df.iloc[i, 2].replace('\n', '')
        desc = env_df.iloc[i, 1] + "\n"
        str1 = str1 + f'{key} = {desc}'
        dict1[key] = value
    code2 = input(str1)
    dict_value = dict1[code2]
    split = dict_value.split(':')
    program = split[0]
    env = split[1]
    return program, env


def monitor_disk_exceeding_standard(ip, user, password):
    host = {
        "host": ip,  # rd2
        "ssh_user": user,
        "ssh_pwd": password,
    }
    ssh = get_ssh(host)
    cmd = f'''
        df -h
    '''
    command = ssh_command(ssh, cmd)
    split = command.split('\n')
    for i in range(len(split)):
        if i == 0:
            continue
        item = split[i]
        if item:
            index = item.find('%')
            value = ''
            try:
                value = item[index - 3: index]
                persent = int(value.replace(' ', ''))
            except Exception as e:
                print(item)
                print(value)
                sys.exit(1)
            if persent >= 85:
                return True
    return False


def monitor_memory_exceeding_standard(ip, user, password):
    host = {
        "host": ip,  # rd2
        "ssh_user": user,
        "ssh_pwd": password,
    }
    ssh = get_ssh(host)
    cmd = f'''
            free
        '''
    command = ssh_command(ssh, cmd)
    split = command.split('\n')
    mem = split[1]
    for i in range(100):
        if '  ' in mem:
            mem = mem.replace('  ', ' ')
        else:
            break
    mem_split = mem.split(' ')
    total_mem = int(mem_split[1])
    total_free = int(mem_split[3])
    already_used = int((total_mem - total_free) / total_mem * 100)
    return already_used


def monitor_server_health(df):
    log.info('开始监控服务器健康情况')
    for i in range(len(df)):
        ip = df.iloc[i, 0]
        ssh_user = df.iloc[i, 1]
        ssh_pwd = df.iloc[i, 2]
        server_alive = ping(ip)
        if server_alive:
            disk_exceeding_standard = monitor_disk_exceeding_standard(ip, ssh_user, ssh_pwd)
            memory_use = monitor_memory_exceeding_standard(ip, ssh_user, ssh_pwd)
            if disk_exceeding_standard or memory_use >= 90:
                log.warning(f'服务器 {ip} 成功连接,磁盘超标状态 {disk_exceeding_standard} ,内存已使用 {memory_use}%')
            else:
                log.info(f'服务器 {ip} 成功连接,磁盘超标状态 {disk_exceeding_standard} ,内存已使用 {memory_use}%')
        else:
            log.warning(f'服务器 {ip} 无法连接')


def monitor_service_alive(servers_df, logs_df):
    log.info('开始监控服务存活情况')
    for i in range(len(logs_df)):
        ip = logs_df.iloc[i, 0]
        user, password = get_pass_by_ip(servers_df, ip)
        service = logs_df.iloc[i, 3]
        host = {
            "host": ip,  # rd2
            "ssh_user": user,
            "ssh_pwd": password,
        }
        ssh = get_ssh(host)
        cmd = f'''
                ps aux | grep {service}
            '''
        command = ssh_command(ssh, cmd)
        alive = False
        if command:
            split = command.split('\n')
            for item in split:
                if 'java' in item and service in item:
                    alive = True
                    break
        if alive:
            log.info(f'{service} 服务存活')
        else:
            log.warning(f'{service} 服务未存活')


def do_spider():
    logs_df = txt2pd('server_log.txt')
    servers_df = txt2pd('server_pass.txt')

    code = input(f'''请输入要执行的监控项:
0=退出程序,
1=监控服务器健康状况,
2=监控服务存活情况,
3=监控系统日志数量,
4=监控系统异常日志,
5=监控mysql最新时间,
''')
    if code == '0':
        log.info('程序正常退出')
        sys.exit(0)
    elif code == '1':
        # 监控服务器健康状况
        monitor_server_health(servers_df)
    elif code == '2':
        # 监控服务存活情况
        program, env = choose_program_and_env()
        logs_df = logs_df.loc[(logs_df[4] == program) & (logs_df[5] == env)]
        monitor_service_alive(servers_df, logs_df)
    elif code == '3':
        # 监控系统日志数量
        program, env = choose_program_and_env()
        logs_df = logs_df.loc[(logs_df[4] == program) & (logs_df[5] == env)]
        monitor_log_count(servers_df, logs_df)
    elif code == '4':
        # 监控系统异常日志
        program, env = choose_program_and_env()
        logs_df = logs_df.loc[(logs_df[4] == program) & (logs_df[5] == env)]
        monitor_error_log(servers_df, logs_df)
    elif code == '5':
        # 监控mysql最新时间
        program, env = choose_program_and_env()
        label = 'get_latest_time'
        sql_df = txt2pd('mysql_sql.txt')
        mysql_pass_df = txt2pd('mysql_pass.txt')
        last_time_df = txt2pd('mysql_latest_time.txt')
        mysql_sql_df2 = sql_df.loc[(sql_df[0] == label)]
        mysql_pass_df2 = mysql_pass_df.loc[(mysql_pass_df[0] == program) & (mysql_pass_df[1] == env)]
        last_time_df2 = last_time_df.loc[(last_time_df[3] == program) & (last_time_df[4] == env)]
        monitor_mysql_latest_time(mysql_sql_df2, mysql_pass_df2, last_time_df2)
    else:
        log.error('输入错误!')


# 蜘蛛网系统
if __name__ == '__main__':
    log = LogConf().logger
    log.info('欢迎来到蜘蛛网系统!')
    time.sleep(1)
    while True:
        do_spider()
        time.sleep(1)
