import requests as r
import bs4
import jsbeautifier
import re

ignore_word_list = ['yandexMap', 'VKWebApp', 'reactInternal', 'component', 'Icon', 'Browser', 'Scroll', 'get',
                    'Location', 'Panel', 'Point', 'Hook', 'animat', 'remove', 'event', 'mouse', 'refresh', 'padding',
                    'child']

ignore_url_list = ['w3.org', 'reactjs.org']


def start():
    scripts_url = []
    base_url = input('URL?\n')
    if len(base_url) < 5:
        print('is that URL?')
        quit()
    scan_type = input(
        'Select scan type(s)\n '
        '1 - Hardcoded VK Token and Params\n '
        '2 - Links \n '
        '3 - possible tokens \n')
    if len(scan_type) < 1:
        print('bro wtf, define scan type')
        quit()
    text = r.get(base_url).text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    scripts = soup.find_all('script')
    srcs = [link['src'] for link in scripts if 'src' in link.attrs]
    base_url = base_url.split('?')[0]
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


def jser(scripts_url, scan_type):
    print(scripts_url)
    for file in scripts_url:
        try:
            js = r.get(file).text
            beauty = jsbeautifier.beautify(js)
            lines = beauty.splitlines()
            scanner(lines, scan_type)
        except Exception as err:
            print('Seems like something is broken. Please copy an error below and report it to me with the link which '
                  'was scanned '
                  'by using GitHub, https://vk.com/zema or https://t.me/damnware '
                  'Thanks!\n')
            print(err)
            pass


def scanner(lines, scan_type):
    if "1" in scan_type:
        for line in lines:
            if "vk1.a." and "vk_access_token_settings=" in line:
                print("Found hardcoded VK Token and params: \n" + line.lstrip())
            elif "vk1.a." in line:
                print("Found hardcoded VK Token: \n" + line.lstrip())
            elif "vk_access_token_settings=" in line:
                print("Found hardcoded params at line: \n" + line.lstrip())
    if "2" in scan_type:
        for line in lines:
            if re.findall(r"(http|ftp|https)://([\w_-]+(?:\.[\w_-]+)+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])",
                          line) and not any(url.lower() in line.lower() for url in ignore_url_list):
                print("Found link: " + re.search("(?P<url>https?://\S+)", line).group("url"))
    if "3" in scan_type:
        for line in lines:
            if re.findall(r"[a-zA-Z\d]{25,100}", line) and not any(
                    word.lower() in line.lower() for word in ignore_word_list):
                print(re.findall(r"[a-zA-Z\d]{25,100}", line))


try:
    start()
except Exception as e:
    print('Seems like smth is broken. Please copy an error below and report it to me'
          'by using GitHub, https://vk.com/zema or https://t.me/damnware '
          'Thanks!\n')
    print(e)
    pass
