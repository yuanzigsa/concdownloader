import os, re, time, random
import threading

def curl():
    while True:
        time.sleep(1)
        urls = open('soft.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
            localtime = time.localtime(time.time())
            hour = int(time.strftime("%H", time.localtime()))
            cmd = "curl -s -A 'Mozilla/5.0' -o /dev/null '" + url + "'"
            os.popen(cmd)

def kill_curl():
    while True:
        os.popen('pkill  curl')
        print('pkill  curl')
        sec = random.randint(10, 20)
        time.sleep(sec)

kill_curl_thread = threading.Thread(target=kill_curl)
kill_curl_thread.start()

for _ in range(200):  # 创建一些线程
    threading.Thread(target=curl).start()

time.sleep(999999999999999)