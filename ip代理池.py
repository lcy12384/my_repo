import requests
from fake_useragent import UserAgent
import json
from lxml import etree
import random

def cre_headers():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    return headers

def get_ip_pool():
    with open("D:/WorkSpace/毕业设计/ip_kuaidaili.json", "r") as load_f:
        load_dic = json.load(load_f)
        data = load_dic['data']
        proxies_pool = data['proxy_list']
    return  proxies_pool

def cre_proxies():
    proxy = random.choice(get_ip_pool())
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": 'd2213256669', "pwd": 'xu04zwnc', "proxy": proxy},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": 'd2213256669', "pwd": 'xu04zwnc', "proxy": proxy}
    }
    return proxies

def ip_kuaidaili():
    #通过快代理获取付费代理ip
    url = "https://dps.kdlapi.com/api/getdps/?secret_id=ova46vu74f7tvnhwrd0w&num=20&signature=05aqi07it63y93hyj3oq9wi5wdhaf145&pt=1&dedup=1&format=json&sep=1"
    res = requests.get(url)
    print(type(res.json()))
    with open("D:/WorkSpace/毕业设计/ip_kuaidaili.json", "w") as f:
        json.dump(res.json(), f)

def ip_zhandaye():
    #通过爬取站大爷免费代理获取代理ip
    # for i in range(1,4):
        url = f"https://www.zdaye.com/free/1/?dengji=1"
        res = requests.get(url, headers=cre_headers())
        res.close()
        et = etree.HTML(res.text)
        ip = et.xpath('//tr/td[1]/text()')
        port = et.xpath('//tr/td[2]/text()')
        proxies = []
        print(ip)
        for i in range(1,len(ip)):
            proxies.append(ip[i] + ":" +port[i])
            print(proxies)

def main():
    # ip_zhandaye()
    ip_kuaidaili()
if __name__ == "__main__":
    main()