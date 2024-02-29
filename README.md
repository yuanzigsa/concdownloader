![image](https://github.com/yuanzigsa/concdownloader/assets/30451380/a1e5a1f2-7cbd-48ef-83d5-4f6746194714)

# 打下行程序-Concdownloader

## 一、项目简介

### 1.1 开发背景

这个项目最起初是因为PCDN业务的特殊性，需要我们在跑业务的时候不能光只有上行流量同时也要增加部分下行流量，所以需要我们在服务器部署下载程序，后来在2023年底，由于运营商策略的调整，限制了出省，我们要继续保证出省流量就得增加大量的下行流量。

Concdownloader不仅实现了定时切换IP进行下载、用户浏览器代理模拟、动态调整下载线程并发数、URL的失效检测，还通过定时调整hosts列表顺序，实现了从全国多节点进行下载的功能。除此之外，为了降低封禁风险，程序还引入了一些机制。这些丰富的功能使得Concdownloader在打下行程序方面发挥了关键作用，为PCDN部分特殊业务提供了长时间的稳定运行。

### 1.2 环境要求

- 系统：centos 7
- python版本：3.6+
- 依赖库：psutil、pysnmp

### 1.3 项目目录结构

```shell
|-- concdownloader.py       # 主程序
|-- res/                    
|   |-- download_url.txt    # 下载url
|-- tests/                  # 测试文件夹，包含所有的测试用例
|   |-- test.py
|-- log/                    # 存放分片日志 
|   |-- concdownloader.log
|-- scripts/        		
|   |-- init.sh             # concdownloader引导部署脚本
|   |-- speed.sh            # url测速
|-- requirements.txt        # 项目所有依赖的库
|-- README.md               # 项目的README文件，描述项目信息、安装步骤和用法等
```

## 二、部署流程

### 2.1 通过skytonOPS部署

1. 在skytonops运维平台“执行任务”，勾选需要部署的机器（如果没有需要先进行添加）

   ![image](https://github.com/yuanzigsa/concdownloader/assets/30451380/fd39547f-acfd-4bf4-9412-fe0ecd618cf9)

2. 选择执行模板“【部署】Concdownloader”

   ![image](https://github.com/yuanzigsa/concdownloader/assets/30451380/c73933e4-b6e0-4a4a-9b52-1b38ad6f6d43)


3. 最后点击“开始执行”即可

   ![image](https://github.com/yuanzigsa/concdownloader/assets/30451380/d1b99ae0-5dd5-4ef7-b580-d44cc221446b)


4. 部署成功后可以通过“`service concdownloader status`”查看状态，该程序会由linux系统下的systemd服务来进行管理

   ![image](https://github.com/yuanzigsa/concdownloader/assets/30451380/fad0f333-42b3-406f-bce6-2b8de94d0770)


### 2.2 手动部署

1. 临时配置linux系统dns

   ```bash
   sudo bash -c 'echo -e "nameserver 114.114.114.114\nnameserver 8.8.8.8\nnameserver 223.5.5.5" > /etc/resolv.conf'
   ```

2. 配置阿里云yum源

   ```bash
   sudo mv -f /etc/yum.repos.d /etc/yum.repos.d.backup
   sudo mkdir /etc/yum.repos.d
   curl -o /etc/yum.repos.d/CentOS-Base.repo -L http://mirrors.163.com/.help/CentOS7-Base-163.repo
   sudo yum clean all
   ```

3. 校准系统时间

   ```bash
   sudo yum install -y ntpdate
   sudo ntpdate time.windows.com
   sudo timedatectl set-timezone Asia/Shanghai
   sudo hwclock --systohc
   ```

4. 安装python3

   ```bash
   sudo yum install -y python3
   ```

5. 安装gcc

   ```bash
   sudo yum install -y gcc python3-devel
   ```

6. 安装wget

   ```bash
   sudo yum install -y wget
   ```

7. 安装python所需的外置库

   ```bash
   pip3 install requests -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   pip3 install pysnmp -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   pip3 install psutil -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   pip3 install colorlog -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   ```

7. 将项目打包文件concdownloader.tar.gz拷贝至/opt/目录下

   ```bash
   cd /opt/
   tar -zxvf  concdownloader.tar.gz
   ```

8. 将下载url写入/opt/concdownloader/res/download_ur.txt文件中

9. 运行程序

   - 使用nohup守护的方式

     ```bash
     nohup python3 concdownloader.py &
     ```

   - 作为系统服务来运行

     - 创建服务配置文件

       ```bash
       vi /etc/systemd/system/concdownloader.service
       ```

     - 写入以下内容

       ```bash
       [Unit]
       Description=Concdownloader
       After=network.target\n\n[Service]
       ExecStart=/usr/bin/python3 /opt/concdownloader/concdownloader.py
       Restart=always
       User=root
       WorkingDirectory=/opt/concdownloader
       
       [Install]
       WantedBy=multi-user.target"
       ```

     - 使得服务生效

       ```bash
       systemctl daemon-reload 
       systemctl enable concdownloader.service
       ```

     - 启动服务

       ```bash
       service concdownloader start
       ```

## 三、功能详解

concdownloader实现了一个多线程的文件下载程序，支持多IP轮询下载，并提供了日志记录和URL可用性检测等功能。他的代码部分主要包括以下功能：

- 配置日志：通过配置日志，方便程序的维护和排查问题。日志文件按天滚动，保留时长为30天。

- 获取本机在线IP：通过psutil库获取本机的在线IP地址。

- 获取CPU闲置率：通过读取/proc/stat文件获取CPU的使用情况，计算出CPU的闲置率。

- 检测URL可用性：通过发送HTTP请求检测URL是否可用，并记录日志。

- 获取下载：从文件中读取下载URL，并使用wget命令进行下载。支持单IP以及多IP自动识别按小时进行轮询下载。

- 定期清理wget进程：定期清理正在运行的wget进程。

- 定期随机排列hosts列表：定期随机排列/etc/hosts文件中的内容。

- 检测当前URL可用性：定期检测URL的可用性。


代码的主要逻辑是在主函数中创建多个线程，每个线程执行不同的任务。其中，kill_wget函数用于清理wget进程，random_hosts_list函数用于随机排列hosts列表，urls_vaild_check函数用于检测URL的可用性。wget函数用于执行下载任务，通过调用wget命令进行文件下载。

## 四、配置维护

### 4.1 download_url的不定期更新

因为url面临随时失效和被封禁的可能性，所以需要不定期对url进行更新，通过skytonops运维平台执行模板“查询url数量”也可以查询到url剩余可用数量

### 4.2 hosts文件的不定期更新

同理hosts也面临随时失效的可能性，因此也需要不定期对其进行更新，通过skytonops运维平台执行解析，并再次分发即可。











