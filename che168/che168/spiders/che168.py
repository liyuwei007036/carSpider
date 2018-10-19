import re

import scrapy
from che168.items import Che168Item


class che168(scrapy.Spider):
    name = 'che168'

    def start_requests(self):

        urls = ['https://www.che168.com/china/a0_0ms1dgscncgpi1ltocspexx0/']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        cars = response.css('li.list-photo-li a.carinfo')
        for car in cars:
            url = car.css('.carinfo ::attr(href)').extract()[0]
            name = car.css('div.list-photo-info h4.car-series::text').extract_first()

            url = 'https://www.che168.com{0}'.format(url)
            yield scrapy.Request(url=url, callback=self.parse2)

            info = car.css('div.list-photo-info p::text').extract_first()

            print(name, '---->', info, '---->', url)

        next_url = response.css('div#listpagination a.page-item-next::attr(href)').extract_first()
        if next_url is not None:
            next_url = 'https://www.che168.com{0}'.format(next_url)
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse2(self, response):
        vehicle_name = response.css('div .car-title h2::text').extract_first()
        infos = response.css('div.details ul li span::text').extract()
        price = response.css('div.car-price ins::text').extract_first()
        car_address = response.css('div.car-address').extract_first()

        imgs = response.css('div ul li.grid-10')
        for img in imgs:
            print(img.css('a img').extract())
            urls = img.css('a img::attr(src)').extract()
            print(urls)

        url = response.url
        searchObj = re.search(r'(\d+.html)', url)
        name = searchObj.group()
        item = Che168Item()
        item['url'] = url
        item['che168_id'] = name.split('.')[0]
