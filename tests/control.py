import sys
import logging


# 获取命令行参数
if len(sys.argv) < 2:
    logging.warning(
        "可以直接使用命令来进行指定下载类型，如：python3 concdownloader ipv6 或者 pyhon3 concdownloader all，默认ipv4下载")
    downtype = 'ipv4'
else:
    downtype = sys.argv[1]
if "ipv4" or "ipv6" or "all" in downtype:
    downtype = downtype
else:
    logging.info("输入无效，程序退出！")

if downtype == 'ipv4':
    print("ipv4")

if downtype == 'ipv6':
    print("ipv6")

if downtype == 'all':
    print("all")