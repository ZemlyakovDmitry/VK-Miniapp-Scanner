from typing import Dict, List, Union, Optional
from validators import url as validate_url, ValidationFailure
from requests import get
from bs4 import BeautifulSoup


def input_handler(max_input_attempts: int) -> Optional[Dict[str, str]]:
    input_attempts = 0
    base_url = ""
    selected_scan_type = ""

    while input_attempts < max_input_attempts:
        if input_attempts >= max_input_attempts:
            print('Too many attempts. Exiting...')
            return

        base_url = input('Enter URL to check\n> ').split('?')[0]
        is_url_valid: Union[bool,
                            ValidationFailure] = validate_url(base_url)
        if isinstance(is_url_valid, ValidationFailure):
            print('Warning: URL validation failed, please check your URL again!\n')
            input_attempts += 1
            continue

        input_attempts = 0
        break

    if input_attempts >= max_input_attempts:
        print('Error: Too many attempts. Exiting...')
        return

    print(
        '\nList of scan type(s)\n'
        '1 - Hardcoded VK Token and Params\n'
        '2 - Links\n'
        '3 - Possible tokens \n'
    )

    while input_attempts < max_input_attempts:
        selected_scan_type: str = input(
            'Select scan type(s) [Multiple scan types are written together]\n> ')
        if not selected_scan_type:
            print('Scan type cannot be empty. Please select one or more scan types!\n')
            input_attempts += 1
            continue
        input_attempts = 0
        break

    if input_attempts >= max_input_attempts:
        print('Error: Too many attempts. Exiting...')
        return

    return {
        'base_url': base_url,
        'scan_type': selected_scan_type
    }


def get_list_of_src(base_url: str) -> List[str]:
    text = get(base_url).text
    soup = BeautifulSoup(text, features='html.parser')
    scripts = soup.find_all('script')
    return [link['src'] for link in scripts if 'src' in link.attrs]


def get_list_of_scripts(base_url: str) -> List[str]:
    scripts_url: List[str] = []
    srcs = get_list_of_src(base_url)

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

    return scripts_url
