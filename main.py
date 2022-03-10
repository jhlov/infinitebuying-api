import json
from datetime import datetime, timedelta

import yfinance as yf
from pandas_datareader import data as pdr

yf.pdr_override()


def can_sell(order_type: str, price_type: str, rate: float, avg_price: float, yesterday_close: float, high: float,
             close: float) -> float:
    """
    매도 가능한지 여부
    Parameters
    ----------
    order_type (str): 주문 조건, (loc or 지정가)
    price_type (str): 주문 가격 조건, (평단가 or 전날 종가)
    rate (float): 주문 가격 퍼센트
    avg_price (float): 평단가
    yesterday_close (float): 전날 종가
    high (float): 오늘 고가
    close (float): 오늘 종가

    Returns
    -------
    매도 가능하면 true 리턴
    """
    order_price: float = get_order_price(price_type, rate, avg_price, yesterday_close)

    if order_type == 'loc':
        return order_price <= close

    if order_type == 'limitOrder':
        return order_price <= high


def get_order_price(price_type: str, rate: float, avg_price: float, yesterday_close: float) -> float:
    """
    거래 주문 가격
    Parameters
    ----------
    price_type (str): 주문 가격 조건, (평단가 or 전날 종가)
    rate (float): 주문 가격 퍼센트
    avg_price (float): 평단가
    yesterday_close (float): 전날 종가

    Returns
    -------
    주문 가격
    """
    order_price: float = avg_price if price_type == 'avgPrice' else yesterday_close
    return round(order_price * (100 + rate) / 100, 2)


def get_bid_price(order_type: str, price_type: str, rate: float, avg_price: float, yesterday_close: float,
                  close: float) -> float:
    """
    실제 매도 or 매수 거래된 금액
    Parameters
    ----------
    order_type (str): 주문 조건, (loc or 지정가)
    price_type (str): 주문 가격 조건, (평단가 or 전날 종가)
    rate (float): 주문 가격 퍼센트
    avg_price (float): 평단가
    yesterday_close (float): 전날 종가
    close (float): 오늘 종가

    Returns
    -------
    거래 금액
    """
    if order_type == 'loc':
        return close

    if order_type == 'limitOrder':
        return get_order_price(price_type, rate, avg_price, yesterday_close)


def can_buy(order_type: str, price_type: str, rate: float, avg_price: float, yesterday_close: float, high: float,
            close: float) -> float:
    """
    구매 가능 여부
    Parameters
    ----------
    order_type (str): 주문 조건, (loc or 지정가)
    price_type (str): 주문 가격 조건, (평단가 or 전날 종가)
    rate (float): 주문 가격 퍼센트
    avg_price (float): 평단가
    yesterday_close (float): 전날 종가
    high (float): 오늘 고가
    close (float): 오늘 종가

    Returns
    -------
    구매 가능 여부
    """
    order_price: float = get_order_price(price_type, rate, avg_price, yesterday_close)

    if order_type == 'loc':
        return close <= order_price

    if order_type == 'limitOrder':
        return order_price <= high


