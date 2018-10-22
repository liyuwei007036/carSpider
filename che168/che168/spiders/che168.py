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
        province = response.css('div.breadnav a::text').extract()[1]
        vehicle_name = response.css("div.car-title h2::text").extract_first()
        price = response.css('div.car-price ins::text').extract_first()
        all = response.css('div.details ul span::text').extract()
        address = response.css('div.car-address::text').extract()
        add = address[0].split(r':')[1]
        update_date = address[1].split(r':')[1]
        price = re.search(r'(\d+.\d+)', price).group()
        distance = re.search(r'(\d+)', all[0]).group()
        last_date = all[1]
        volume = re.search(r'(\d+.?\d?[L|T])', all[2]).group()
        trubo = re.search(r'([\u4e00-\u9fa5]+)', all[2]).group()
        city = all[3]
        gb = all[4]
        owner = response.css('ul.infotext-list li.grid-20::text').extract_first()
        if owner is not None:
            owner = owner.strip()
        item = Che168Item()
        item['url'] = url
        item['che168_id'] = name.split('.')[0]
        item['vehicle_name'] = vehicle_name
        item['province'] = province
        item['city'] = city
        item['price'] = price
        item['distance'] = distance
        item['volume'] = volume
        item['trubo'] = trubo
        item['last_date'] = last_date
        item['update_date'] = update_date
        item['address'] = add
        item['owner'] = owner
        item['gb'] = gb

        ul = response.css('div ul li.grid-10')
        imgs = []
        for li in ul:
            img = 'https:' + li.css('li.grid-10 img::attr(src2)').extract_first()
            imgs.append(img)

        item['imgs'] = imgs
        yield item
