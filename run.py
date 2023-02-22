from scrapy.crawler import CrawlerProcess

from crawlers.Diksi import DiksiSpider
from crawlers.Vprok import VprokParser
from crawlers.Magnit import MagnitSpider
from crawlers.Svetofor import SvetoforSpider

import scrapy
import argparse


def run_scrapy_spider(Spider: scrapy.Spider, output_loc: str):
    feed_format = output_loc.split(".")[-1]
    process = CrawlerProcess(
        settings={
            "FEED_URI": output_loc,
            "FEED_FORMAT": feed_format,
            "FEED_EXPORT_ENCODING": "utf-8",
        }
    )
    process.crawl(Spider)
    process.start()


def run_custom_parser(Parser: object, output_loc: str):
    parser = Parser(output_loc)
    parser.run()


# run parser given user settings input
def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("crawler", metavar="crawler", type=str)
    argp.add_argument(
        "-o", metavar="output_loc", required=True, help="Specify output location"
    )
    args = argp.parse_args()

    # match case for each crawler defined in crawlers lib
    match args.crawler:
        case "diksi":
            run_scrapy_spider(DiksiSpider, args.o)
        case "vprok":
            run_custom_parser(VprokParser, args.o)
        case "magnit":
            run_scrapy_spider(MagnitSpider, args.o)
        case "svetofor":
            run_scrapy_spider(SvetoforSpider, args.o)


if __name__ == "__main__":
    main()
