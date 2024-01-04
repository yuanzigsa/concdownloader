import time


# 获取cpu闲置率
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
    time.sleep(0.1)
    new_times = read_cpu_times()
    idle_value = calculate_idle_percentage(old_times, new_times)
    return idle_value


print(get_cpu_idle_value())