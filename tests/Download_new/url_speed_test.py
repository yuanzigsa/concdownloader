import subprocess

urls_file = "soft_speed.txt"
output_file = "download_speeds.txt"
max_concurrent_downloads = 10
timeout_seconds = 180

count = 0
with open(output_file, "w") as f:
    with open(urls_file, "r") as urls:
        for url in urls:
            url = url.strip()

            def download_task(url):
                download_speed = subprocess.check_output(
                    f"timeout {timeout_seconds} wget -O /dev/null -o /dev/stdout {url} 2>&1 | grep -oP '\\d+\\.\\d+ [KM]B/s' | tail -n 1",
                    shell=True,
                    universal_newlines=True
                )
                f.write(f"{url} {download_speed}\n")

            download_task(url)
            count += 1

            if count == max_concurrent_downloads:
                count = 0

print(f"下载速度测试完成。结果保存在 {output_file} 中。")
