import random

ip_list = ['27.24.175.18', '27.24.175.21', '61.136.184.2', '61.136.184.3', '192.168.1.1', '8.8.8.8', '123.123.123.123', '36.35.3.1']
ip_pool = random.sample(ip_list, 5)

while True:
    current_ip = random.choice(ip_pool)
    print(current_ip)

