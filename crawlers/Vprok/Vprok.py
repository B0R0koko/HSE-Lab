import requests
import json
import re
import logging
import os
import time

from typing import *
from tqdm import tqdm

from .Product import Product


class VprokParser:
    QUERY_URL = "https://www.vprok.ru/web/api/v1/catalog/category/{}"

    def __init__(self, output_loc: str) -> Self:
        self._load_headers()
        self._load_categories()
        self._open_file(output_loc)

    def _open_file(self, output_loc: str) -> None:
        self.file = open(output_loc, "a", encoding="utf8")
        self.file.write("[")
        self.file_opened = True

    def _load_categories(self) -> None:
        with open("crawlers/Vprok/cfg/categories.json", "r") as file:
            self.categories = json.load(file)["categories"]

    def _load_headers(self) -> None:
        with open("crawlers/Vprok/cfg/headers.json", "r") as file:
            self.headers = json.load(file)

    def close_file(self):
        if self.file_opened:
            self.file.seek(self.file.tell() - 1, os.SEEK_SET)
            self.file.write("")
            self.file.write("]")
            self.file.close()

    def parse_json(self, resp: dict) -> Dict[str, Any]:
        for product in resp["products"]:
            product = Product(product)
            yield product.data

    def save_data(self, resp: dict) -> None:
        for product in self.parse_json(resp):
            json.dump(product, self.file, ensure_ascii=False, indent=4)
            self.file.write(",")

    def post_request(self, url, params, data) -> requests.Response:
        resp: requests.Response = requests.post(
            url=url, params=params, data=data, headers=self.headers
        )
        return resp

    def make_request(self, url, params, data) -> dict:
        for i in range(1, 6):
            resp = self.post_request(url, params, data)
            if resp.ok:
                time.sleep(1)
                return {"successful": True, "data": resp.json()}
            print(f"Bad response for {url}. Attempt {i}")
            time.sleep(5)
            os.system("clear")
        return {"successful": False, "data": resp}

    def fetch_category(self, category: str):
        params = {
            "sort": "popularity_desc",
            "limit": "60",
            "page": 1,
        }
        data = json.dumps({"noRedirect": True, "url": category})

        category_id = re.search("\d+", category)[0]
        category_url = self.QUERY_URL.format(category_id)
        resp: dict = self.make_request(url=category_url, params=params, data=data)

        if not resp["successful"]:
            return

        total_pages = resp["data"]["pages"]

        pbar = tqdm(range(1, total_pages + 1), leave=False)
        pbar.set_description(category)

        for i in pbar:
            params["page"] = i

            resp: dict = self.make_request(url=category_url, params=params, data=data)
            if resp["successful"]:
                self.save_data(resp["data"])

    def run(self):
        for category in tqdm(self.categories):
            self.fetch_category(category)

        self.close_file()


if __name__ == "__main__":
    parser = VprokParser()
    parser.run()
