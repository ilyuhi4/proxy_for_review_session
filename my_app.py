from urllib import request

import requests as requests
from flask import Flask
from markupsafe import escape

app = Flask(__name__)
main_page = 'https://news.ycombinator.com/'


@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/test/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return 'Путь запроса %s' % escape(subpath)


@app.route('/<path:subpath>')
def xakep_main_page(subpath: str) -> bytes:
    """Main view function that redirects requests from local server to remote in main_page global variable
    :subpath: str - string from address without http://127.0.0.1/
    :rtype: bytes
    """
    print('Идем развлекаться на Xakep NEWS')
    print(f'Путь поиска страницы: {subpath}')
    # status_code = get_page_from_xakep(subpath)
    # return f'Идем на Xakep NEWS!     \nStatus code is: {get_page_from_xakep(subpath)}'
    return get_page_from_xakep(subpath).content


def get_page_from_xakep(subpath: str) -> requests.Response:
    """
    Returns the result of GET request to the remote page
    :rtype: requests.Response
    """
    current_page = main_page + subpath
    print(f'Полезли на Xakep тащить страницу: {subpath}')
    result = requests.get(current_page)
    print('Код ответа:', result.status_code)
    print('Утащили ', (len(result.content)), 'символов')
    print('Отправил контент обратно')
    return result
