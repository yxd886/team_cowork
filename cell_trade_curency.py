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


# [{
#     "id": "BTC",
#     "name": “Bitcoin”，
#      "deposit": "1",
#      "withdraw": “1”,
#       “withdraw_min”:”0.000001btc”
# }, {
#     "id": "ETH",
#     "name": “Ethereum”,
#     "deposit": "1",
#      "withdraw": “1”，
#      “withdraw_min”:”0.0001eth”
#     }
#  …
# ]


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
    return response.json().get('order_id', '-1')


#########################################################
# get order info

def cancel_order(order_id, instrument_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/cancel_order/' + instrument_id + '/' + order_id
    # request params
    params = {'order_id': order_id, 'instrument_id': instrument_id}
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


def get_order_pending():
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders_pending'
    url = base_url + request_path
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    response = requests.get(url, headers=header)
    print(response.json())
    return response.json()


def cancel_all_pending_orders():
    orders = get_order_pending()
    for order in orders:
        cancel_order(order['order_id'])


# get depth info
def get_depth(instrument_id, size):
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/instruments/' + instrument_id + '/book'

    params = {'size': str(size), 'depth': '0.0001', "instrument_id": 'btc_usdt'}

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



def take_market_order(instrument_id, direction, size=None, money=None):
    # take order
    base_url = 'https://www.okex.com'
    request_path = '/api/spot/v3/orders'
    if direction == 'buy':
        print("Buy Buy Buy")
        assert(money)
        params = {'type': 'market', 'side':'buy','instrument_id': instrument_id,
          'notional': str(money)}
    if direction == 'sell':
        print("Sell Sell Sell")
        assert(size)
        params = {'type': 'market', 'side':'sell','instrument_id': instrument_id, 'size': str(size)}
    # request params
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
    return response.json().get('order_id', '-1')

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

price_per_iteration = 5

instrument_id="eos-usdt"
buy_ratio = 0.002
sell_ratio = 0.0035


order_price =3.7522
sellPrice = order_price*(1+sell_ratio)

while True:
    try:
        time.sleep(2)
        current_price = get_current_price(instrument_id)
        if current_price>order_price*(1+buy_ratio):
            order_price = order_price*(1+buy_ratio)
        ratio = (order_price-current_price)/order_price
        print("order_price:%f,current_price:%f"%(order_price,current_price))
        print(ratio)
        if current_price<order_price and ratio>=buy_ratio:
            buy_order_id = take_market_order(instrument_id, "buy", money = price_per_iteration);
            if buy_order_id != '-1':
                order_price,size = get_order_info(instrument_id,buy_order_id)
                while order_price==0:
                    time.sleep(1)
                    order_price,size = get_order_info(instrument_id,buy_order_id)
                sellPrice = order_price*(1+sell_ratio)
                take_order(instrument_id, "sell", sellPrice, size=size);
                time.sleep(10)
            else:
                order_price = get_current_price(instrument_id)
    except:
        print("warning!!!!!!!execpt!!!!!!")
        break;
        order_price = get_current_price(instrument_id)
        sellPrice = order_price * (1 + sell_ratio)
        continue
    else:
        continue

