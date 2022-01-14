import json
from datetime import datetime, timedelta

import requests


"""
람다 today_rsi
"""
def get_rsi(params: dict):
    date: str = params.get('date', None)
    is_prev: str = params.get('prev', '')

    url: str = ''

    if date:
        if is_prev == 'true':
            prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily.json?orderBy="$key"&endAt="{0}"&limitToLast=1'.format(prev_date)
        elif is_prev == 'false':
            next_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily.json?orderBy="$key"&startAt="{0}"&limitToFirst=1'.format(next_date)
        else:
            url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily/{0}.json'.format(date)
    else:
        # 가장 최근
        url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily.json?orderBy="$key"&limitToLast=1'

    r = requests.get(url)
    data = json.loads(r.text)
    if r.status_code != 200:
        return {
            'statusCode': r.status_code,
            'body': json.dumps({
                'error': data['error']
            })
        }

    if not data:
        return {
            'statusCode': r.status_code,
            'body': json.dumps({
                'date': date,
                'data': []
            })
        }
    elif len(data.keys()) == 1:
        # 이전, 이후
        key = list(data.keys())[0]
        value = data[key]
    else:
        # 날짜를 지정 했을 때
        key = date
        value = data

    # 1년전 데이터 불러오기
    last_year_date = (datetime.strptime(key, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
    url = 'https://infinite-buying-default-rtdb.firebaseio.com/rsi_daily.json?orderBy="$key"&endAt="{0}"&limitToLast=1'.format(last_year_date)
    r = requests.get(url)
    last_year_data = json.loads(r.text)
    if r.status_code == 200 and last_year_data:
        last_year_data = list(last_year_data.values())[0]
    
    data = []
    for k, v in value.items():
        v['ticker'] = k
        del(v['date'])
        del(v['ave_down'])
        del(v['ave_up'])
        del(v['high'])
        del(v['low'])
        del(v['open'])
        del(v['prev_date'])
        if k in last_year_data:
            v['last_year_close'] = last_year_data[k]['close']
        data.append(v)
    
    return {
        'statusCode': r.status_code,
        'body': json.dumps({
            'date': key,
            'data': data
        })
    }

params = {
    'date': '2021-11-22',
    # 'prev': 'false',
}

print(get_rsi(params))
