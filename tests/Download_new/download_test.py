import os
import re
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor

def wget(url):
    cmd = f"wget -q --user-agent='Mozilla/5.0' -O /dev/null '{url}'"
    os.popen(cmd)

def download():
    while True:
        time.sleep(1)
        urls = open('soft.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
            localtime = time.localtime(time.time())
            hour = int(time.strftime("%H", time.localtime()))
            with ThreadPoolExecutor(max_workers=200) as executor:
                executor.submit(wget, url)

# if __name__ == '__main__':
#     for _ in range(200):
#         threading.Thread(target=download).start()

#     time.sleep(999999999999999)
import os
cpus = os.cpu_count()
number_of_threads = cpus * 5
print(cpus)
print(number_of_threads)
