import pandas as pd
import numpy as np


def parse_scrapy_result(path):
    f = pd.read_json(path)

    # save the dividend record temporarily
    dividend_record = f['dividend_record']

    # set the next_dividend_amount
    f['dividend'] = [record[0]['amount'] if len(record) != 0 else None for record in dividend_record]

    f['last_sale_price'] = pd.to_numeric(f['last_sale_price'], errors='coerce')

    f['single_dividend_yield'] = f['dividend'].astype('float64') / f['last_sale_price'].astype('float64')
    f['single_dividend_yield'] = f['single_dividend_yield'].apply(lambda x: f'{x: .2%}' if not np.isnan(x) else None)

    # drop the dividend_record column to save some basic information
    f.drop(columns=['dividend_record'], inplace=True)

    # replace all the "N/A" with None
    f.replace('N/A', None, inplace=True)

    with pd.ExcelWriter('data/result.xlsx') as w:
        # save the basic information
        f.to_excel(w, sheet_name='info', index=False)

        # save the dividend record
        for i in range(len(dividend_record)):
            symbol = f['symbol'][i]
            record_f = pd.DataFrame(dividend_record[i])

            # replace all the "N/A" with None
            record_f.replace('N/A', None, inplace=True)

            # write the dividend record to the Excel file
            record_f.to_excel(w, sheet_name=f'dr_{symbol}', index=False)

    print('The result is saved in data/result.xlsx')
