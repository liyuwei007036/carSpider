# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql


class Che168Pipeline(object):

    def __init__(self):
        db = pymysql.connect("localhost", "root", "123456", "py_car")
        cursor = db.cursor()

    def process_item(self, item, spider):
        res = self.dbpool.runInteraction(self.insert_into_table, item)
        return item

    def insert_into_table(self, cursor, item):
        cursor.execute('''
            insert into Login values("%s", "%s")' %  (user_id, password)
        ''')
