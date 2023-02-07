from scrapy.crawler import CrawlerProcess

from crawlers.Diksi import DiksiSpider
from crawlers.Vprok import VprokSpider

import scrapy
import argparse


def run_scrapy_spider(Spider: scrapy.Spider, output_loc: str):
    feed_format = output_loc.split(".")[-1]
    process = CrawlerProcess(
        settings={"FEED_URI": output_loc, "FEED_FORMAT": feed_format}
    )
    process.crawl(Spider)
    process.start()


# run parser given user settings input
def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("crawler", metavar="crawler", type=str)
    argp.add_argument(
        "-o", metavar="output_loc", required=True, help="Specify output location"
    )
    args = argp.parse_args()
    print(args)

    # match case for each crawler defined in crawlers lib
    match args.crawler:
        case "diksi":
            run_scrapy_spider(DiksiSpider, args.o)
        case "vprok":
            ...


if __name__ == "__main__":
    main()
