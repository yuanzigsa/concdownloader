# @Author  : yuanzi
# @Time    : 2024/9/29 22:17
# Website: https://www.yzgsa.com
# Copyright (c) <yuanzigsa@gmail.com>
import json
import logging
import subprocess
import time
from datetime import datetime
import psutil


# 获取接口实时下行速率
def get_real_time_download_rate(interface, interval=1):
    try:
        # 读取当前接收字节数
        with open(f"/sys/class/net/{interface}/statistics/rx_bytes", "r") as f:
            initial_rx_bytes = int(f.read().strip())

        # 等待指定的时间间隔
        time.sleep(interval)

        # 再次读取接收字节数
        with open(f"/sys/class/net/{interface}/statistics/rx_bytes", "r") as f:
            final_rx_bytes = int(f.read().strip())

        # 计算字节变化量
        bytes_received = final_rx_bytes - initial_rx_bytes

        # 将字节转换为位（1 字节 = 8 位），再转换为 Mbps
        download_rate_mbps = (bytes_received * 8) / (interval * 1000000)  # Mbps
        logging.info(f"{interface}当前实时下行速率：{download_rate_mbps}Mbps")
        return download_rate_mbps

    except Exception as e:
        logging.error(f"获取实时下行速率失败: {e}")
        return None


# 通过tc命令添加限速规则 (kbit/s)
def limit_bandwidth(interface, rate_mbps):
    try:
        # 删除现有的流量控制规则
        subprocess.run(f"tc qdisc del dev {interface} root", shell=True, stderr=subprocess.DEVNULL)

        # 添加限速规则，将带宽限制为 rate kbit/s
        rate_kbits = rate_mbps * 1000
        subprocess.run(
            f"tc qdisc add dev {interface} root tbf rate {rate_kbits}kbit burst 32kbit latency 400ms",
            shell=True, check=True
        )
        logging.info(f"{interface} 限速已设置为 {rate_kbits} kbit/s")
    except subprocess.CalledProcessError as e:
        logging.error(f"设置限速失败 on {interface}: {e}")
    except Exception as e:
        logging.error(f"其他错误 {interface}: {e}")


# 获取所有网络接口，排除lo（本地回环接口）
def get_network_interfaces():
    interfaces = psutil.net_if_addrs()
    return [iface for iface in interfaces if iface != "lo"]


# 定义限速策略，按时间段调整带宽
def apply_bandwidth_limit(speed_limit_list):
    interfaces = get_network_interfaces()
    current_time = datetime.now().time()

    with open('speed_limit.info', 'r') as file:
        speed_limit_info = json.load(file)

    # 遍历 speed_limit 中的每个时间段
    for index, period in enumerate(speed_limit_list):
        for time_range, limit_factor in period.items():
            start_time_str, end_time_str = time_range.split('-')
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            # 如果当前时间在该时间段内，应用对应的限速
            if start_time <= current_time <= end_time:
                for interface in interfaces:
                    real_max_rate = get_real_time_download_rate(interface)
                    if real_max_rate and speed_limit_info[index][json.dumps(period)] is not True:
                        limit_bandwidth(interface, int(real_max_rate * limit_factor))  # 限速为指定比例
                        speed_limit_info.append({json.dumps(period): True})
                break
    else:
        # 如果不在任何限速时间段内，恢复全速
        for interface in interfaces:
            limit_bandwidth(interface, get_real_time_download_rate(interface))  # 恢复全速

    with open('speed_limit.info', 'w') as file:
        json.dump(speed_limit_info, file, indent=4)
