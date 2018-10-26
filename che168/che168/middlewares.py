# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.exceptions import IgnoreRequest

from che168.redisopera import UrlFilterAndAdd
from che168.settings import PROXY_POOL_MAX, USER_AGENTS, PROXY_POOL_MIN, ADD_PROXY


class Che168DownloaderMiddleware(object):

    def __init__(self):
        self.dupefilter = UrlFilterAndAdd()

    proxy_pool = []
    cur_proxy = {}

    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):

        if self.dupefilter.check_url(request.url):
            raise IgnoreRequest('{1} URL重复 无需再次处理 自动忽略{0}\r\n'.format(request.url, datetime.now()))

        request.headers.setdefault('User-Agent', random.choice(USER_AGENTS))

        # 如果开启了代理 则自动添加代理
        if ADD_PROXY:
            cur_proxy = random.choice(self.proxy_pool)
            request.meta["proxy"] = '{0}://{1}:{2}'.format(cur_proxy.get('type'), cur_proxy.get('ip'),
                                                           cur_proxy.get('port'))

    def process_response(self, request, response, spider):

        # 如果返回的请求的body为空，很可能Ip被封掉了 进行暂停机制
        if len(response.body) < 1:
            print('{0} Ip可能被封掉了 暂停5分钟后继续发起请求 {1}'.format(datetime.now(), response.url), end='\r\n')
            for i in range(300):
                time.sleep(1)
                print('{0}s 后开始请求'.format(300 - i), end='\r\n')

            return request

        if ADD_PROXY and response.status != 200:
            self.proxy_pool.remove(self.cur_proxy)
            cur_proxy = random.choice(self.proxy_pool)

            if len(self.proxy_pool) < PROXY_POOL_MIN:
                print('{1}------------------------IP代理池IP数量小于{0}正在重新获取'.format(PROXY_POOL_MIN, datetime.now()))
                self.get_proxies(url='http://www.xicidaili.com/nn/')

            request.meta["proxy"] = '{0}://{1}:{2}'.format(cur_proxy.get('type'), cur_proxy.get('ip'),
                                                           cur_proxy.get('port'))
            return request

        return response

    def process_exception(self, request, exception, spider):
        print(exception)

    def spider_opened(self, spider):
        print('{1} -------------------------{0} 已启动----------------'.format(spider.name, datetime.now()))
        if ADD_PROXY:
            print('-------------------------正在获取代理IP----------------')
            url = 'http://www.xicidaili.com/wn/'
            self.get_proxies(url)

    def get_proxies(self, url):
        session = requests.Session()
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        session.headers.update(head)
        res = session.get(url=url)
        soup = BeautifulSoup(res.content, 'lxml')
        trs = soup.find_all('tr', class_='odd')
        for tr in trs:
            td = tr.get_text().split()
            dic = {
                'ip': td[0],
                'port': td[1],
                'type': td[4].lower()
            }

            if len(self.proxy_pool) >= PROXY_POOL_MAX:
                break
            self.check_proxy(head=head, dic=dic)

        # 获取下一页:
        if len(self.proxy_pool) < PROXY_POOL_MAX:
            next_page = soup.find('a', class_='next_page')['href']
            next_page = 'http://www.xicidaili.com{0}'.format(next_page)
            print(next_page)
            self.get_proxies(url=url)

    def check_proxy(self, head, dic):
        url = 'https://www.baidu.com'
        proxy = {
            dic.get('type'): '{0}://{1}:{2}'.format(dic.get('type'), dic.get('ip'), dic.get('port'))
        }

        try:
            res = requests.get(url=url, headers=head, proxies=proxy, timeout=2)
            if res.status_code == requests.codes.ok and dict not in self.proxy_pool:
                self.proxy_pool.append(dic)
                print('----------------- 当前连接池数量{0}/{1}----------------'.format(len(self.proxy_pool), PROXY_POOL_MAX))
        except requests.RequestException as e:
            print(e)
