# @Author  : yuanzi
# @Time    : 2024/9/29 22:17
# Website: https://www.yzgsa.com
# Copyright (c) <yuanzigsa@gmail.com>

import os
import json
import time
import socket
import random
import psutil
import logging
import requests
import threading
from logging.handlers import TimedRotatingFileHandler
from modules.speed_limit import apply_bandwidth_limit


# 配置日志以方便维护
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, 'concdownloader.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', interval=1, backupCount=30)  # 日志文件按天滚动，保留时长为30天
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)  # 将Handler添加到Logger中


# 支持单IP以及多IP自动识别按小时进行轮询下载
logo = f"""开始启动Concdownloader程序...\n
   ██████                                 ██                               ██                         ██               
  ██░░░░██                               ░██                              ░██                        ░██               
 ██    ░░   ██████  ███████   █████      ░██  ██████  ███     ██ ███████  ░██  ██████   ██████       ░██  █████  ██████
░██        ██░░░░██░░██░░░██ ██░░░██  ██████ ██░░░░██░░██  █ ░██░░██░░░██ ░██ ██░░░░██ ░░░░░░██   ██████ ██░░░██░░██░░█
░██       ░██   ░██ ░██  ░██░██  ░░  ██░░░██░██   ░██ ░██ ███░██ ░██  ░██ ░██░██   ░██  ███████  ██░░░██░███████ ░██ ░ 
░░██    ██░██   ░██ ░██  ░██░██   ██░██  ░██░██   ░██ ░████░████ ░██  ░██ ░██░██   ░██ ██░░░░██ ░██  ░██░██░░░░  ░██   
 ░░██████ ░░██████  ███  ░██░░█████ ░░██████░░██████  ███░ ░░░██ ███  ░██ ███░░██████ ░░████████░░██████░░██████░███   
  ░░░░░░   ░░░░░░  ░░░   ░░  ░░░░░   ░░░░░░  ░░░░░░  ░░░    ░░░ ░░░   ░░ ░░░  ░░░░░░   ░░░░░░░░  ░░░░░░  ░░░░░░ ░░░    
【程序版本】：v1.2
【更新时间】：2024/9/14
【当前路径】：{os.getcwd()}
"""


# 读取配置文件
def read_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    value1 = config.get("download_type")
    value2 = config.get("ips")
    value3 = config.get("polling_interval")
    value4 = config.get("download_threads")
    value_list = config.get("speed_limit")

    if value1 != "ipv4" and value1 != "ipv6" and value1 != "all":
        logging.error("config.json配置文件中下载类型有误，仅允许ipv4、ipv6或者all，请检查！")
        value1 = "ipv4"

    if type(value2) != int and type(value3) != int and type(value4) != int:
        value2 = "3"
        value3 = "600"
        value4 = "200"
        logging.error("ips、polling_interval或者download_threads配置有误，只允许整数！")

    return value1, value2, value3, value4, value_list


# 获取本机在线IP
def get_ip_addresses(type):
    ip_addresses = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.address != '127.0.0.1' and address.address != "::1":
                if type == 'ipv4':
                    if address.family == socket.AF_INET:
                        ip_addresses.append(address.address)
                elif type == 'ipv6':
                    if address.family == psutil.AF_LINK:
                        ip_addresses.append(address.address)
                else:
                    ip_addresses.append(address.address)
    return ip_addresses


# 获取cpu闲置率
def get_cpu_idle_value():

    def read_cpu_times():
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu '):
                    parts = line.split()
                    cpu_times = [int(p) for p in parts[1:]]
                    return cpu_times

    def calculate_idle_percentage(old_times, new_times):
        total_time_diff = sum(new_times) - sum(old_times)
        idle_time_diff = new_times[3] - old_times[3]
        idle_percentage = 100 * (idle_time_diff / total_time_diff)
        idle_value = int(idle_percentage)
        return idle_value

    old_times = read_cpu_times()
    time.sleep(0.1)
    new_times = read_cpu_times()
    idle_value = calculate_idle_percentage(old_times, new_times)
    return idle_value


def get_urls():
    urls = []
    with open('res/download_url.txt', 'r') as f:
        for url in f.readlines():
            if "http" in url:
                urls.append(url.strip())
    return urls


# 检测url可用性
def urls_check():
    def url_check(url):
        try:
            result = requests.get(url, stream=True, timeout=3)
            if result.status_code == 200:
                if not result.history:
                    return url
                else:
                    logging.warning(f"重定向url:{url}（重定向到:{result.url}）")
            else:
                logging.warning(f"失效url（错误码:{result.status_code}）：{url} ")
        except Exception as e:
            logging.error(f"url检测异常：{url}，异常信息：{e}")

    def start_check(urls):
        valid_urls = [url_check(url) for url in urls]
        valid_urls = filter(None, valid_urls)
        with open('res/download_url.txt', 'w') as f:
            f.write('\n'.join(valid_urls))

    global url_list
    aft_urls = get_urls()
    logging.info(f"url库总数量: {len(aft_urls)}条")
    start_check(aft_urls)
    bef_urls = get_urls()

    logging.info(f"经检测有效url数量: {len(bef_urls)}")
    with open('url_vaild.info', 'w') as f:
        f.write(f"当前可用url数量: {len(bef_urls)}\n")

    if bef_urls != aft_urls:
        url_list = aft_urls


