import requests
from bs4 import BeautifulSoup
import re


host = 'https://www.chinapost.com.cn'
root_uri = '/html1/category/181313/7294-1.htm'


def create_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.chinapost.com.cn',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }


def make_request(host, uri):
    res = requests.get(host + uri, headers=create_headers())
    if res.status_code == 200:
        res.encoding = 'utf-8'
        return res.text
    return None


def fetch_type_bids(d, t, host, uri):
    pages = {}
    is_last_page = False
    p = 0
    while not is_last_page:
        p += 1
        html_text = make_request(host, uri)
        soup = BeautifulSoup(html_text, 'html.parser')
        bids = []
        for bid in soup.select('#Content3 div.new_list ul li'):
            if bid.get('id') == 'PageNum':
                continue
            name_span, date_span = bid.children
            name_a, *_ = name_span.children
            bid_name = name_a.get('title')
            bid_ref = name_a.get('href')
            bid_date = date_span.string
            bids.append((d, t, p, bid_name, bid_date, bid_ref))
            print(f'{d},{t},第{p}页,{bid_date},"{bid_name}"')
        pages[p] = bids
        page_num = list(soup.select('#Content3 div.new_list ul li#PageNum a#CBNext'))
        if len(page_num) == 0:
            is_last_page = True
        else:
            uri = page_num[0].get('href')
    return pages


def fetch_department_bids(d, host, uri):
    bid_types = {}
    html_text = make_request(host, uri)
    redirect_string = re.search(r"window\.location\.href='(\S+)'", html_text)
    if redirect_string is not None: # redirected
        uri = redirect_string.group(1)
        html_text = make_request(host, uri)
    soup = BeautifulSoup(html_text, 'html.parser')
    # current type is not a <a> tag, but a <span>
    current_bid_type = next(iter(soup.select('span#CurrentlyNode'))).string
    bid_types[current_bid_type] = uri
    for t_a in soup.select('#Content3 div.san_nav ul li span a'):
        bid_types[t_a.string] = t_a.get('href')
    return {t: fetch_type_bids(d, t, host, t_uri) for t, t_uri in bid_types.items()}


def fetch_all_bids(host, uri):
    bid_departments = {}
    html_text = make_request(host, uri)
    soup = BeautifulSoup(html_text, 'html.parser')
    for d_a in soup.select('#Content1 div.about_nav ul li span.tit span a'):
        bid_departments[d_a.string] = d_a.get('href')
    return {d: fetch_department_bids(d, host, d_uri) for d, d_uri in bid_departments.items()}


if __name__ == '__main__':
    all_bids = fetch_all_bids(host, root_uri)

