# @Author  : yuanzi
# @Time    : 2024/9/14 14:18
# Website: https://www.yzgsa.com
# Copyright (c) <yuanzigsa@gmail.com>
import threading
import random
import time


def demo1():
    while True:
        print(f"demo1:{number}")
        time.sleep(1)


def demo2():
    # global number
    while True:
        number = random.choice(numbers)
        print(f"demo2:{number}")
        time.sleep(1)


if __name__ == '__main__':
    numbers = [1, 2, 3, 4, 5]
    number = random.choice(numbers)
    # threading.Thread(target=demo1).start()
    # threading.Thread(target=demo2).start()
    print(random.sample(numbers,3))
