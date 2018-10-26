from datetime import datetime

import scrapy.cmdline as line

today = datetime.now()
line.execute('scrapy crawl che168 -s LOG_FILE=d:\che168-{0}-{1}-{2}-log.log'.format(today.year, today.month, today.day).split())
