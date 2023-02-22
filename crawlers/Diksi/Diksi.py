from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from .Product import DiksiProduct

import json


class DiksiSpider(Spider):
    name = "diksi_crawler"
    allowed_domains = ["dostavka.dixy.ru"]

    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.load_headers()

    def load_headers(self):
        with open("crawlers/Diksi/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def start_requests(self):
        yield Request(
            url="https://dostavka.dixy.ru/catalog/",
            headers=self.headers,
            callback=self.parse,
        )

    def parse(self, response):
        categories = {}

        for category in response.css("div.catalog_section_list > div"):
            name = category.css("li.name > span::text").get()
            href = category.css("a.dark_link").attrib["href"]
            categories[name] = href

        for category, href in categories.items():
            yield Request(
                url=f"https://dostavka.dixy.ru{href}",
                headers=self.headers,
                callback=self.parse_category,
                meta={"category": category},
            )

    def parse_category(self, response):
        products = response.css("div.catalog_block > div.item_block")
        category = response.meta["category"]

        for product in products:
            loader = ItemLoader(item=DiksiProduct(), selector=product)
            loader.add_css("name", "div.card-name")
            loader.add_css("price_prev", "div.base.price-block div.cross")
            loader.add_css("price_cur", "div.base.price-block div.basic")
            loader.add_value("category", category)
            yield loader.load_item()

        next_page = response.css("a.flex-next")

        if next_page:
            next_href = next_page.attrib["href"]
            yield Request(
                url=f"https://dostavka.dixy.ru{next_href}",
                headers=self.headers,
                callback=self.parse_category,
                meta={"category": category},
            )
