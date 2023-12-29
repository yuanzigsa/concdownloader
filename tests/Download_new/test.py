import re
import os
import sys
import json
import time
import struct
import socket
import logging
import requests
import threading
import subprocess

# 控制节点基础信息获取与推送的API接口
get_pppoe_basicinfo_api_url = "http://122.191.108.42:9119/orion/expose-api/machine-info/get-config"
update_pppline_api_url = "http://122.191.108.42:9119/orion/expose-api/machine-info/update-pppline"
update_dial_connect_api_url = "http://122.191.108.42:9119/orion/expose-api/machine-info/update-dial-connect"

# 配置日志以方便维护
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler('auto_pppoe.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)


machineTag = "DSIX30NGF"
def get_pppoe_basicinfo_from_control_node():
    headers = {
        "O-Login-Token": "accessToken",
        "accessToken": "ops_access"
    }
    params = {
        "machineTag": f"{machineTag}"
    }
    try:
        response = requests.get(get_pppoe_basicinfo_api_url, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        pppoe_basicinfo = response_data.get("data", {})
        if pppoe_basicinfo is not None:
            logging.info("从控制节点获取配置信息成功")
            return pppoe_basicinfo
        else:
            logging.error("从控制节点获取配置信息失败，返回数据为空，请检查本机系统获取的SN是否与控制节点记录的一致")
            sys.exit(1)
    except requests.RequestException as e:
        logging.error("从控制节点获取配置信息失败，错误信息：%s", str(e))
        sys.exit(1)


import re

original_value = " v 5   "
cleaned_value = re.sub(r'\s+', '', original_value)
print(cleaned_value)
