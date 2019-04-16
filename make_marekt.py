import hmac
import base64
import requests
import json
import datetime
import time

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
    print("%s %s %s"%(direction,direction,direction))

    # request params
    params = {'type': 'limit', 'side':direction,'instrument_id': instrument_id, 'size': str(size),
              'price': str(price)}

    print(params)

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

    print(response.json())
    order_id = response.json().get('order_id', '-1')
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
    print(response.json())


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

    print(response.json())
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
    print(response.json())
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
    print(response.json())
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
    status = response.json().get('status',0)
    print(response.json())
    return status



price_per_iteration = 5

instrument_id="eos-okb"
open_ratio = 0.01
close_ratio = 0.012
exception = False

while True:

    ask,buy = get_buy1_sell1(instrument_id)
    if ask-0.01>buy+0.01:
        upper = ask-0.01
        lower = buy+0.01
    else:
        upper = ask
        lower = buy
    size = 0.2
    print("take pair order")
    sell_order_id=take_order(instrument_id, "sell", upper, size=size)
    buy_order_id =take_order(instrument_id, "buy", lower, size=size)
    assert(sell_order_id!='-1' or buy_order_id!='-1')

    while True:
        time.sleep(1)
        sell_status = 'none'
        buy_status = 'none'
        if(sell_order_id!='-1'):
            sell_status = get_order_status(instrument_id,sell_order_id)
        if(buy_order_id!='-1'):
            buy_status = get_order_status(instrument_id,buy_order_id)
        if sell_status=='filled':
            break;
        if buy_status=='filled':
            break;


