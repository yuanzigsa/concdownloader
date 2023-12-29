import requests
from concurrent.futures import ThreadPoolExecutor
import random
import threading

# 定义一个锁，用于同步访问计数器
lock = threading.Lock()
found_urls_count = 0
max_urls_to_find = 100

def check_url(number1, number2, stop_event):
    global found_urls_count
    url = f"https://pc.qq.com/detail/{number1}/detail_{number2}.html"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "The requested URL was not found on this server" not in response.text:
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
    number2_values = random.sample(range(1, 30001), 30000)
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

check_urls_concurrently()
