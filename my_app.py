from urllib import request

import lxml
import requests as requests
from flask import Flask, request
from markupsafe import escape
from bs4 import BeautifulSoup

app = Flask(__name__)
main_page = 'https://news.ycombinator.com/'

@app.route('/')
@app.route('/<path:subpath>')
def xakep_main_page(subpath: str = '') -> bytes:
    """Main view function that redirects requests from local server to remote in main_page global variable
    :subpath: str - string from address without http://127.0.0.1/
    :rtype: bytes
    """
    # GET параметры теряются нужно дополнительно передавать
    # http://127.0.0.1:5000/user?id=atamyrat
    return get_page_from_xakep(subpath=subpath, params=dict(request.values.items()))


def get_page_from_xakep(subpath: str, params: dict) -> bytes:
    """
    Returns the result of GET request to the remote page
    :type params: dict
    :type subpath: str or path
    """
    current_page = main_page + subpath
    result = requests.get(current_page, params=params)
    if result.headers['content-type'] == 'text/html':
        result = replace_direct_urls(result)
    return result.content


# проверка и редактирование прямых ссылок на другие ресурсы чтобы активный адрес всё равно оставался локальным
def replace_direct_urls(response):
    """Заменяем прямые ссылки main_page на относительные
    :rtype: Response
    """
    soup = BeautifulSoup(response.content, 'lxml')
    for tag in soup.find_all('a'):
        if main_page in str(tag['href']):
            old_string = tag['href']
            new_string = old_string.replace(main_page, '')
            tag['href'] = new_string
        response._content = soup.encode_contents()
    return response


def add_tag_to_words(response: requests.Response):
    pass

# TODO http://127.0.0.1:5000/reply - не работает
