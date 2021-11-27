import json
from datetime import datetime, timedelta

import requests

ticker_list = [
    'BNKU',
    'BULZ',
    'CURE',
    'DFEN',
    'DPST',
    'DRN',
    'DUSL',
    'FAS',
    'FNGU',
    'HIBL',
    'LABU',
    'MIDU',
    'NAIL',
    'PILL',
    'RETL',
    'SOXL',
    'TECL',
    'TNA',
    'TPOR',
    'TQQQ',
    'UDOW',
    'UPRO',
    'UTSL',
    'WANT',
    'WEBL',
]


def run(params: dict):
    start_date: str = params.get('start_date', None)
    end_date: str = params.get('end_date', None)

    if not start_date or not end_date:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'parameters error'
            })
        }

    # 기간 체크
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'parameters error'
            })
        }

    url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily.json?orderBy="$key"&startAt="{0}"&endAt="{1}"'.format(start_date, end_date)
    r = requests.get(url)
    data = json.loads(r.text)
    if r.status_code != 200:
        return {
            'statusCode': r.status_code,
            'body': json.dumps({
                'error': data['error']
            })
        }
    
    timestamp = []
    rsi = {}
    close = {}
    for ticker in ticker_list:
        rsi[ticker] = []
        close[ticker] = []

    data_list = []

    for k, v in data.items():
        data_list.append({
            'date': k,
            'value': v
        })

    data_list.sort(key=lambda x : x['date'])

    for data in data_list:
        timestamp.append(data['date'])
        v = data['value']
        for ticker in ticker_list:
            if ticker in v:
                rsi[ticker].append(round(v[ticker]['rsi'], 2))
                close[ticker].append(v[ticker]['close'])
            else:
                rsi[ticker].append(None)
                close[ticker].append(None)

    # 데이터가 없으면 삭제
    delete_key_list = []
    for k, v in rsi.items():
        if not any(v):
            delete_key_list.append(k)

    for key in delete_key_list:
        del(rsi[key])

    delete_key_list = []
    for k, v in close.items():
        if not any(v):
            delete_key_list.append(k)

    for key in delete_key_list:
        del(close[key])

    return {
        'statusCode': 200,
        'body': json.dumps({
            'timestamp': timestamp,
            'rsi': rsi,
            'close': close,
        })
    }


params = {
    'start_date': '2010-01-04',
    'end_date': '2020-01-08',
}

f = open("out.txt", 'w')
print(run(params), file=f)
f.close()
