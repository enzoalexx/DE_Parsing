# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose


def parse_param_names(params):
    return {k: v.replace('\n', '').strip() for k, v in params.items()}


def handle_params(params):
    key, value = '', ''
    params_dict = {}
    for n in range(len(params)):
        if n % 2 == 0:
            key = params[n]
        else:
            params_dict[key] = params[n]
    return params_dict


def parse_price(price):
    value_str = price.replace(' ', '')
    try:
        return float(value_str)
    except ValueError:
        print(f'Cannot convert price str {price} to number')


class LmparserItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()  #output_processor=TakeFirst()
    photos = scrapy.Field()
    params = scrapy.Field(input_processor=Compose(parse_param_names, handle_params))  #
    url = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(parse_price))  # output_processor=TakeFirst(),
