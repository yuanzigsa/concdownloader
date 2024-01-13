#!/bin/bash
#===============================================================================
# Date：Jan. 11th, 2024
# Author : yuanzi
# Description: 初始化系统，提供auto_downloader运行环境
#===============================================================================

# 定义日志函数
get_current_time() {
    echo "$(date "+%Y-%m-%d %H:%M:%S")"
}
log_info() {
    echo -e "$(get_current_time) \e[32mINFO\e[0m: $1"
}

log_error() {
    echo -e "$(get_current_time) \e[31mERROR\e[0m: $1"
}

log_warning() {
    echo -e "$(get_current_time) \e[33mWARNING\e[0m: $1"
}

log_info "执行开始..."
# 检查是否以root用户身份运行
if [[ $EUID -ne 0 ]]; then
    log_error "请以root用户身份运行此脚本"
    exit 1
fi

# 配置dns
config_dns() {
    sudo bash -c 'echo -e "nameserver 114.114.114.114\nnameserver 8.8.8.8\nnameserver 223.5.5.5" > /etc/resolv.conf'
    log_info "已将DNS配置为114.114.114.114和8.8.8.8以及223.5.5.5"
}

# 配置阿里云yum源
config_yum(){
  sudo mv -f /etc/yum.repos.d /etc/yum.repos.d.backup
  sudo mkdir /etc/yum.repos.d
  curl -o /etc/yum.repos.d/CentOS-Base.repo -L http://mirrors.163.com/.help/CentOS7-Base-163.repo
  sudo yum clean all
  sudo yum makecache
  log_info "yum源已经设置完成！"
}

# 校准时间
check_time() {
    log_info "开始检查系统时间..."
    sudo yum install -y ntpdate
    sudo ntpdate time.windows.com
    sudo timedatectl set-timezone Asia/Shanghai
    sudo hwclock --systohc
    log_info "已校准系统时间"
}

# 检查服务状态
check_auto_downloader_service() {
    status=$(service auto_downloader status > /dev/null 2>&1 && echo "active" || echo "inactive")
    if [ "$status" = "active" ]; then
        log_info "检测到auto_downloader已经处于Active状态。\n"
        service auto_pcdn status -l
        answer=""
        if timeout 10 read -t 10 -p "是否清除之前的所有部署，重新进行部署？ (y/n): " answer; then
            if [ "$answer" = "y" ]; then
                log_info "重新部署操作已被取消。"
                exit 1
            fi
        else
            log_info "等待用户输入超时，重新部署操作已被取消。"
            exit 1
        fi
    fi
    return 0
}

# python3环境部署及所需外置库的安装
install_python3_env() {
    log_info "开始安装python3..."
    sudo yum install -y python3
    log_info "python3已安装"

    log_info "开始安装gcc..."
    sudo yum install -y gcc python3-devel
    log_info "gcc已安装"

    log_info "开始安装python所需的外置库..."
    pip3 install requests -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
    pip3 install pysnmp -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
    pip3 install psutil -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
    pip3 install colorlog -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
    log_info "python所需的外置库已全部安装"
}

# 创建服务并运行
create_systemd_service() {
    script_path="/opt/auto_downloader/auto_downloader.py"
    log_info "开始将auto_downloader写进系统服务运行..."
    service_content="[Unit]\nDescription=AutoDownloader\nAfter=network.target\n\n[Service]\nExecStart=/usr/bin/python3 $script_path\nRestart=always\nUser=root\nWorkingDirectory=/opt/auto_downloader\n\n[Install]\nWantedBy=multi-user.target\n"
    service_file_path='/etc/systemd/system/auto_downloader.service'
    echo -e "$service_content" > "$service_file_path"

    systemctl daemon-reload &> /dev/null
    systemctl enable auto_downloader.service
    log_info "AutoDownloader程序已创建并写进系统服务并设置成开机自启"
}

# 检查日志文件
check_log() {
    log_file="/opt/auto_downloader/log/auto_downloader.log"
    search_string="运维监控数据采集"
    timeout=60  # 设置超时时间为60秒
    elapsed_time=0

    while [ $elapsed_time -lt $timeout ]; do
        # 检查日志文件中是否包含特定字符
        if grep -q "$search_string" "$log_file"; then
            sleep 10
            log_info "执行结束！"
            break
        fi
        sleep 1
        ((elapsed_time++))
    done
    sleep 1
    if [ $elapsed_time -ge $timeout ]; then
        log_error "超时退出...请检查！"
    fi
}

# 部署AutoPCDN程序
deploy_auto_downloader() {
    # 下载auto_pcdn脚本程序
    mkdir -p /opt/auto_downloader/
    curl -o /opt/auto_downloader/auto_downloader.tar.gz -L https://gitee.com/yuanzichaopu/auto-downloader/releases/download/autodownloader/auto_downloader.tar.gz
    log_info "auto_downloader程序包下载完成"
    # 解压
    cd /opt/auto_downloader/ || exit
    tar -zxvf  auto_downloader.tar.gz
    mv -f hosts /etc/hosts
    sudo yum install -y wget
    log_info "已安装wget"
    sudo yum install -y lrzsz
    log_info "已安装lrzsz"
    # 安装yum源插件
    yum install yum-fastestmirror -y
    log_info "已安装yum源自动选择插件，会自动优先选择最快的yum源"
    # 安装基础环境
    install_python3_env
    # 启动服务并检查日志
#    touch /opt/auto_pcdn/log/auto_downloader.log
    create_systemd_service
#    tail -f /opt/auto_pcdn/log/auto_downloader.log &
#    TAIL_PID=$!
#    check_log
#    kill $TAIL_PID
}

# 配置dns确保正确解析域名
config_dns

# 配置yum
config_yum

# 校准时间时区
check_time

deploy_auto_downloader

# 部署AutoDownloader程序(如果未部署)
#if check_auto_downloader_service; then
#    deploy_auto_downloader
#fi



