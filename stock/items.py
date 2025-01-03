# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DividendHistoryItem(scrapy.Item):
    # define the fields for your item here like:
    ex_or_eff_date = scrapy.Field()
    type = scrapy.Field()
    amount = scrapy.Field()
    declaration_date = scrapy.Field()
    record_date = scrapy.Field()
    payment_date = scrapy.Field()
    currency = scrapy.Field()


class StockItem(scrapy.Item):
    # get in the info
    symbol = scrapy.Field()
    company_name = scrapy.Field()
    asset_class = scrapy.Field()
    last_sale_price = scrapy.Field()
    exchange = scrapy.Field()

    # get the summary information
    annual_dividend = scrapy.Field()
    dividend_yield = scrapy.Field()
    fifty_two_week_low = scrapy.Field()
    fifty_two_week_high = scrapy.Field()

    # list of DividendHistoryItem
    dividend_record = scrapy.Field()

    # dividend capture information
    next_dividend_amount = scrapy.Field()
    single_dividend_yield = scrapy.Field()

    dividend_payment_date = scrapy.Field()
    ex_dividend_date = scrapy.Field()