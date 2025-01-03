import json
import os

import subprocess

from scrapy import cmdline

from analyse import parse_scrapy_result

# run the spider, and save the result in the scrapy_result.json file.
subprocess.run(['scrapy', 'crawl', 'dividends',
                # '-a' 'ex-div=2025-01-03', # set the target ex-dividend date.
                '-O', 'data/scrapy_result.json'], check=True)

# parse the result into an Excel file.
parse_scrapy_result('data/scrapy_result.json')
