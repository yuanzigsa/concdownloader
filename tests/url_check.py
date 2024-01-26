import
import requests
def urls_check():
    def url_check(url):
        result = requests.get(url, stream=True)
        if result.status_code == 200:
            # 文件总大小
            # total_size = int(result.headers.get('Content-Length', 0))
            # mb_size = total_size / 1024 / 1024
            # mb_size = round(mb_size, 2)
            # print(f"文件总大小: {mb_size}MB")
            return url
        else:
            print(f"失效url（错误码:{result.status_code}）：{url} ")


    def get_urls():
        urls = []
        with open('../res/download_url.txt', 'r') as f:
            for url in f.readlines():
                if "http" in url:
                    urls.append(url.strip())
        return urls


    def start_check(urls):
        with open('../res/download_url.txt', 'w') as f:
            for url in urls:
                vaild_url = url_check(url)
                if vaild_url:
                    f.writelines(vaild_url + '\n')


        urls = get_urls()
        print(f"当前url数量: {len(urls)}")
        start_check(urls)
        urls = get_urls()
        print(f"经检测有效url数量: {len(urls)}")
        with open('url_vaild.info', 'w') as f:
            f.write(f"当前可用url数量: {len(urls)}\n")

urls_check()


