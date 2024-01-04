from playwright.sync_api import Playwright, sync_playwright
import time

def run(playwright: Playwright, browser, url: str) -> None:
    page = browser.new_page()
    page.goto(url)
    page.get_by_role("link", name="立即下载").click()
    page.wait_for_timeout(100)
    with page.expect_download() as download_info:
        page.get_by_text("直接下载").click()
    download = download_info.value
    print(download.url)
    with open('download.txt', 'a') as f:
        f.write(download.url + '\n')
    page.close()

def main(playwright: Playwright, urls: list) -> None:
    browser = playwright.chromium.launch(headless=True)
    for url in urls:
        run(playwright, browser, url)
    browser.close()

def read_urls_from_file(file_path: str):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

start_time = time.time()

with sync_playwright() as playwright:
    urls = read_urls_from_file('url.txt')
    main(playwright, urls)

print('总用时：' + f'{time.time() - start_time:.2f}')