def run(params: dict):
    """
    백테스트 시작
    Parameters
    ----------
    params

    Returns
    -------

    """
    stock: str = params['stock']
    start_date: str = params['startDate']
    money: float = float(params['money'])
    total_days: int = int(params['totalDays'])
    first_buying_price_type: str = params["firstBuyingPriceType"]
    buying1_condition = {
        'order_type': params['buying1OrderType'],
        'price_type': params['buying1PriceType'],
        'rate': float(params['buying1Rate']),
    }

    buying2_condition = {
        'order_type': params['buying2OrderType'],
        'price_type': params['buying2PriceType'],
        'rate': float(params['buying2Rate']),
    }

    selling_condition = {
        'order_type': params['sellingOrderType'],
        'price_type': params['sellingPriceType'],
        'rate': float(params['sellingRate']),
    }

    money_per_day = money / total_days  # 하루 투자금액

    end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=365)
    end_date = end_date.strftime('%Y-%m-%d')
    try:
        # df = fdr.DataReader(stock, start_date, end_date)
        df = pdr.get_data_yahoo(stock, start=start_date, end=end_date)
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': '잘못된 요청입니다.',
            })
        }

    step: int = 0  # 회차
    days: int = 0  # 일자
    total_count: int = 0  # 총 보유 개수
    total_price: float = 0  # 총 매수금
    avg_price: float = 0  # 평단가
    yesterday_close_price: float = 0  # 전날 종가

    buying_info = []
    sell_info = None

    for date_idx, row in df.iterrows():
        days += 1

        # 매수 정보 초기화
        buying_price: float = 0
        buying_count: int = 0

        if days == 1:
            # 첫날 구매
            step = 2

            if first_buying_price_type == 'open':
                buying_price = row.Open
            elif first_buying_price_type == 'close':
                buying_price = row.Close

            buying_count = max(2, int(money_per_day / buying_price))  # 최소 2개
        else:
            # 1. 매도(매도되면 매수는 패스)
            if can_sell(selling_condition['order_type'], selling_condition['price_type'], selling_condition['rate'],
                        avg_price, yesterday_close_price, row.High, row.Close):
                # print('매도')

                sell_price: float = get_bid_price(selling_condition['order_type'], selling_condition['price_type'],
                                                  selling_condition['rate'],
                                                  avg_price, yesterday_close_price, row.Close)

                evaluated_price: float = sell_price * total_count  # 평가금
                profits: float = evaluated_price - total_price  # 수익금
                profits_rate: float = profits / total_price  # 수익률
                total_money_profits_rate: float = profits / money  # 원금 대비 수익률

                # print(
                #     '회차: {0} | 날짜: {1} | 종가: {2} | 매도단가: {3:,.2f} | 매도개수: {4} | 평가금: {5:,.2f} | 총매수금: {6:,.2f} | 수익금: {7:,.2f} | 수익률: {8:.1f} | 원금대비수익률: {9:.1f}'.format(
                #         math.ceil(step / 2), date_idx.strftime('%Y-%m-%d'), row.Close, sell_price, total_count,
                #         evaluated_price, total_price, profits, profits_rate * 100, total_money_profits_rate * 100))

                sell_info = {
                    'days': days,
                    'date': date_idx.strftime('%Y-%m-%d'),
                    'close': row.Close,
                    'sell_unit_price': sell_price,
                    'sell_count': total_count,
                    'evaluated_price': evaluated_price,
                    'total_price': total_price,
                    'profits': profits,
                    'profits_rate': profits_rate,
                    'total_money_profits_rate': total_money_profits_rate
                }
                break

            # 2. LOC 평단매수
            if can_buy(buying1_condition['order_type'], buying1_condition['price_type'], buying1_condition['rate'],
                       avg_price, yesterday_close_price, row.High, row.Close):
                buying_price = get_bid_price(buying1_condition['order_type'], buying1_condition['price_type'],
                                             buying1_condition['rate'],
                                             avg_price, yesterday_close_price, row.Close)
                buying_count += max(1, int(money_per_day / 2 / buying_price))
                step += 1

            # 2. LOC 큰수매수
            if can_buy(buying2_condition['order_type'], buying2_condition['price_type'], buying2_condition['rate'],
                       avg_price, yesterday_close_price, row.High, row.Close):
                buying_price = get_bid_price(buying2_condition['order_type'], buying2_condition['price_type'],
                                             buying2_condition['rate'],
                                             avg_price, yesterday_close_price, row.Close)
                buying_count += max(1, int(money_per_day / 2 / buying_price))
                step += 1

        total_count += buying_count
        total_price += buying_count * buying_price
        avg_price = total_price / total_count  # 평단가

        evaluated_price = row.Close * total_count  # 평가금
        profits = evaluated_price - total_price  # 수익금
        profits_rate = profits / total_price  # 수익률
        total_money_profits_rate = profits / money  # 원금 대비 수익률

        buying_info.append({
            'days': days,
            'date': date_idx.strftime('%Y-%m-%d'),
            'close': row.Close,
            'buying_count': buying_count,
            'buying_price': buying_price * buying_count,
            'avg_price': avg_price,
            'total_count': total_count,
            'evaluated_price': evaluated_price,
            'total_price': total_price,
            'profits': profits,
            'profits_rate': profits_rate,
            'total_money_profits_rate': total_money_profits_rate
        })

        yesterday_close_price = row.Close

        # print(
        #     '회차: {0} | 날짜: {1} | 종가: {2} | 매수단가: {3} | 매수개수: {4} | 평단가: {5:.2f} | 보유개수: {6} | 평가금: {7:,.2f} | 총매수금: {8:,.2f} | 수익금: {9:,.2f} | 수익률: {10:.1f} | 원금대비수익률: {11:.1f}'.format(
        #         math.ceil(step / 2), date_idx.strftime('%Y-%m-%d'), row.Close, buying_price, buying_count, avg_price,
        #         total_count, evaluated_price, total_price, profits, profits_rate * 100, total_money_profits_rate * 100))

        if total_days * 2 <= step:
            break

    return {
        'statusCode': 200,
        'body': json.dumps({
            'buying_info': buying_info,
            'sell_info': sell_info
        })
    }


_params = {
    "stock": "TQQQ",
    "startDate": "2021-01-01",
    "money": 10000,
    "totalDays": 40,
    "firstBuyingPriceType": "close",
    "buying1OrderType": "loc",
    "buying1PriceType": "avgPrice",
    "buying1Rate": 0,
    "buying2OrderType": "loc",
    "buying2PriceType": "avgPrice",
    "buying2Rate": 15,
    "sellingOrderType": "limitOrder",
    "sellingPriceType": "avgPrice",
    "sellingRate": 10
}

# run('TQQQ', '2020-01-01')
r = run(_params)
print(r)
