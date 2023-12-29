from playwright.sync_api import Playwright, sync_playwright
import requests
import time
import datetime

def run(playwright: Playwright, url: str) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    page.get_by_role("link", name="立即下载").click()
    page.wait_for_timeout(500)
    with page.expect_download() as download_info:
        page.get_by_text("直接下载").click()
    download = download_info.value
    download_url = download.url
    print(f"下载链接: {download_url}")
    context.close()
    browser.close()

    # 检查URL有效性
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "已开始持续对Url有效性进行检测")
    check_url_validity(download_url)

def check_url_validity(url: str):
    start_time = time.time()
    while True:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code != 200:
                elapsed_time = time.time() - start_time
                print(f"经过{elapsed_time}秒后以上链接失效！")
                break
        except requests.RequestException as e:
            print(f"报错: {e}")
            break
        time.sleep(5)  

def read_urls_from_file(file_path: str):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

with sync_playwright() as playwright:
    urls = read_urls_from_file('url.txt')
    for url in urls:
        run(playwright, url)
