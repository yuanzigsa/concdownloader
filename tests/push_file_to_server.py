import os
import paramiko
from scp import SCPClient
import threading
import json

def run_command_on_server(server, command, output_dict):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])
        
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        result = f"在 {server['host']} 上执行命令的输出：\n{output if output else error}"
        
    except Exception as e:
        result = f"在 {server['host']} 上执行命令失败: {e}"
    finally:
        ssh.close()
        output_dict[server['host']] = result

def put_file_to_server(filename, remote_path="/root/"):
    local_file_path = filename
    remote_file_path = os.path.join(remote_path, filename)
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_file_path, remote_file_path)
        print(f"文件已成功传输到 {server['host']}")
    except Exception as e:
        print(f"传输到 {server['host']} 失败: {e}")
    finally:
        ssh.close()


if __name__ == '__main__':
    # JSON文件路径
    json_file_path = '../../res/server_login_info.json'
    with open(json_file_path, 'r') as file:
        servers = json.load(file)

    # 创建线程列表和输出字典
    threads = []
    outputs = {}

    # 传输文件到每个服务器并执行命令
    for server in servers:
        # 假设要执行的命令是 "bash env.sh"
        # command = "sudo nohup python3 download_multi-ip_rotate.py &"

        command = "ls"

        put_file_to_server("download_multi-ip_rotate.py")
        

        # 创建线程
        thread = threading.Thread(target=run_command_on_server, args=(server, command, outputs))
        threads.append(thread)
        thread.start()


    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 打印每个服务器的输出
    for server, output in outputs.items():
        print(output)

    print("所有命令执行完成。")
