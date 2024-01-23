import os, re, time, random
import threading


def wget():
    while True:
        time.sleep(1)
        urls = open('./url_v1.1.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
            # user_agent = random.choice(USER_AGENTS)
            cmd = f"wget -q --user-agent='Mozilla/5.0' -O /dev/null '{url}'"
            os.popen(cmd)

def kill_wget():
    while True:
        os.popen('pkill  wget')
        print('pkill  wget')
        sec = random.randint(10, 20)
        time.sleep(sec)

kill_wget_thread = threading.Thread(target=kill_wget)
kill_wget_thread.start()

cpus = os.cpu_count()
number_of_threads = cpus * 5

for _ in range(number_of_threads):  # 创建一些线程
    threading.Thread(target=wget).start()

time.sleep(999999999)


## 1.增加wget下载循环的cpu闲置判断  2.定期杀死一部分睡眠进程
import os, re, time, random
import threading

def wget():
    while True:
        if get_cpu_idle_value() > 5:
            # print('cpu有空闲，新增任务')
            urls = open('./url_v1.1.txt').readlines()
            random.shuffle(urls)
            if 'http' in urls[0]:
                url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
                cmd = f"wget -q --user-agent='Mozilla/5.0' -O /dev/null '{url}'"
                os.popen(cmd)
                # cmd = ["wget", "-q", "--user-agent='Mozilla/5.0'", "-O", "/dev/null", url]
                # subprocess.run(cmd)

def kill_wget():
    while True:
        time.sleep(300)
        try:
            ps_output = os.popen('ps aux').read()
            ps_lines = ps_output.split('\n')

            sleeping_processes = []
            for line in ps_lines:
                if 'wget' in line and 'S' in line:
                    process_id = int(line.split()[1])
                    sleeping_processes.append(process_id)
            num_sleeping_processes = len(sleeping_processes)

            if num_sleeping_processes > 600:
                processes_to_kill = sleeping_processes[:num_sleeping_processes-200]
                for process_id in processes_to_kill:
                    os.popen(f'kill {process_id}')
                    # print(f'杀死睡眠进程 {process_id}')
        except Exception as e:
            print(f"错误: {e}")

def get_cpu_idle_value():
    def read_cpu_times():
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu '):
                    parts = line.split()
                    cpu_times = [int(p) for p in parts[1:]]
                    return cpu_times

    def calculate_idle_percentage(old_times, new_times):
        total_time_diff = sum(new_times) - sum(old_times)
        idle_time_diff = new_times[3] - old_times[3]
        idle_percentage = 100 * (idle_time_diff / total_time_diff)
        idle_value = int(idle_percentage)
        return idle_value
    
    old_times = read_cpu_times()
    time.sleep(1)
    new_times = read_cpu_times()
    idle_value = calculate_idle_percentage(old_times, new_times)
    
    return idle_value

kill_wget_thread = threading.Thread(target=kill_wget)
kill_wget_thread.start()    

cpus = os.cpu_count()
for _ in range(cpus * 5):
    threading.Thread(target=wget).start()




## 去除wget下载循环的cpu闲置判断
import os, re, time, random
import threading

def wget():
    while True:
        urls = open('./url_v1.1.txt').readlines()
        random.shuffle(urls)
        if 'http' in urls[0]:
            url = 'http' + urls[0].replace('\n', '').replace('\r\n', '').split('http')[-1]
            cmd = f"wget -q --user-agent='Mozilla/5.0' -O /dev/null '{url}'"
            os.popen(cmd)

def clear_sleeping_wget_process():
    while True:
        time.sleep(300)
        try:
            ps_output = os.popen('ps aux').read()
            ps_lines = ps_output.split('\n')

            sleeping_processes = []
            for line in ps_lines:
                if 'wget' in line and 'S' in line:
                    process_id = int(line.split()[1])
                    sleeping_processes.append(process_id)
            num_sleeping_processes = len(sleeping_processes)

            if num_sleeping_processes > 600:
                processes_to_kill = sleeping_processes[:num_sleeping_processes-200]
                for process_id in processes_to_kill:
                    os.popen(f'kill {process_id}')
                    # print(f'杀死睡眠进程 {process_id}')
        except Exception as e:
            print(f"错误: {e}")

def kill_wget():
    while True:
        time.sleep(300)
        os.popen('pkill  wget')

def cpu_limit_python_process():
    process_id = os.getpid('python')
    os.popen(f'cpulimit -l 10 -p {process_id} &')
    
kill_wget_thread = threading.Thread(target=clear_sleeping_wget_process)
kill_wget_thread.start()    
cpu_limit_python_process()
cpus = os.cpu_count()
for _ in range(80):
    threading.Thread(target=wget).start()