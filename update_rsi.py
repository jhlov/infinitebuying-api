import datetime
import json

import FinanceDataReader as fdr
import requests
from pytz import timezone

eastern = timezone('US/Eastern')

ticker_list = [
    'BNKU',
    'DFEN',
    'DPST',
    'DUSL',
    'FAS',
    'FNGU',
    'HIBL',
    'LABU',
    'MIDU',
    'NAIL',
    'RETL',
    'SOXL',
    'TECL',
    'TNA',
    'TPOR',
    'TQQQ',
    'UPRO',
    'WANT',
    'WEBL',
    'BULZ',
    'UDOW',
    'PILL',
    'CURE',
    'DRN',
    'UTSL'
]

def update_rsi():
    # 1. 미국 시간을 얻는다.
    today = datetime.datetime.now(tz=eastern)
    print('today', today)

    # 2. 장이 끝났으면 오늘 날짜, 끝나기 전이면 어제 날짜
    if today.hour < 18:
        end_date = (today - datetime.timedelta(days=1)).date()
    else:
        end_date = today.date()

    print('end_date', end_date)

    for ticker in ticker_list:
        print('ticker', ticker)

        # 3. 제일 마지막 데이터를 부른다.
        r = requests.get('https://infinite-buying-default-rtdb.firebaseio.com/rsi/{}.json?orderBy="$key"&limitToLast=1'.format(ticker))
        if r.status_code != 200:
            print('error', r.status_code)

        dict = json.loads(r.text)
        last_date = list(dict.keys())[0]
        last_data = dict[last_date]
        print('last_data', last_data)

        # 4. 돌아가면서 업데이트
        start_date = (datetime.datetime.strptime(last_date, '%Y-%m-%d') + datetime.timedelta(days=1)).date()
        print(start_date)

        df = fdr.DataReader(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        up = 0
        down = 0
        ave_up = last_data['ave_up']
        ave_down = last_data['ave_down']
        prev_close = last_data['close']
        prev_date = last_date
        for idx, row in df.iterrows():
            date = idx.strftime('%Y-%m-%d')
            close = row.Close

            if prev_close < close:
                up = close - prev_close
            else:
                down = prev_close - close

            ave_up = (ave_up * 13 + up) / 14
            ave_down = (ave_down * 13 + down) / 14

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
            print(r)

            # 날짜 별
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily/{}/{}.json'.format(date, ticker)
            r = requests.put(url, data=json.dumps(data))
            print(r)

            up = 0
            down = 0
            prev_date = date
            prev_close = close



update_rsi()
