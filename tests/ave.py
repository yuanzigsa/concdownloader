import time
import random

def chunk_list(lst, chunk_size):
    avg_chunk_size = len(lst) // chunk_size
    remainder = len(lst) % chunk_size

    chunks = []
    start = 0
    for i in range(chunk_size):
        if i < remainder:
            end = start + avg_chunk_size + 1
        else:
            end = start + avg_chunk_size
        chunks.append(lst[start:end])
        start = end

    return chunks

# 示例列表
my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,20,30,40,50,60,70,80]

# 将列表平均分成 10 份
result = chunk_list(my_list, 1)
print(result)


x = 10

print(x)
def modify_global_variable():
    global x  # 声明 x 是全局变量
    x = 20  # 修改全局变量 x 的值

modify_global_variable()
print(x)  # 输出 20


url_list = [['http://www.python.org', 'http:'], ['http://www.python.org', 'https:']]
ip_list = ['192.168.3.11', '1.1.1.1']

ip_url = {}
x = 0
for ip in ip_list:
    ip_url[ip] = url_list[x]
    x += 1

print(ip_url)

url_list = [['http://www.baidu.org', 'http:'], ['http://www.python.org', 'https:']]
ip_list = ['192.168.3.11', '1.1.1.1']

ip_url = {}
for ip, url in zip(ip_list, url_list):
    ip_url[ip] = url

print(ip_url)

url_list = [['tencent.com', 'taobao.com'], ['python.org', 'baidu.com'], ['alibaba.com', 'jd.com', 'abc.com']]
ip_list = ['192.168.3.11', '1.1.1.1', '8.8.8.8']

ip_url = {}
i = 0

while True:
    for j in range(len(ip_list)):
        ip_url[ip_list[j]] = url_list[(j + i) % len(url_list)]
    time.sleep(2)  # 暂停 60 秒，即一分钟
    i += 1

    print(random.choice(ip_url.get('192.168.3.11')))


