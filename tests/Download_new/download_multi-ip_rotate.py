import os
import time
import random
import psutil
from datetime import datetime
import threading

def get_ip_addresses():
    ip_addresses = []
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET' and address.address != '127.0.0.1':
                ip_addresses.append(address.address)
    return ip_addresses


def wget():
    global current_ip, last_hour
    while True:
        time.sleep(1)
        urls = open('soft.txt').readlines()
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


def kill_wget():
    while True:
        os.popen('pkill  wget')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time}" + ': 执行pkill wget成功')
        sec = random.randint(10, 20)
        time.sleep(sec)


def random_hosts_list():
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
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time}" + ": 随机排列hosts列表成功")
        except Exception as e:
            print(f"{current_time}" + f"出错: {e}")

        time.sleep(1200)


if __name__ == '__main__':
    current_ip = None
    last_hour = None
    # 获取IP地址列表
    ip_list = get_ip_addresses()
    # 清理wget线程
    threading.Thread(target=kill_wget).start()
    threading.Thread(target=random_hosts_list).start()
    # 创建下载线程，所创建的线程数量根据机器性能决定
    for _ in range(100):  
        threading.Thread(target=wget).start()


