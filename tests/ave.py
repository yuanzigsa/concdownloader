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



import time
from itertools import cycle

import time
from itertools import cycle

url_list = [['tencent.com', 'taobao.com'], ['python.org', 'baidu.com'], ['alibaba.com', 'jd.com', 'abc.com']]
url_cycle = cycle(url_list)

while True:
    current_urls = next(url_cycle)
    for url in current_urls:
        print(url)
    print("------------")
    time.sleep(1)  # 暂停60秒
