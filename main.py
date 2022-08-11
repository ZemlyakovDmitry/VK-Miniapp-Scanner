import re
from typing import Dict, List, Optional

import requests as r
import jsbeautifier
import utils

IGNORE_WORD_LIST: List[str] = [
    'yandexMap', 'VKWebApp', 'reactInternal', 'component', 'Icon', 'Browser', 'Scroll',
    'get', 'Location', 'Panel', 'Point', 'Hook', 'animat', 'remove', 'event', 'mouse',
    'refresh', 'padding', 'child'
]
IGNORE_URL_LIST: List[str] = ['w3.org', 'reactjs.org']
SCRIPT_FAILURE_MSG: str = 'Seems like smth is broken. Please copy an error below' \
    ' and report it to me by using GitHub, https://vk.com/zema or https://t.me/damnware. Thanks!'
MAX_INPUT_ATTEMPTS: int = 3  # Define your own number of attempts


def main() -> None:
    input_data = utils.input_handler(MAX_INPUT_ATTEMPTS)
    if input_data is None:
        return

    scripts_url: List[str] = utils.get_list_of_scripts(input_data['base_url'])
    print(f'List of scripts URL: {scripts_url}')
    check_scripts_links(scripts_url, input_data['scan_type'])
    print('Finished scanning!')


def check_scripts_links(scripts_url: List[str], scan_type: str) -> None:
    dict_with_possible_tokens: Dict[str, List[str]] = {}

    for url in scripts_url:
        try:
            script_text: str = r.get(url).text
            beautified_lines: str = jsbeautifier.beautify(
                script_text).splitlines()
            list_of_tokens = scan_script(beautified_lines, scan_type)
            if list_of_tokens is not None:
                dict_with_possible_tokens[url] = list_of_tokens
        except r.exceptions.RequestException as request_error:
            print(f'{SCRIPT_FAILURE_MSG}\nHere are error details: {request_error}')
        except TypeError as splitlines_error:
            print(f'{SCRIPT_FAILURE_MSG}\nHere are error details: {splitlines_error}')

    if dict_with_possible_tokens:
        print('Found some possible tokens:')
        for i, (key, value) in enumerate(dict_with_possible_tokens.items()):
            print(f'{i + 1}. URL: {key}\nTokens: {value}\n')


def scan_script(beautified_lines: List[str], scan_type: str) -> Optional[List[str]]:
    third_option_list: List[str] = []
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
                for word in regex_find_result:
                    third_option_list.append(word)

    if len(third_option_list) > 0:
        return third_option_list
    return None


if __name__ == '__main__':
    main()
