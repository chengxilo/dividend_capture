# dividend capture helper

This is a simple tool to help with your dividend capture strategy.

The tool will calculate the `amount / last sale price`(I will call it `single_dividend_yield` in this document) 
for those stock of which ex-dividend date is `target_date` in the nasdaq dividend calendar. 

For example, for ex-dividend date 2024-12-12, [ULTY](https://www.nasdaq.com/market-activity/etf/ulty/dividend-history),
the amount is $0.7092, and the last sale price is $9.34 when we run this tool. The `single_dividend_yield` is 0.7092 / 9.34 = 7.59%.
So if you can buy this stock before the ex-dividend date and sell it in the ex-dividend date with the same price, you can get 7.59% profit.

But dividend capture is not that simple, you should know that the stock price will drop for the ex-dividend day and 
always more than the dividend amount, so you should learn more about it before you use this tool. It's not a strategy 
which can make you always win. But it is a profitable strategy if you use it correctly.

## How to use

Just run the main.py file, and the result will be in the `result.json` file. The result will be sorted by the 
`single_dividend_yield` in descending order.

```shell
python main.py
```

And wait for the result.

You can edit the `main.py` file to change the argument of the spider which collect and filter the data. But of course, the
default argument is enough for most cases.

## Arguments

- `target_date`: The ex-dividend date of which dividend you want to capture. Default: date of tomorrow, format: yyyy-mm-dd.
- `key_filter`: Set the key filter, keys which are not in the filter will be ignored. Default: `symbol,ex_dividend_date,single_dividend_yield`