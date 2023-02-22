from scrapy.spiders import Spider
from scrapy.http import JsonRequest, Request
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin, urlencode

import json
import re


SETTINGS = dict(
    DOWNLOAD_HANDLERS={
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    PLAYWRIGHT_MAX_CONTEXTS=1,
    PLAYWRIGHT_MAX_PAGES_PER_CONTEXT=1,
    LOG_LEVEL="INFO",
    PLAYWRIGHT_LAUNCH_OPTIONS={"headless": False},
)

API_ENDPOINT = "https://www.vprok.ru/web/api/v1/catalog/category/"


class VprokSpider(Spider):
    name = "vprok_spider"
    custom_settings = SETTINGS

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self._load_headers()

    def _load_headers(self):
        with open("crawlers/Vprok/headers.json", "r") as file:
            self.headers = json.load(file)

    # open chromium headless browser and collect all available categories
    def start_requests(self):
        yield Request(
            url="https://www.vprok.ru/",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "button.Burger_burger__bNSA_"),
                    PageMethod(
                        "evaluate",
                        'document.querySelector("button.Burger_burger__bNSA_").click()',
                    ),
                ],
            },
            callback=self.parse_catalogs,
            errback=self.errback_close_page,
        )

    # playwright on_error action
    async def errback_close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    # for each collected catalog make an API request to REST API
    async def parse_catalogs(self, response):
        catalogs = response.css('div.CatalogMenu_parents__Krpe1 > a[href*="catalog"]')
        catalogs = [catalog.attrib["href"] for catalog in catalogs]

        print(catalogs)

        page = response.meta["playwright_page"]
        await page.close()
