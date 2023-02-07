import scrapy
import re

from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def clean_price(val: str):
    return re.sub("[^\d\.]", "", val)


class DiksiProduct(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags), output_processor=TakeFirst()
    )
    price_prev = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst(),
    )
    price_cur = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_price),
        output_processor=TakeFirst(),
    )
