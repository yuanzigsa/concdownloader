#!/usr/bin/python
#coding=utf-8
import os,re,time,random
import threading
import itertools


# 创建一个无限迭代器
ip_pool = itertools.cycle(['221.233.216.14', '221.233.216.15', '221.233.216.16', '221.233.216.17', '221.233.216.18'])


def wget():
    while True:
        time.sleep(1)
        urls=open('soft.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url='http'+urls[0].replace('\n','').replace('\r\n','').split('http')[-1]
            localtime = time.localtime(time.time())
            hour=int(time.strftime("%H", time.localtime()))
            # 获取下一个IP
            ip = next(ip_pool)
            cmd="wget  --bind-address="+ip+" -q --user-agent='Mozilla/5.0' -O /dev/null '"+url+"'"
            os.popen(cmd)

                            
def kill_wget():
    while True:
        os.popen('pkill  wget')
        print('pkill  wget')
        sec=random.randint(10,20)

        time.sleep(sec)


kill_wget_thread = threading.Thread(target=kill_wget)
kill_wget_thread.start()

for _ in range(100):  # 创建线程，所创建的线程数量根据机器性能决定
    threading.Thread(target=wget).start()

time.sleep(999999999999999)
