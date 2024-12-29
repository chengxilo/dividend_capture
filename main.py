import json
import os

import subprocess

from scrapy import cmdline

# run the spider, and save the result in the scrapy_result.json file.
subprocess.run(['scrapy', 'crawl', 'dividends',
                '-a' 'target_date=2024-12-30',
                '-a', 'key_filter=symbol,ex_dividend_date,single_dividend_yield',
                '-O', 'scrapy_result.json'], check=True)

# sort the result by the dividend yield
with open('scrapy_result.json', 'r') as f:
    data = json.load(f)

data.sort(key=lambda x: x['single_dividend_yield'], reverse=True)

with open('result.json', 'w') as f:
    json.dump(data, f, indent=4)
