# @Author  : yuanzi
# @Time    : 2024/10/20 9:09
# Website: https://www.yzgsa.com
# Copyright (c) <yuanzigsa@gmail.com>
import subprocess
from modules.speed_limit import get_network_interfaces


def remove_speed_limit():
    interfaces = get_network_interfaces()
    for interface in interfaces:
        command = f"tc qdisc del dev {interface} ingress"
        command2 = f"tc qdisc del dev {interface} root"
        subprocess.run(command, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command2, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
