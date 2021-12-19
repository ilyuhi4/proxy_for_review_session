import re
from urllib import request

import requests as requests
from flask import Flask, request
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
    # ковыряем контент только для текстов - остальное отдаем неизменно
    if 'text/html' in result.headers['content-type']:
        result = replace_direct_urls(result)
    return result.content


# проверка и редактирование прямых ссылок на другие ресурсы чтобы активный адрес всё равно оставался локальным
def replace_direct_urls(response):
    """Заменяем прямые ссылки main_page на относительные
    :rtype: Response
    """
    soup = BeautifulSoup(response.content, 'lxml')
    for tag in soup.find_all(href=re.compile(main_page)):
        old_string = tag['href']
        new_string = old_string.replace(main_page, '')
        tag['href'] = new_string
    response._content = soup.encode_contents()
    add_tag_to_words(response)
    return response


def add_tag_to_words(response: requests.Response):
    soup = BeautifulSoup(response.content, 'lxml')
    # Нашли все тэги у которых есть строки
    text_tags = soup.findChildren(recursive=True, text=True)
    # бегаем по ним
    for tag in text_tags:
        # проверяем не слишком ли короткая сама строка
        if len(tag.string) > 5:
            result_list = []
            # если не очень, то делим строки на слова по разделителю пробел
            word_list = tag.string.split(' ')
            # смотрим слова на соответствие условию: 6 символов очищенного слова
            for word in word_list:
                # перед редактированием отправляем слово на чистку и получаем обратно очищенное слово с признаком чистки
                # и передаем на редактирование
                if len(word) in (6, 7):
                    # TODO обработать "public.)"
                    cleaned_word = clean_word(word)
                    if len(cleaned_word[0]) == 6 and cleaned_word[0].isalpha():
                        result_list.append(edit_word(cleaned_word, word[-1]))
                    else:
                        result_list.append(word)
                else:
                    result_list.append(word)
            result_tag_string = ' '.join(result_list)
            tag.string.replace_with(result_tag_string)
    response._content = soup.encode_contents()
    return response


# TODO http://127.0.0.1:5000/reply - не работает


def clean_word(word: str) -> tuple:
    """Очистка слова от мусора: слово может быть из 6 символов, но со знаками препинания слитно.
        Возвращаем очищенное слово и признак очистки"""
    if word.replace('.', '') != word:
        return word.replace('.', ''), True
    elif word.replace(',', '') != word:
        return word.replace(',', ''), True
    elif word.replace(':', '') != word:
        return word.replace(':', ''), True
    elif word.replace('!', '') != word:
        return word.replace('!', ''), True
    elif word.replace('?', '') != word:
        return word.replace('?', ''), True
    else:
        return word, False


def edit_word(cleaned_word: tuple, symbol: str) -> str:
    """Производим добавление символа ™ в слово в зависимости от наличия или отсутствия пунктуации"""
    if cleaned_word[1]:
        return cleaned_word[0] + "™" + symbol
    else:
        return cleaned_word[0] + "™"
