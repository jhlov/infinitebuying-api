import json

import FinanceDataReader as fdr
import numpy as np
import pandas as pd
import requests


def initRSI(ticker, start_date, end_date):
    df = fdr.DataReader(ticker, start_date, end_date)
    # print(df)

    count = 0
    ave_up = 0
    ave_down = 0
    sum_up = 0
    sum_down = 0
    prev_close = 0
    for idx, row in df.iterrows():
        date = idx.strftime('%Y-%m-%d')
        close = row.Close

        if 0 < count:
            if prev_close < close:
                up = close - prev_close
                sum_up += up
            else:
                down = prev_close - close
                sum_down += down

        if count == 13:
            ave_up = sum_up / 14
            ave_down = sum_down / 14

        if 13 < count:
            ave_up = (ave_up * 13 + up) / 14
            ave_down = (ave_down * 13 + down) / 14

        if 13 <= count:
            RSI = ave_up / (ave_up + ave_down) * 100
            print('{} {} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}'.format(ticker, date, close, up, down, ave_up, ave_down, RSI))

            data = {
                'date': date,
                'close': close,
                'open': row.Open,
                'high': row.High,
                'low': row.Low,
                'volume': row.Volume,
                'change': row.Change,
                'diff': round(close - prev_close, 2),
                'ave_up': ave_up,
                'ave_down': ave_down,
                'rsi': RSI,
                'prev_date': prev_date
            }

            # 종목 별
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi/{}/{}.json'.format(ticker, date)
            r = requests.put(url, data=json.dumps(data))

            # 날짜 별
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily/{}/{}.json'.format(date, ticker)
            r = requests.put(url, data=json.dumps(data))

            print(r)

        up = 0
        down = 0
        prev_date = date
        prev_close = close
        count += 1


# initRSI('BNKU', '2019-04-04', '2021-11-22')
# initRSI('DFEN', '2017-05-04', '2021-11-22')
# initRSI('DPST', '2015-08-20', '2021-11-22')
# initRSI('DUSL', '2017-05-04', '2021-11-22')
# initRSI('FAS', '2008-11-07', '2021-11-22')
# initRSI('FNGU', '2018-01-24', '2021-11-22')
# initRSI('HIBL', '2019-11-08', '2021-11-22')
# initRSI('LABU', '2015-05-29', '2021-11-22')
# initRSI('MIDU', '2009-01-09', '2021-11-22')
# initRSI('NAIL', '2015-08-20', '2021-11-22')
# initRSI('RETL', '2010-07-15', '2021-11-22')
# initRSI('SOXL', '2010-03-12', '2021-11-22')
# initRSI('TECL', '2008-12-18', '2021-11-22')
# initRSI('TNA', '2008-11-06', '2021-11-22')
# initRSI('TPOR', '2017-11-07', '2021-11-22')
# initRSI('TQQQ', '2010-02-11', '2021-11-22')
# initRSI('UPRO', '2009-06-26', '2021-11-22')
# initRSI('WANT', '2018-12-03', '2021-11-22')
# initRSI('WEBL', '2019-11-08', '2021-11-22')
# initRSI('BULZ', '2021-08-17', '2021-11-22')
# initRSI('UDOW', '2010-02-11', '2021-11-22')
# initRSI('PILL', '2017-11-15', '2021-11-22')
# initRSI('CURE', '2011-06-15', '2021-11-22')
# initRSI('DRN', '2009-07-16', '2021-11-22')
# initRSI('UTSL', '2017-05-03', '2021-11-22')
