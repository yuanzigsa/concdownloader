#!/bin/bash

# 修改 /etc/resolv.conf 为特定的 nameserver
echo "nameserver 218.203.123.116" | sudo tee /etc/resolv.conf

# 安装 Python 3
sudo yum install -y python3

# 安装 gcc 和 python3-devel
sudo yum install -y gcc python3-devel

sudo yum install -y wget

# 使用阿里云源安装 psutil
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ psutil
