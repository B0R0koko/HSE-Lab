from scrapy.http import Request
from scrapy import Spider

import scrapy

from typing import *
from urllib.parse import urlencode

import json
import math


class MagnitSpider(Spider):
    name = "magnit_spider"
    allowed_domains = ["dostavka.magnit.ru"]

    params = {
        "page": 1,
        "sort": "popular",
        "division": 793078,
        "shop_code": 793078,
        "useSiteXmlIdService": "express",
    }

    FETCH_URL = "https://dostavka.magnit.ru/api/catalog/product-list/{}?{}"

    def __init__(self, *args, **kwargs) -> Self:
        super().__init__(*args, **kwargs)
        self.load_categories()

    def load_categories(self) -> None:
        with open("crawlers/Magnit/cfg/categories.json", "r") as file:
            self.categories = json.load(file)["categories"]

    def start_requests(self) -> scrapy.Request:
        self.params["page"] = 1

        for category in self.categories:
            category_name = category.split("/")[-1]

            yield Request(
                url=self.FETCH_URL.format(category_name, urlencode(self.params)),
                callback=self.parse_category,
                meta={"category_name": category_name},
            )

    def parse_category(self, response) -> scrapy.Request:
        data = json.loads(response.body)
        category_name = response.meta["category_name"]
        n_pages = math.ceil(data["count"] / data["pageSize"])

        for i in range(1, n_pages + 1):
            # update params and feed to request
            self.params["page"] = i

            yield Request(
                url=self.FETCH_URL.format(category_name, urlencode(self.params)),
                callback=self.parse_json,
                meta={"category_name": category_name},
            )

    def parse_json(self, response) -> Dict[str, Any]:
        data = json.loads(response.body)

        for product in data["items"]:
            yield {
                "name": product["name"],
                "category": product["category"]["name"],
                "shop_code": product["offers"][0]["shop_code"],
                "currentPrice": product["offers"][0]["currentPrice"],
                "previousPrice": product["offers"][0]["previousPrice"],
                "quantity": product["offers"][0]["quantity"],
            }
