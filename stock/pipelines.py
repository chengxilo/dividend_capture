# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class DividendsPipeline:
    def process_item(self, item, spider):
        # This pipeline will calculate the dividend yield for the period
        # remove the $ sign
        item['last_sale_price'] = item['last_sale_price'][1:] if item['last_sale_price'] != 'N/A' else 'N/A'
        item['annual_dividend'] = item['annual_dividend'][1:] if item['annual_dividend'] != 'N/A' else 'N/A'

        # remove the ex-dividend record after the target date
        del_idx = 0
        while item['dividend_record'][del_idx]['ex_or_eff_date'] > spider.target_date:
            del_idx += 1
        item['dividend_record'] = item['dividend_record'][del_idx:]

        # get the next dividend information
        item['ex_dividend_date'] = item['dividend_record'][0]['ex_or_eff_date']
        item['dividend_payment_date'] = item['dividend_record'][0]['payment_date']
        # remove the $ sign
        for dividend in item['dividend_record']:
            dividend['amount'] = dividend['amount'][1:]

        return item
