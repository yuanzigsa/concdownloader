import os
import time
import random
import logging
import threading
import asyncio
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import aiohttp

# ... （前面的代码保持不变）

# 异步下载函数
async def async_download(url, session, current_ip):
    try:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, connector=aiohttp.TCPConnector(local_addr=(current_ip, 0))) as response:
            # 处理响应，这里只是简单的读取响应内容并打印
            content = await response.text()
            logging.info(f"下载成功: {url}")
    except Exception as e:
        logging.error(f"下载失败: {url}, 错误信息: {e}")

# 异步主函数
async def async_main():
    global current_ip, last_hour
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

        async with aiohttp.ClientSession() as session:
            tasks = [async_download(url, session, current_ip) for _ in range(10)]  # 10个并发下载任务
            await asyncio.gather(*tasks)

if __name__ == '__main__':
    # ... （前面的代码保持不变）

    # 创建下载线程池
    created_threads = 0
    while get_cpu_idle_value() > 15:
        asyncio.run(async_main())
        created_threads += 1
    logging.info(f"已创建{created_threads}个异步下载任务来进行持续下载")

    # ... （后面的代码保持不变）
