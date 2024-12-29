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
        item['last_sale_price'] = item['last_sale_price'][1:]
        item['annualized_dividend'] = item['annualized_dividend'][1:]

        # remove the ex-dividend record after the target date
        del_idx = 0
        while item['dividend_record'][del_idx]['ex_or_eff_date'] > spider.target_date:
            del_idx += 1
        item['dividend_record'] = item['dividend_record'][del_idx:]

        item['ex_dividend_date'] = item['dividend_record'][0]['ex_or_eff_date']
        item['dividend_payment_date'] = item['dividend_record'][0]['payment_date']
        # remove the $ sign
        for dividend in item['dividend_record']:
            dividend['amount'] = dividend['amount'][1:]

        if len(item['dividend_record']) != 0:
            item['next_dividend_amount'] = item['dividend_record'][0]['amount']
            item['single_dividend_yield'] = \
                ('{:.2%}'.format(float(item['next_dividend_amount']) / float(item['last_sale_price'])))

        shall_delete = []
        for key in item.keys():
            if key not in spider.key_filter:
                shall_delete.append(key)
        for key in shall_delete:
            del item[key]

        return item
