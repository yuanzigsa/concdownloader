import os
import time
import random
import psutil
import logging
import threading
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# 配置日志以方便维护
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, 'auto_downloader.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', interval=1, backupCount=30)  # 日志文件按天滚动，保留时长为30天
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)  # 将Handler添加到Logger中

# Time : 2024/1/4
# Author : yuanzi


# 支持单IP以及多IP自动识别按小时进行轮询下载
logo = f"""开始启动AutoDownloader程序...\n
     ██               ██            ███████                                 ██                         ██               
    ████             ░██           ░██░░░░██                               ░██                        ░██               
   ██░░██   ██   ██ ██████  ██████ ░██    ░██  ██████  ███     ██ ███████  ░██  ██████   ██████       ░██  █████  ██████
  ██  ░░██ ░██  ░██░░░██░  ██░░░░██░██    ░██ ██░░░░██░░██  █ ░██░░██░░░██ ░██ ██░░░░██ ░░░░░░██   ██████ ██░░░██░░██░░█
 ██████████░██  ░██  ░██  ░██   ░██░██    ░██░██   ░██ ░██ ███░██ ░██  ░██ ░██░██   ░██  ███████  ██░░░██░███████ ░██ ░ 
░██░░░░░░██░██  ░██  ░██  ░██   ░██░██    ██ ░██   ░██ ░████░████ ░██  ░██ ░██░██   ░██ ██░░░░██ ░██  ░██░██░░░░  ░██   
░██     ░██░░██████  ░░██ ░░██████ ░███████  ░░██████  ███░ ░░░██ ███  ░██ ███░░██████ ░░████████░░██████░░██████░███   
░░      ░░  ░░░░░░    ░░   ░░░░░░  ░░░░░░░    ░░░░░░  ░░░    ░░░ ░░░   ░░ ░░░  ░░░░░░   ░░░░░░░░  ░░░░░░  ░░░░░░ ░░░    
【程序版本】：v1.0
【更新时间】：2024/1/4
【当前路径】：{os.getcwd()}
"""

# 获取本机在线IP
def get_ip_addresses():
    ip_addresses = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET' and address.address != '127.0.0.1':
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


# wget下载
def wget():
    global current_ip, last_hour
    while True:
        try:
            time.sleep(1)
            urls = open('res/soft.txt').readlines()
            random.shuffle(urls)
            if 'http' in urls[0]:
                url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
                localtime = time.localtime(time.time())
                hour = int(time.strftime("%H", localtime))

                # 如果当前小时与上次的小时不同，选择一个新的随机IP
                if hour != last_hour:
                    current_ip = random.choice(ip_list)
                    last_hour = hour

                cmd = "wget  --bind-address=" + current_ip + " -q --user-agent='Mozilla/5.0' -O /dev/null '" + url + "'"
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
            logging.info(f"出错: {e}")

        time.sleep(interval)


if __name__ == '__main__':
    # 限制python进程的cpu占用率

    # 启动程序
    logging.info(logo)
    current_ip = None
    last_hour = None
    # 获取IP地址列表
    ip_list = get_ip_addresses()
    # 清理wget线程
    threading.Thread(target=kill_wget).start()
    threading.Thread(target=random_hosts_list).start()

    # 创建下载线程，所创建的线程数量根据机器性能决定
    created_threads = 0
    while get_cpu_idle_value() > 15:
        threading.Thread(target=wget).start()
        created_threads += 1
    logging.info(f"已创建{created_threads}个wget下载线程来进行持续下载")

    # 创建其他线程下载工具
    # 爬取资源
    # 提取域名
    # 解析域名 （外省解析）
    # 查IP归属
    # 写hosts
    # ip =$(curl - s http: // myip.ipip.net)
    # echo
    # "My public IP address is: $ip"
