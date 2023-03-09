from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.loader import ItemLoader
from .Product import DiksiProduct

import json
import scrapy

from typing import *


class DiksiSpider(Spider):
    name = "diksi_crawler"
    allowed_domains = ["dostavka.dixy.ru"]

    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, name=None, **kwargs) -> Self:
        super().__init__(name, **kwargs)
        self.load_headers()

    def load_headers(self) -> None:
        with open("crawlers/Diksi/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def start_requests(self) -> scrapy.Request:
        yield Request(
            url="https://dostavka.dixy.ru/catalog/",
            headers=self.headers,
            callback=self.parse,
        )

    def parse(self, response) -> scrapy.Request:
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

    def parse_category(self, response) -> scrapy.Request:
        category = response.meta["category"]

        sub_cats = {
            el.css("span::text").get(): el.attrib["href"]
            for el in response.css("div.section-compact-list > div > div > a")
        }

        for sub_name, sub_href in sub_cats.items():
            yield Request(
                url=f"https://dostavka.dixy.ru{sub_href}",
                headers=self.headers,
                callback=self.parse_subcategory,
                meta={"category": category, "sub_name": sub_name},
            )

    def parse_subcategory(self, response):
        products = response.css("div.catalog_block > div.item_block")

        for product in products:
            loader = ItemLoader(item=DiksiProduct(), selector=product)

            loader.add_css("name", "div.card-name")
            loader.add_css("price_prev", "div.base.price-block div.cross")
            loader.add_css("price_cur", "div.base.price-block div.basic")
            loader.add_value("category", response.meta["category"])
            loader.add_value("subcategory", response.meta["sub_name"])

            yield loader.load_item()

        next_page = response.css("a.flex-next")

        if next_page:
            next_href = next_page.attrib["href"]
            yield Request(
                url=f"https://dostavka.dixy.ru{next_href}",
                headers=self.headers,
                callback=self.parse_subcategory,
                meta=response.meta,
            )
