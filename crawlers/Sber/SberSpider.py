import scrapy
import json

from urllib.parse import urlencode

from typing import *


class SberSpider(scrapy.Spider):
    name = "sber"

    def __init__(self, **kwargs) -> Self:
        super().__init__(**kwargs)
        self.load_headers()

    def load_headers(self) -> None:
        with open("crawlers/Sber/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def start_requests(self) -> scrapy.Request:
        params = {"depth": 1, "include": "", "reset_cache": "true"}
        yield scrapy.Request(
            url=f"https://sbermarket.ru/api/v3/stores/83/categories?{urlencode(params)}",
            headers=self.headers,
            callback=self.start_parsing,
        )

    def start_parsing(self, response) -> scrapy.Request:
        resp = json.loads(response.body)
        categories = {
            category["name"]: category["slug"] for category in resp["categories"]
        }
        for parent_category, slug in categories.items():
            params = {"depth": 1, "reset_cache": "true"}

            yield scrapy.Request(
                url=f"https://sbermarket.ru/api/v3/stores/83/categories/{slug}?{urlencode(params)}",
                headers=self.headers,
                meta={"parent_category": parent_category},
                callback=self.parse_parent_category,
            )

    def parse_parent_category(self, response) -> scrapy.Request:
        resp = json.loads(response.body)
        subcategories = {el["name"]: el["slug"] for el in resp["category"]["children"]}

        for subcat_name, slug in subcategories.items():
            params = {
                "tid": slug,
                "page": 1,
                "per_page": 20,
                "sort": "popularity",
            }

            yield scrapy.Request(
                url=f"https://sbermarket.ru/api/v3/stores/83/products?{urlencode(params)}",
                headers=self.headers,
                callback=self.parse_subcategory,
            )

    def parse_subcategory(self, response) -> Dict[str, Any]:
        resp = json.loads(response.body)

        for product in resp["products"]:
            yield {
                "name": product["name"],
                "price": product["price"],
                "original_price": product["original_price"],
                "discount": product["discount"],
                "human_volume": product["human_volume"],
                "grams_per_unit": product["grams_per_unit"],
                "price_type": product["price_type"],
                "unit_price": product["unit_price"],
                "original_unit_price": product["original_unit_price"],
                "score": product["score"],
                "comment_count": product["score_details"]["comment_count"],
            }
