from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from .items import DiksiProduct

import json


class DiksiSpider(Spider):
    name = "diksi_crawler"
    allowed_domains = ["dostavka.dixy.ru"]
    start_urls = ["https://dostavka.dixy.ru/catalog/"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.load_cookies()

    def load_cookies(self):
        with open("crawlers/Diksi/cookies.json", "r") as file:
            self.cookies = json.load(file)

    def start_requests(self):
        yield Request(self.start_urls[0], cookies=self.cookies, callback=self.parse)

    def parse(self, response):
        categories = response.css("div.catalog_section_list a.dark_link::attr(href)")
        for category in categories:
            yield response.follow(category.get(), callback=self.parse_category)

    def parse_category(self, response):
        products = response.css("div.catalog_block > div.item_block")

        for product in products:
            loader = ItemLoader(item=DiksiProduct(), selector=product)
            loader.add_css("name", "div.card-name")
            loader.add_css("price_prev", "div.base.price-block div.cross")
            loader.add_css("price_cur", "div.base.price-block div.basic")

            yield loader.load_item()

        next_page = response.css("a.flex-next").attrib["href"]

        if next_page:
            yield response.follow(next_page, callback=self.parse_category)
