import subprocess
import threading
import time
import concurrent.futures

# 定义要下载的URL列表
url_list = []

# 从文件中读取URL列表
with open('soft.txt', 'r') as file:
    url_list = file.read().splitlines()

# 定义下载函数
def download_url(url):
    try:
        subprocess.run([
            'wget',
            url,
            '-O', '/dev/null', '-q',
            '--header', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.1234.5678 Safari/537.36',
        ])
        print(f'Successfully downloaded: {url}')
    except Exception as e:
        print(f'下载错误{url}: {e}')

# 定义带宽饱和下载任务
def saturate_bandwidth():
    while True:
        # 在线程池中创建多个下载线程
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            executor.map(download_url, url_list)

# 启动带宽饱和任务
saturate_thread = threading.Thread(target=saturate_bandwidth)
saturate_thread.daemon = True
saturate_thread.start()

# 让脚本持续运行
while True:
    time.sleep(1)
