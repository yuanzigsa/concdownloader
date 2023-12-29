#!/bin/bash
urls_file="soft_speed.txt"
output_file="download_speeds.txt"
> $output_file
max_concurrent_downloads=10
timeout_seconds=180

count=0
while IFS= read -r url
do
    download_task() {
        download_speed=$(timeout "$timeout_seconds" wget -O /dev/null -o /dev/stdout "$url" 2>&1 | grep -oP '\d+\.\d+ [KM]B/s' | tail -n 1)
        echo "$url $download_speed" >> "$output_file"
    }
    download_task &
    count=$((count + 1))

    if [ $count -eq $max_concurrent_downloads ]; then
        wait
        count=0
    fi
done < "$urls_file"

wait
echo "下载速度测试完成。结果保存在 $output_file 中。"

