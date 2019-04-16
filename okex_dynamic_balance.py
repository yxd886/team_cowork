import hmac
import base64
import requests
import json
import datetime
import time
from statistics import mean 

CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
APPLICATION_JSON = 'application/json'

apiKey = "3a7993f8-840a-4340-af87-3ac7ea97478f"
secreetKey = "A08D4589CB25C6E20052F6DACF391102"


# apiKey = "3c672666-d452-4bd1-9c91-f29d61ee49ee"
# secreetKey= "9B9B4DC755A9137ABCC4DF0C93C4BCFF"

def get_time_stamp():
    now = datetime.datetime.utcnow().isoformat()
    now = now[:-3]
    now = now + 'Z'
    return now


# signature
def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


# set request header
def get_header(api_key, sign, timestamp, passphrase):
    header = dict()
    header[CONTENT_TYPE] = APPLICATION_JSON
    header[OK_ACCESS_KEY] = api_key
    header[OK_ACCESS_SIGN] = sign
    header[OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[OK_ACCESS_PASSPHRASE] = passphrase
    return header


def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'

    return url[0:-1]




########################################################
def get_position(instrument_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/' + instrument_id + '/position'

    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')

    # do request
    response = requests.get(url, headers=header)

    return (response.json())


def take_order(instrument_id, direction, price, size):
    # take order
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders'
    #print("%s %s %s"%(direction,direction,direction))

    # request params
    params = {'type': 'limit', 'side':direction,'instrument_id': instrument_id, 'size': str(size),
              'price': str(price)}

    #print(params)

    # request path
    url = base_url + request_path

    # request header and body
    body = json.dumps(params)
    now = get_time_stamp()
    header = get_header(apiKey,
                        signature(now, 'POST', request_path, body, secreetKey), now,
                        'dxyDXY835472123')

    # do request
    response = requests.post(url, data=body, headers=header)

    order_id = response.json().get('order_id', '-1')
    return order_id
'''
def take_force_order(instrument_id, direction, notional=None, size=None):
    # take order
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders'

    # request params
    if direction=="buy":
        params = {'type': 'market', 'side':direction,'instrument_id': instrument_id,
                  'notional': str(notional)}
    else:
        params = {'type': 'market', 'side':direction,'instrument_id': instrument_id,
                  'size': str(size)}


    # request path
    url = base_url + request_path

    # request header and body
    body = json.dumps(params)
    now = get_time_stamp()
    header = get_header(apiKey,
                        signature(now, 'POST', request_path, body, secreetKey), now,
                        'dxyDXY835472123')

    # do request
    response = requests.post(url, data=body, headers=header)

    order_id = response.json().get('order_id', '-1')
    return order_id
'''

def take_force_order(instrument_id, direction, notional=None, size=None):

    sell1,buy1 = get_buy1_sell1(instrument_id)
    price = list()
    if direction=="buy":
        size = notional/sell1
        for i in range(int(size/0.5)):
            take_order(instrument_id,"buy",sell1,0.5)
            price.append(sell1)
            time.sleep(0.5)

    if direction=="sell":
        for i in range(int(size/0.5)):
            take_order(instrument_id,"sell",buy1,0.5)
            price.append(buy1)
            time.sleep(0.5)
    return mean(price)



                
    return order_id

#########################################################
# get order info

def cancel_order(instrument_id,order_id ):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/cancel_orders/' + order_id
    # request params
    params = {'instrument_id': instrument_id}
    # request path
    url = base_url + request_path

    # request header and body
    body = json.dumps(params)
    now = get_time_stamp()
    header = get_header(apiKey,
                        signature(now, 'POST', request_path, body, secreetKey), now,
                        'dxyDXY835472123')
    # do request
    response = requests.post(url, data=body, headers=header)


# get depth info
def get_depth(instrument_id, size):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/instruments/' + instrument_id + '/book'

    params = {'size': str(size), 'depth': '0.01', "instrument_id": instrument_id}

    # request path
    request_path = request_path + parse_params_to_str(params)
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')

    # do request
    response = requests.get(url, headers=header)

    return response.json()


def get_available_qty(instrument_id):
    response = get_position(instrument_id)
    aval_qty = response['holding'][0]['avail_position']
    long_avg_cost = response['holding'][0]['avg_cost']
    return float(aval_qty), float(long_avg_cost)


def get_account_info(currency):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/accounts/'
    # request path
    url = base_url + request_path
    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    currency_list = response.json()
    for coin in currency_list:
        if coin['currency']==currency:
            return float(coin['available'])
    return 0


def get_available_balance(currency):
    return get_account_info(currency)


def get_current_price(instrument_id):
    depth = get_depth(instrument_id,1);
    price = float(depth['asks'][0][0])
    return price


def get_buy1_sell1(instrument_id):
    depth = get_depth(instrument_id,1);
    ask_price = float(depth['asks'][0][0])
    buy_price = float(depth['bids'][0][0])
    return ask_price,buy_price



def get_order_info(instrument_id,order_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders/'+order_id

    params = {"instrument_id": instrument_id}

    # request path
    request_path = request_path + parse_params_to_str(params)
    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    filled_notional = float(response.json().get('filled_notional',0))
    filled_size = float(response.json().get('filled_size',1))
    if filled_size==0:
        return 0,0
    price_avg = filled_notional/filled_size
    return price_avg,filled_size

def get_order_status(instrument_id,order_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders/'+order_id

    params = {"instrument_id": instrument_id}

    # request path
    request_path = request_path + parse_params_to_str(params)
    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    average = response.json().get('status',0)

def get_filled_money_and_size(instrument_id,order_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders/'+order_id

    params = {"instrument_id": instrument_id}

    # request path
    request_path = request_path + parse_params_to_str(params)
    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    filled_money = float(response.json().get('filled_notional',0))
    filled_size = float(response.json().get('filled_size',0))
    print("filled_money:%f,filled_size:%f"%(filled_money,filled_size))

    return filled_money,filled_size

def get_kline(instrument_id,granularity):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/instruments/'+instrument_id+'/candles'

    params = {"instrument_id": instrument_id,"granularity":granularity}

    # request path
    request_path = request_path + parse_params_to_str(params)
    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    status = response.json()
    kline = [float(item[4]) for item in status]
    return kline

def get_ma(instrument_id,granularity,level):
    kline = get_kline(instrument_id,granularity)
    ma = list()
    for i in range(int(len(kline)/level)):
        _sum = sum(kline[i:i+level])
        average = float(_sum/level)
        ma.append(average)
    return ma

instrument_id="eos-okb"
granularity="3600"

coin = "EOS"
money = "OKB"
balance_step = 0.025
balance_timeout= 10
last_buy_average_price=2.84
last_sell_average_price=2.79
currency_have = 270
smallest_money=1
smallest_amount=1
state="sought"


def balance_account():
    global last_buy_average_price
    global last_sell_average_price
    print("last buy average:%f,last_sell_average_price:%f"%(last_buy_average_price,last_sell_average_price))
    current_money = get_available_balance(money)
    current_coin = get_available_balance(coin)
    sell1,buy1 = get_buy1_sell1(instrument_id)
    balance = False
    balanced = False
    print("current_money:%f,current_coin:%f,buy1:%f,sell1:%f"%(current_money,current_coin,buy1,sell1))
    ratio = (current_coin*buy1)/(current_coin*buy1+current_money)
    print("!!!!!!!!!!!!!!!!!!!Profit:%f"%(current_coin*buy1+current_money-currency_have))
    print("ratio:%f"%ratio)
    print("current_sell1:%f,current_buy1:%f"%(sell1,buy1))
    '''
    if(ratio<0.48 and sell1<last_sell_average_price):
        balance=True
        print("begin balance buy!!!")
        order_id1 = take_order(instrument_id, "buy", sell1, size=balance_step)
        order_id2 = take_order(instrument_id, "buy", sell1, size=balance_step)
        order_id3 = take_order(instrument_id, "buy", sell1, size=balance_step)

    if(ratio>0.52 and buy1>last_buy_average_price):
        balance = True
        print("begin balance sell!!!")
        order_id1 = take_order(instrument_id, "sell", buy1, size=balance_step)
        order_id2 = take_order(instrument_id, "sell", buy1, size=balance_step)
        order_id3 = take_order(instrument_id, "sell", buy1, size=balance_step)
    if(ratio<=0.52 and ratio>=0.48):
        balanced = True
    time.sleep(balance_timeout)
    if balance:
    	cancel_order(instrument_id, order_id1)
    	cancel_order(instrument_id, order_id2)
    	cancel_order(instrument_id, order_id3)
    '''
    return balanced,buy1,sell1,ratio

def on_tick():
    time.sleep(1)
    global last_buy_average_price
    global last_sell_average_price
    global granularity
    global state
    balanced,buy1,sell1,ratio=balance_account()
    bull = False
    bear = False
    current_money = get_available_balance(money)
    current_coin = get_available_balance(coin)
    ma5 = get_ma(instrument_id,granularity,5)
    ma10 = get_ma(instrument_id,granularity,10)
    ma20 = get_ma(instrument_id,granularity,20)
    print("ma5[0]:%f,ma10[0]:%f,ma5[1]:%f,,ma10[1]:%f"%(ma5[0],ma10[0],ma5[1],ma10[1]))


    if(balanced and state=="bought" and sell1< last_buy_average_price):
        print("buy buy to achieve imbalance!")
        order_id1 = take_order(instrument_id, "buy", sell1, size=current_money/sell1)
        time.sleep(0.5)
        cancel_order(instrument_id, order_id1)  
    elif(balanced and state=="sought" and buy1 > last_sell_average_price):
        print("sell sell  to achieve imbalance!")
        order_id1 = take_order(instrument_id, "sell", buy1, size=current_coin)
        time.sleep(0.5)
        cancel_order(instrument_id, order_id1)

    if(ma5[0]>ma10[0] and buy1>ma20[0] and ratio<0.52):
        bull = True
        bear = False
    elif(ma5[0]<ma10[0] and sell1<ma20[0] and ratio>0.48):
        bear = True
        bull = False
    if(not bull and not bear):
        return
    elif(bull):
        print("BULL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!BUY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        last_buy_average_price=take_force_order(instrument_id,"buy",notional=current_money)
       # filled_money,filled_size = get_filled_money_and_size(instrument_id,id)
       # while(filled_size==0):
       #     time.sleep(0.5)
       #     filled_money, filled_size = get_filled_money_and_size(instrument_id, id)
       # last_buy_average_price = float(filled_money/filled_size)
        state="bought"
    elif(bear):
        print("BEAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!SELL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        last_sell_average_price=take_force_order(instrument_id,"sell",size=current_coin)
        #filled_money,filled_size = get_filled_money_and_size(instrument_id,id)
        #while(filled_size==0):
        #    time.sleep(0.5)
        #    filled_money, filled_size = get_filled_money_and_size(instrument_id, id)
        #last_sell_average_price = float(filled_money/filled_size)
        state="sought"


#print(take_force_order(instrument_id,"sell",size=3.5))
while True:
    on_tick()
