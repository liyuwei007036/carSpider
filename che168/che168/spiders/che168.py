import json
import re
from http import cookiejar
from urllib import request, parse

import scrapy
from che168.items import Che168Item


class che168(scrapy.Spider):
    name = 'che168'

    def start_requests(self):
        urls = ['https://www.che168.com/china/a0_0ms1dgscncgpi1ltocspexx0/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_city)

    def parse_city(self, response):
        citys = response.css('dl.cap-city dd a::attr(href)').extract()
        citysls = []
        for city in citys:
            city_name = re.findall(r'/(.+)/list/#', city)
            if len(city_name) < 1:
                print('出错' + city)
            else:
                if city_name[0] not in citysls and city_name[0] != 'china':
                    citysls.append(city_name[0])

        for c in citysls:
            city_url = 'https://www.che168.com/{0}/a0_0ms1dgscncgpi1ltocspexx0/'.format(c)
            yield scrapy.Request(url=city_url, callback=self.parse)

    def parse(self, response):
        cars = response.css('li.list-photo-li a.carinfo')
        for car in cars:
            url = car.css('.carinfo ::attr(href)').extract_first()
            if url is not None:
                url = 'https://www.che168.com{0}'.format(url)
                yield scrapy.Request(url=url, callback=self.parse_item)

        next_url = response.css('div#listpagination a.page-item-next::attr(href)').extract_first()
        if next_url is not None:
            next_url = 'https://www.che168.com{0}'.format(next_url)
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_item(self, response):
        imgs = response.css('div ul li.grid-10')
        for img in imgs:
            img.css('a img::attr(src)').extract()
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
        phone = self.get_phone_num(item_id=item['che168_id'], url=item['url'])
        item['phone'] = phone
        yield item

    def get_phone_num(self, item_id, url):
        phone = None
        url = 'https://usedcarpv.che168.com/pv.ashx'
        cookie = cookiejar.LWPCookieJar()
        cookie_handler = request.HTTPCookieProcessor(cookie)
        opener = request.build_opener(cookie_handler)
        request.install_opener(opener)
        request.urlopen(url=url)
        cookie.save('cookie.txt', ignore_expires=True, ignore_discard=True)
        cookie_dic = {}
        for i in cookie:
            cookie_dic[i.name] = i.value

        uniqueid = cookie_dic.get('sessionid', None)
        formData = {
            '_appid': '2sc.pc',
            'fromtype': '0',
            'infoid': str(item_id),
            'uniqueid': str(uniqueid),
            'ts': '0',
            '_sign': 'Ehedie3January',
            'sessionid': str(uniqueid),
            'detailpageurl': url,
            'detailpageref': '',
            'adfrom': '0'
        }
        get_num_url = 'https://callcenterapi.che168.com/CallCenterApi/v100/BindingNumber.ashx?' + parse.urlencode(
            formData)
        res = request.urlopen(get_num_url)
        json_data = json.loads(res.read())
        if json_data.get('returncode', 1) == 0:
            if json_data.get('result', None) is not None:
                phone = json_data.get('result').get('xnumber')
        print(phone)
        return phone
