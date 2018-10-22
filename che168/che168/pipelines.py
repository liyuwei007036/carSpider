# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import re
from http import cookiejar
from urllib import request, parse

import pymysql
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class Che168Pipeline(object):
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "123456", "spider")
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        phone = self.get_phone_num(item_id=item['che168_id'], url=item['url'])
        print(item['url'], '----------------------->', phone)
        sql = 'insert into car (che168_id, url, vehicle_name, province, city, price, distance, volume, trubo, last_date, update_date, address, owner, gb, phone) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)'
        par = (item['che168_id'], item['url'], item['vehicle_name'], item['province'], item['city'],
               item['price'],
               item['distance'], item['volume'], item['trubo'], item['last_date'], item['update_date'],
               item['address'], item['owner'], item['gb'], phone,)
        self.cursor.execute(sql, par)
        self.db.commit()
        return item

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
        print('---------------->', json_data)
        if json_data.get('returncode', 1) == 0:
            if json_data.get('result', None) is not None:
                phone = json_data.get('result').get('xnumber')
        return phone


class ImagespiderPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # 循环每一张图片地址下载，若传过来的不是集合则无需循环直接yield
        for image_url in item['imgs']:
            yield Request(image_url, meta={'name': item['che168_id']})

    # 重命名，若不重写这函数，图片名为哈希，就是一串乱七八糟的名字
    def file_path(self, request, response=None, info=None):
        # 提取url前面名称作为图片名。
        image_guid = request.url.split('/')[-1]
        # 接收上面meta传递过来的图片名称
        name = request.meta['name']
        # 过滤windows字符串，不经过这么一个步骤，你会发现有乱码或无法下载
        name = re.sub(r'[？\\*|“<>:/]', '', name)
        # 分文件夹存储的关键：{0}对应着name；{1}对应着image_guid
        filename = u'{0}/{1}'.format(name, image_guid)
        return filename
