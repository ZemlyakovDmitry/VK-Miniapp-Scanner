import re
from typing import List, Optional

import requests as r
import bs4
import jsbeautifier
import utils

IGNORE_WORD_LIST: List[str] = ['yandexMap', 'VKWebApp', 'reactInternal', 'component', 'Icon', 'Browser', 'Scroll', 'get',
                               'Location', 'Panel', 'Point', 'Hook', 'animat', 'remove', 'event', 'mouse', 'refresh', 'padding',
                               'child']

IGNORE_URL_LIST: List[str] = ['w3.org', 'reactjs.org']
SCRIPT_FAILURE_MSG: str = 'Seems like smth is broken. Please copy an error below and report it to me'
'by using GitHub, https://vk.com/zema or https://t.me/damnware. Thanks!'


def main() -> None:
    scripts_url: List[str] = []

    base_url: str = input('URL?\n').split('?')[0]
    is_url_valid: bool = utils.validate_url(base_url)
    if not is_url_valid:
        return

    scan_type: str = input(
        'Select scan type(s)\n '
        '1 - Hardcoded VK Token and Params\n '
        '2 - Links \n '
        '3 - possible tokens \n')
    if not scan_type:
        print('bro wtf, define scan type')
        return

    text: str = r.get(base_url).text
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(text, features='html.parser')
    scripts: bs4.element.ResultSet = soup.find_all('script')
    srcs: List[str] = [link['src'] for link in scripts if 'src' in link.attrs]

    for attribute in srcs:
        if "index.html" in base_url:
            base_url = base_url[:-10]

        if attribute[0:2] == "./" or attribute[0:2] == "..":
            attribute = attribute[2:]
        elif "/" not in attribute[0:2] and attribute[0:4] != "http":
            attribute = "/" + attribute

        if "http" not in attribute:
            url = base_url + attribute
            scripts_url.append(url)
        else:
            scripts_url.append(attribute)

    jser(scripts_url, scan_type)


def jser(scripts_url, scan_type) -> None:
    print(f'List of scripts URL: {scripts_url}')

    for file in scripts_url:
        try:
            script_text: str = r.get(file).text
            beautified_lines: str = jsbeautifier.beautify(
                script_text).splitlines()
            scanner(beautified_lines, scan_type)
        except Exception as e:
            # Better to specify exception
            # Check https://pylint.pycqa.org/en/latest/user_guide/messages/warning/broad-except.html and which exceptions can be raised here
            print(f'{SCRIPT_FAILURE_MSG}\nHere are error details: {e}')
            pass


def scanner(beautified_lines, scan_type):
    for line in beautified_lines:
        if "1" in scan_type:
            line_lstrip: str = line.lstrip()
            if "vk1.a." and "vk_access_token_settings=" in line:
                print(f"Found hardcoded VK Token and params:\n{line_lstrip}")
            elif "vk1.a." in line:
                print(f"Found hardcoded VK Token:\n{line_lstrip}")
            elif "vk_access_token_settings=" in line:
                print(f"Found hardcoded params at line:\n{line_lstrip}")
        if "2" in scan_type:
            regex_find_result: list[str] = re.findall(
                r"(http|ftp|https)://([\w_-]+(?:\.[\w_-]+)+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])", line)
            if regex_find_result and not any(url.lower() in line.lower() for url in IGNORE_URL_LIST):
                regex_search_result: Optional[re.Match[str]] = re.search(
                    "(?P<url>https?://\S+)", line).group("url")
                print(f"Found link: {regex_search_result}")
        if "3" in scan_type:
            regex_find_result: list[str] = re.findall(
                r"[a-zA-Z\d]{25,100}", line)
            if regex_find_result and not any(
                    word.lower() in line.lower() for word in IGNORE_WORD_LIST):
                print(regex_find_result)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Better to handle exceptions in the main method
        # Check https://pylint.pycqa.org/en/latest/user_guide/messages/warning/broad-except.html
        print(f'{SCRIPT_FAILURE_MSG}\nHere are error details: {e}')
