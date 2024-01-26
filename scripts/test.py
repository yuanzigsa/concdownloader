import os
import time
import json
import paramiko
import datetime
import schedule
import logging
from logging.handlers import TimedRotatingFileHandler

# 配置日志以方便维护
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, 'auto_downloader.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', interval=1,
                                        backupCount=30)  # 日志文件按天滚动，保留时长为30天
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)  # 将Handler添加到Logger中


# 远程主机执行命令
def run_command_on_server(server, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        result = f"在 {server['host']} 上执行命令[{command}]的输出：\n{output if output else error}"
        logging.info(result)
        ssh.close()
    except Exception as e:
        result = f"在 {server['host']} 上执行命令[{command}]失败: {e}"
        logging.error(result)


# 中卫联通调度
def zwlt_start():
    node = "中卫联通"
    logging.info(f"【开启{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader start")


def zwlt_stop():
    node = "中卫联通"
    logging.info(f"【停止{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader stop")


# 荆州联通城域网
def jzltcyw_start():
    node = "荆州联通城域网"
    logging.info(f"【开启{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader start")


def jzltcyw_stop():
    node = "荆州联通城域网"
    logging.info(f"【停止{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader stop")


# 荆州联通
def jzlt_start():
    node = "荆州联通"
    logging.info(f"【开启{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader start")


def jzlt_stop():
    node = "荆州联通"
    logging.info(f"【停止{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader stop")


# 宜昌联通
def yclt_start():
    node = "宜昌联通"
    logging.info(f"【开启{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader start")


def yclt_stop():
    node = "宜昌联通"
    logging.info(f"【停止{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader stop")


# 兰州电信
def lzdx_start():
    node = "兰州电信"
    logging.info(f"【开启{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader start")


def lzdx_stop():
    node = "兰州电信"
    logging.info(f"【停止{node}机器的下载程序...】")
    for server in servers[node]:
        server = servers[node][server]
        run_command_on_server(server, "service auto_downloader stop")


if __name__ == '__main__':
    logging.info("下载流量调度程序已启动")

    with open("server_login_info.json", 'r', encoding='utf-8') as file:
        servers = json.load(file)

    yclt_start()
    jzlt_start()
    lzdx_start()
    schedule.every().day.at("19:00").do(zwlt_start)
    schedule.every().day.at("19:00").do(jzltcyw_start)

    schedule.every().day.at("23:00").do(zwlt_stop)
    schedule.every().day.at("23:00").do(jzltcyw_stop)

    while True:
        schedule.run_pending()
        time.sleep(1)

