import logging
import re
import urllib
from datetime import datetime, timedelta
from typing import Any

import requests
import scrapy
from scrapy import Spider

from stock.items import DividendHistoryItem, StockItem

logging.getLogger('urllib3').setLevel(logging.INFO)


def get_summary_url(symbol, asset_class):
    return f'https://api.nasdaq.com/api/quote/{symbol}/summary?assetclass={asset_class}'


def get_dividends_url(symbol, asset_class):
    return f'https://api.nasdaq.com/api/quote/{symbol}/dividends?assetclass={asset_class}'


def get_info_url(symbol, asset_class):
    return f'https://api.nasdaq.com/api/quote/{symbol}/info?assetclass={asset_class}'


class DividendsSpider(Spider):
    name = "dividends"
    allowed_domains = ["nasdaq.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'stock.pipelines.DividendsPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # get the stocks of which ex-dividend date is tomorrow.
        self.month_abbr_to_num = \
            {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
             "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}

        # set the target date, default value is tomorrow
        self.target_date = getattr(self, 'target_date', (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))

        # set the key filter, default value is 'symbol,ex_dividend_date,single_dividend_yield',
        # keys which are not in the filter will be ignored
        self.key_filter = getattr(self, 'key_filter', 'symbol,ex_dividend_date,single_dividend_yield').split(',')

    def start_requests(self):
        url = f'https://api.nasdaq.com/api/calendar/dividends?date={self.target_date}'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs: Any):
        body = response.json()
        rows = body['data']['calendar']['rows']

        if rows is None:
            self.logger.info(f'No dividends on {self.target_date}')
            return

        for row in rows:
            # get the symbol and asset class(these arguments are needed for the api)
            symbol = row['symbol']
            href = f'https://www.nasdaq.com/market-activity/stocks/{symbol}/dividend-history'
            res = requests.get(url=href, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
            pattern = r'https://www.nasdaq.com/market-activity/(etf|stocks)/([\^a-z-]+)/dividend-history'
            url = urllib.parse.unquote(res.url)
            match = re.search(pattern, url)
            if match is None:
                print(match, res.url)
            asset_class = match.group(1)
            symbol = match.group(2)

            symbol.replace('-', '^')
            # get the summary information
            yield scrapy.Request(
                url=get_info_url(symbol, asset_class),
                callback=self.parse_info,
            )

    def parse_info(self, response, **kwargs: Any):
        stock_item = StockItem()
        body = response.json()

        stock_item['symbol'] = body['data']['symbol']
        stock_item['company_name'] = body['data']['companyName']
        stock_item['asset_class'] = body['data']['assetClass']
        stock_item['last_sale_price'] = body['data']['primaryData']['lastSalePrice']
        yield scrapy.Request(
            url=get_summary_url(stock_item['symbol'], stock_item['asset_class']),
            callback=self.parse_summary,
            meta={'stock_item': stock_item}
        )

    def parse_summary(self, response, **kwargs: Any):
        stock_item = response.meta['stock_item']
        body = response.json()

        summary_data = body['data']['summaryData']
        stock_item['annualized_dividend'] = summary_data['AnnualizedDividend']['value']
        stock_item['current_yield'] = summary_data['Yield']['value']
        high_low_str = summary_data['FiftTwoWeekHighLow']['value']
        regex = re.compile(r'\$([0-9.]+)/\$([0-9.]+)')
        match = regex.match(high_low_str)
        if match:
            stock_item['fifty_two_week_low'] = match.group(1)
            stock_item['fifty_two_week_high'] = match.group(2)

        # get the dividend history
        yield scrapy.Request(
            url=get_dividends_url(stock_item['symbol'], stock_item['asset_class']),
            callback=self.parse_dividend_record,
            meta={'stock_item': stock_item}
        )

    def parse_dividend_record(self, response, **kwargs: Any):
        stock_item = response.meta['stock_item']
        body = response.json()

        rows = body['data']['dividends']['rows']
        items = []

        def dateparse(date_str):
            if date_str == 'N/A':
                return 'N/A'
            else:
                return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")

        for row in rows:
            item = DividendHistoryItem()
            item['ex_or_eff_date'] = dateparse(row['exOrEffDate'])
            item['type'] = row['type']
            item['amount'] = row['amount']
            item['declaration_date'] = dateparse(row['declarationDate'])
            item['record_date'] = dateparse(row['recordDate'])
            item['payment_date'] = dateparse(row['paymentDate'])
            item['currency'] = row['currency']
            items.append(item)

        stock_item['dividend_record'] = items
        yield stock_item

    def close(self, reason):
        return super().close(self, reason)
