import requests as r
import bs4
import jsbeautifier
import re

ignore_list = ["yandexMap", "VKWebApp", "reactInternal", "component", "Icon", "Browser", "Scroll", "get", "Location", "Panel", "Point", "Hook", "animat", "remove", "event", "mouse", "refresh", "padding", "child"]

def url_collector():
    scripts_url = []
    base_url = input("URL?\n")
    if len(base_url) < 5:
        print("is that URL?")
        quit()
    scan_type = input("Scan type? (separated by commas)\n 1 - Hardcoded VK Token and Params\n 2 - Links \n 3 - possible tokens \n")
    if len(scan_type) < 1:
        print("bro wtf, define scan type")
        quit()
    text = r.get(base_url).text
    soup = bs4.BeautifulSoup(text, features='html.parser')
    scripts = soup.find_all('script')
    srcs = [link['src'] for link in scripts if 'src' in link.attrs]
    base_url = base_url.split('?')[0]
    for attribute in srcs:
        if "index.html" in base_url:
            base_url = base_url[:-11]

        if attribute[0:2] == "./":
            attribute = attribute[1:]
            print("1")
        elif attribute[0:2] == "..":
            attribute = attribute[1:]
            print("2")

        if "http" not in attribute:
            url = base_url + attribute
            scripts_url.append(url)
            print(scripts_url)
        else:
            scripts_url.append(attribute)
    scanner(scripts_url, scan_type)


def scanner(scripts_url, scan_type):
    for file in scripts_url:
        js = r.get(file).text
        beauty = jsbeautifier.beautify(js)
        Lines = beauty.splitlines()
        if "1" in scan_type:
            for line in Lines:
                if "vk1.a." and "vk_access_token_settings=" in line:
                    print("Found hardcoded VK Token and params: \n" + line.lstrip())
                elif "vk1.a." in line:
                    print("Found hardcoded VK Token: \n" + line.lstrip())
                elif "vk_access_token_settings=" in line:
                    print("Found hardcoded params at line: \n" + line.lstrip())
        if "2" in scan_type:
            for line in Lines:
                if 'w3.org' not in line and 'reactjs.org' not in line and re.findall(r"(http|ftp|https)://([\w_-]+(?:\.[\w_-]+)+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])", line):
                    print("Found link: " + re.search("(?P<url>https?://[^\s]+)", line).group("url"))
        if "3" in scan_type:
            for line in Lines:
#                if re.findall(r"[a-zA-Z\d]{25,100}", line) and "yandexMap" not in line and "VKWebApp" not in line and "reactInternal" not in line and "component" not in line:
                if re.findall(r"[a-zA-Z\d]{25,100}", line) and not any(word.lower() in line.lower() for word in ignore_list):
                    print(re.findall(r"[a-zA-Z\d]{25,100}", line))


url_collector()
