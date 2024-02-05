import requests


def url_redirect_check(url):
    response = requests.get(url)
    if response.history:
        print(f'发生了重定向，最终URL是: {response.url}')
        return url
    else:
        print('没有发生重定向')
        return None