def chunk_list(lst, chunk_size):
    avg_chunk_size = len(lst) // chunk_size
    remainder = len(lst) % chunk_size

    chunks = []
    start = 0
    for i in range(chunk_size):
        if i < remainder:
            end = start + avg_chunk_size + 1
        else:
            end = start + avg_chunk_size
        chunks.append(lst[start:end])
        start = end

    return chunks


# 获取下载
def random_ip_pool(ip_pool, last_hour):
    localtime = time.localtime(time.time())
    hour = int(time.strftime("%H", localtime))
    if hour != last_hour:
        ip_pool = random.sample(ip_list, 5)
        return ip_pool, hour
    else:
        return ip_pool, last_hour


# wget下载
def wget():
    while True:
        try:
            time.sleep(1)
            ip = random.choice(ip_pool)
            url = random.choice(urls)
            cmd = "wget  --bind-address=" + ip + " -q --user-agent='Mozilla/5.0' -O /dev/null '" + url + "'"
            os.popen(cmd)
        except Exception as e:
            logging.error(f"wget下载失败：{e}")


# 定期清理wget进程
def kill_wget():
    interval = random.randint(60, 90)
    while True:
        os.popen('pkill  wget')
        logging.info("执行pkill wget成功")
        time.sleep(interval)


#  定期随机排列hosts列表
def random_hosts_list():
    interval = random.randint(1200, 2000)

    def random_hosts():
        with open('/etc/hosts', 'r') as file:
            lines = file.readlines()
        header = lines[:2]
        content = lines[2:]
        random.shuffle(content)
        with open('/etc/hosts', 'w') as file:
            file.writelines(header + content)

    while True:
        try:
            random_hosts()
            logging.info("随机排列hosts列表成功")
        except Exception as e:
            logging.info(f"随机hosts列表时发生错误: {e}")

        time.sleep(interval)


# 检测当前url可用性
def urls_vaild_check():
    interval = 86400
    while True:
        try:
            urls_check()
            logging.info("url可用性检测完成")
        except Exception as e:
            logging.info(f"url可用性检测时发生错误: {e}")
        time.sleep(interval)


# url按ip进行轮询
def ip_polling():
    global ip_pool
    interval = polling_interval

    while True:
        try:
            ip_pool = random.sample(ip_list, ips)
            logging.info(f"本机IP总数量：{len(ip_list)}个")
            logging.info(f"当前IP轮询数量：{ips}个")
            logging.info(f"当前下载IP：{ip_pool}")
        except Exception as e:
            logging.info(f"IP轮询出错: {e}")
        time.sleep(interval)


# 按照时间段进行限速
def speed_limit():
    interval = 60
    time.sleep(10)
    with open('speed_limit.info', 'w') as file:
        info = json.load(file)
        speed_limit_info = [{json.dumps(value): False} for value in info]
        json.dump(speed_limit_info, file, indent=4)

    while True:
        try:
            apply_bandwidth_limit(speed_limit_list)
            logging.info("限速成功")
        except Exception as e:
            logging.info(f"限速出错: {e}")
        time.sleep(interval)


if __name__ == '__main__':
    # 启动程序
    logging.info(logo)
    url_pool = []

    # 读取配置
    downtype, ips, polling_interval, download_threads, speed_limit_list = read_config()

    # 获取IP地址列表
    ip_list = get_ip_addresses(downtype)
    ip_pool = random.sample(ip_list, ips)
    # 获取url列表
    urls = get_urls()

    # 清理wget线程
    threading.Thread(target=ip_polling).start()
    logging.info(f"====================随机IP轮询线程：已启动！===================")
    threading.Thread(target=kill_wget).start()
    logging.info(f"====================Wget清理线程：已启动！====================")
    threading.Thread(target=random_hosts_list).start()
    logging.info(f"====================随机hosts线程：已启动！===================")
    threading.Thread(target=speed_limit).start()
    logging.info(f"====================分时段下载限速线程：已启动！===================")
    threading.Thread(target=urls_vaild_check).start()
    logging.info(f"==================URL可用性检测线程：已启动！==================")

    for _ in range(download_threads):
        threading.Thread(target=wget).start()
    logging.info(f"已创建{download_threads}个wget下载线程来进行持续下载")
