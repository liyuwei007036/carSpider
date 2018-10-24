# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

import requests
from bs4 import BeautifulSoup
from che168.settings import PROXY_POOL_MAX, USER_AGENTS, PROXY_POOL_MIN, ADD_PROXY
from scrapy import signals

from che168.redisopera import UrlFilterAndAdd


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
            return None

        if ADD_PROXY:
            cur_proxy = random.choice(self.proxy_pool)
            request.meta["proxy"] = '{0}://{1}:{2}'.format(cur_proxy.get('type'), cur_proxy.get('ip'),
                                                           cur_proxy.get('port'))
        request.headers.setdefault('User-Agent', random.choice(USER_AGENTS))

    def process_response(self, request, response, spider):
        if ADD_PROXY:
            if response.status != 200 or len(response.body) < 1:
                self.proxy_pool.remove(self.cur_proxy)
                cur_proxy = random.choice(self.proxy_pool)
                request.meta["proxy"] = '{0}://{1}:{2}'.format(cur_proxy.get('type'), cur_proxy.get('ip'),
                                                               cur_proxy.get('port'))
                if len(self.proxy_pool) < PROXY_POOL_MIN:
                    print('------------------------IP代理池IP数量小于{0}正在重新获取'.format(PROXY_POOL_MIN))
                    self.get_proxies(url='http://www.xicidaili.com/nn/')
                return request
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        print('-------------------------{0} 已启动----------------'.format(spider.name))
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
