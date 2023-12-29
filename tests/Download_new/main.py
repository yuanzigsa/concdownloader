import os, re, time, random
import threading

def wget():
    while True:
        time.sleep(1)
        urls = open('soft.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
            localtime = time.localtime(time.time())
            hour = int(time.strftime("%H", time.localtime()))
            cmd = "wget -q --user-agent='Mozilla/5.0' -O /dev/null '" + url + "'"
            os.popen(cmd)

def kill_wget():
    while True:
        os.popen('pkill  wget')
        print('pkill  wget')
        sec = random.randint(10, 20)
        time.sleep(sec)

kill_wget_thread = threading.Thread(target=kill_wget)
kill_wget_thread.start()

for _ in range(200):  # 创建一些线程
    threading.Thread(target=wget).start()

time.sleep(999999999999999)
