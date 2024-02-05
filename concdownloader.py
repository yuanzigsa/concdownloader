import os
import time
import random
import psutil
import logging
import requests
import threading
from logging.handlers import TimedRotatingFileHandler

# 配置日志以方便维护
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, 'concdownloader.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = TimedRotatingFileHandler(filename=log_file_path, when='midnight', interval=1, backupCount=30)  # 日志文件按天滚动，保留时长为30天
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)  # 将Handler添加到Logger中

# Time : 2024/1/23
# Author : yuanzi


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
【程序版本】：v1.0
【更新时间】：2024/1/26
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
                # 文件总大小
                # total_size = int(result.headers.get('Content-Length', 0))
                # mb_size = total_size / 1024 / 1024
                # mb_size = round(mb_size, 2)
                # print(f"文件总大小: {mb_size}MB")
            else:
                logging.warning(f"失效url（错误码:{result.status_code}）：{url} ")
        except Exception as e:
            logging.error(f"url检测异常：{url}，异常信息：{e}")

    def get_urls():
        urls = []
        with open('res/download_url.txt', 'r') as f:
            for url in f.readlines():
                if "http" in url:
                    urls.append(url.strip())
        return urls

    def start_check(urls):
        valid_urls = [url_check(url) for url in urls]
        valid_urls = filter(None, valid_urls)
        with open('res/download_url.txt', 'w') as f:
            f.write('\n'.join(valid_urls))


    urls = get_urls()
    logging.info(f"当前url数量: {len(urls)}")
    start_check(urls)
    urls = get_urls()
    logging.info(f"经检测有效url数量: {len(urls)}")
    with open('url_vaild.info', 'w') as f:
        f.write(f"当前可用url数量: {len(urls)}\n")


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
    global current_ip, last_hour
    ip_pool = ip_list
    while True:
        try:
            time.sleep(1)
            with open('res/download_url.txt', 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
            url = random.choice(urls)
            if 'http' in url:
                # 如果当前小时与上次的小时不同，生成新的随机ip池
                if len(ip_list) >= 5:
                    ip_pool, last_hour = random_ip_pool(ip_pool,last_hour)
                current_ip = random.choice(ip_pool)
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
            logging.info(f"随机hosts列表时发生错误: {e}")

        time.sleep(interval)


# 检测当前url可用性
def urls_vaild_check():
    interval = 36000
    while True:
        try:
            urls_check()
            logging.info("url可用性检测完成")
        except Exception as e:
            logging.info(f"url可用性检测时发生错误: {e}")
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
    logging.info(f"====================wget清理线程：已启动！====================")
    threading.Thread(target=random_hosts_list).start()
    logging.info(f"====================随机hosts线程：已启动！===================")
    threading.Thread(target=urls_vaild_check).start()
    logging.info(f"==================url可用性检测线程：已启动！==================")

    create_threads = 200
    for _ in range(200):
        threading.Thread(target=wget).start()
    logging.info(f"已创建{create_threads}个wget下载线程来进行持续下载")
    # 创建下载线程，所创建的线程数量根据机器性能决定
    # created_threads = 0
    # while get_cpu_idle_value() > 30:
    #     threading.Thread(target=wget).start()
    #     created_threads += 1
    # logging.info(f"已创建{created_threads}个wget下载线程来进行持续下载")
    # 创建其他线程下载工具