import os
import json
import random
import requests
import paramiko
import threading
from scp import SCPClient
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# 定义一个锁，用于同步访问计数器
lock = threading.Lock()
found_urls_count = 0
max_urls_to_find = 50

def check_page(response):
    if response.status_code == 200:
        if "The requested URL was not found on this serve" not in response.text:
            if "<title>404</title>" not in response.text:
                return True


def check_url(number1, number2, stop_event):
    global found_urls_count
    url = f"https://pc.qq.com/detail/{number1}/detail_{number2}.html"
    try:
        response = requests.get(url, timeout=5)
        if check_page(response):
            with lock:
                if found_urls_count >= max_urls_to_find:
                    stop_event.set()
                    return
                found_urls_count += 1
                print(f"找到有效URL: {url} (总计: {found_urls_count})")
                with open("url.txt", "a") as file:
                    file.write(url + "\n")
                if found_urls_count >= max_urls_to_find:
                    stop_event.set()
    except requests.exceptions.RequestException as e:
        print(f"错误: {url}, error: {e}")

def check_urls_concurrently():
    number1_values = random.sample(range(1, 21), 20)
    number2_values = random.sample(range(1, 30001), 2000)
    stop_event = threading.Event()
    with ThreadPoolExecutor(max_workers=64) as executor:
        futures = []
        for number1 in number1_values:
            for number2 in number2_values:
                if stop_event.is_set():
                    break
                future = executor.submit(check_url, number1, number2, stop_event)
                futures.append(future)
            if stop_event.is_set():
                break
        # 等待所有线程完成，或者直到stop_event被设置
        for future in futures:
            if stop_event.is_set():
                future.cancel()
            else:
                future.result()
                
# 函数：处理每个URL，获取下载URL并保存
def get_download_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.find_all('a', class_='detail-install-normal')
            if not a_tags:
                raise ValueError("没有找到下载URL。")
            for a in a_tags:
                download_url = a.get('href')
                if download_url:
                    with open('download_url.txt', 'a', encoding='utf-8') as f:
                        f.write(download_url + '\n')
                    print('找到下载URL:', download_url)
        else:
            print('请求页面失败，状态码:', response.status_code)
    except requests.RequestException as e:
        print(f'请求URL时出现错误: {e}')
    except ValueError as ve:
        print(f'处理URL时出现错误: {ve}')
    except Exception as ex:
        print(f'处理URL "{url}" 时出现未知错误: {ex}')

def push_download_url_to_servers():
    json_file_path = 'server_login_info.json'
    with open(json_file_path, 'r') as file:
        servers = json.load(file)

    local_file_path = 'download_url.txt'
    remote_file_path = '/root/download_url.txt'

    # 传输文件到每个服务器
    for server in servers:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(local_file_path, remote_file_path)
            print(f"文件已成功传输到 {server['host']}")
        except Exception as e:
            print(f"传输到 {server['host']} 失败: {e}")
        finally:
            ssh.close()

# 主程序开始
# 清空之前的数据
if 'url.txt' in os.listdir():
    os.remove('url.txt')
if 'download_url.txt' in os.listdir():
    os.remove('download_url.txt')
check_urls_concurrently()
with open('url.txt', 'r', encoding='utf-8') as file:
    for line in file:
        url = line.strip()
        get_download_url(url)

# 推送至给个服务器
# push_download_url_to_servers()