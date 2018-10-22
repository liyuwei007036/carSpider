# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Che168Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    che168_id = scrapy.Field()
    vehicle_name = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    price = scrapy.Field()
    distance = scrapy.Field()
    volume = scrapy.Field()  # 排量
    trubo = scrapy.Field()  # 挡位
    last_date = scrapy.Field()  # 上牌时间
    update_date = scrapy.Field()  # 发布时间
    address = scrapy.Field()
    owner = scrapy.Field()
    gb = scrapy.Field()
    imgs = scrapy.Field()
    phone = scrapy.Field()
