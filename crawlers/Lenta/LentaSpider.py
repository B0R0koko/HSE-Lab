from scrapy.http import Request
from scrapy import Spider

import scrapy


class LentaSpider(Spider):
    def start_requests(self):
        yield Request(url="https://lenta.com/api/v1/skus/list")
