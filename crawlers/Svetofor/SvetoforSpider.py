from scrapy.http import Request
from scrapy import Spider

import json
import scrapy

from urllib.parse import urljoin

from typing import *


class SvetoforSpider(Spider):
    BASE_URL = "https://spb-pargolovo.svetoforonline.ru"

    name = "svetofor_spider"
    allowed_domains = ["spb-pargolovo.svetoforonline.ru"]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.load_categories()

    def load_categories(self) -> None:
        with open("crawlers/Svetofor/cfg/categories.json", "r") as file:
            self.categories = json.load(file)

    def start_requests(self) -> scrapy.Request:
        for category_href in self.categories:
            yield Request(
                url=self.BASE_URL + category_href,
                callback=self.parse_category,
                meta={"category_href": category_href},
            )

    def parse_category(self, response) -> scrapy.Request:
        category_href = response.meta["category_href"]
        pages = [a.attrib["href"] for a in response.css("td.paging > a")[:-2]]

        for page in pages:
            yield Request(
                url=urljoin(self.BASE_URL + category_href, page),
                callback=self.parse_products,
                meta={"category_href": category_href},
            )

    def parse_products(self, response):
        products = response.css("div.product-grid > div")

        for product in products:
            yield {
                "name": product.css("a::text").get(),
                "price": product.css("span::text").get(),
                "category": self.categories[response.meta["category_href"]],
            }
