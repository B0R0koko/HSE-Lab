from scrapy.http import Request, JsonRequest
from scrapy import Spider
from urllib.parse import urlencode
from selectolax.parser import HTMLParser

from typing import *

import re
import json


class VprokSpider(Spider):
    name = "vprok_spider"
    allowed_domains = ["www.vprok.ru"]

    custom_settings = {"LOG_LEVEL": "DEBUG", "CONCURRENT_REQUESTS": 5}

    QUERY_URL = "https://www.vprok.ru/web/api/v1/catalog/category/{}?{}"

    def __init__(self) -> Self:
        self.load_headers()
        self.load_categories()

    def load_categories(self) -> None:
        with open("crawlers/Vprok/cfg/categories.json", "r") as file:
            self.categories = json.load(file)["categories"]

    def load_headers(self) -> None:
        with open("crawlers/Vprok/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def start_requests(self):
        # collect number of pages to make furthe requests asynchronously
        # otherwise with while loops its blocking io

        params = {
            "sort": "popularity_desc",
            "limit": "60",
            "page": 1,
        }

        for category in self.categories:
            category_id = re.search("\d+", category)[0]

            payload = {
                "noRedirect": True,
                "url": category,
            }

            yield JsonRequest(
                url=self.QUERY_URL.format(category_id, urlencode(params)),
                headers=self.headers,
                callback=self.parse_category,
                data=payload,
                meta={"category_href": category, "category_id": category_id},
            )

    def parse_category(self, response):
        resp = json.loads(response.body)
        category_id = response.meta["category_id"]
        category_href = response.meta["category_href"]

        payload = json.dumps({"noRedirect": True, "url": category_href})

        for i in range(1, resp["pages"] + 1):
            params = {
                "sort": "popularity_desc",
                "limit": "60",
                "page": i,
            }

            yield Request(
                url=self.QUERY_URL.format(category_id, urlencode(params)),
                method="POST",
                body=payload,
                headers=self.headers,
                callback=self.parse_json,
            )

    def parse_json(self, response):
        yield {"response": response.url}
