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
secreetKey= "A08D4589CB25C6E20052F6DACF391102"

#apiKey = "3c672666-d452-4bd1-9c91-f29d61ee49ee"
#secreetKey= "9B9B4DC755A9137ABCC4DF0C93C4BCFF"

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
    request_path = '/api/futures/v3/'+instrument_id+'/position'

    # request path
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')

    # do request
    response = requests.get(url, headers=header)

    return(response.json())


def take_order(instrument_id,direction,price,size):
    # take order
    base_url = 'https://www.okex.com'
    request_path = '/api/futures/v3/order'
    type='0'
    if direction=='buy':
        type='1'
    if direction=='sell':
        type='3'

    print("type:"+type)

    # request params
    params = {'type': type, 'instrument_id':instrument_id, 'size': str(size),
              'price': str(price),'leverage':'10'}

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
    return response.json().get('order_id','-1')


#########################################################
# get order info

def get_order_info():
    base_url = 'https://www.okex.com'
    request_path = '/api/futures/v3/orders'

    params = {'status':'all', 'instrument_id': 'okb_usdt'}

    # request path
    request_path = request_path + parse_params_to_str(params)
    url = base_url + request_path

    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')

    # do request
    response = requests.get(url, headers=header)

    print(response.json())


def cancel_order(order_id,instrument_id):
    base_url = 'https://www.okex.com'
    request_path = '/api/futures/v3/cancel_order/'+instrument_id+'/'+order_id
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
    request_path = '/api/futures/v3/orders_pending'
    url = base_url + request_path
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None,secreetKey), now, 'dxyDXY835472123')
    response = requests.get(url, headers=header)
    print(response.json())
    return response.json()


def cancel_all_pending_orders():
    orders = get_order_pending()
    for order in orders:
        cancel_order(order['order_id'])



# get depth info
def get_depth(instrument_id,size):

    base_url = 'https://www.okex.com'
    request_path = '/api/futures/v3/instruments/'+instrument_id+'/book'

    params = {'size':str(size), 'depth': '0.01',"instrument_id":'btc_usdt'}

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
    aval_qty = response['holding'][0]['long_avail_qty']
    long_avg_cost = response['holding'][0]['long_avg_cost']
    return float(aval_qty),float(long_avg_cost)


def get_account_info(currency):
    base_url = 'https://www.okex.com'
    request_path = '/api/futures/v3/accounts/'+currency
    # request path
    url = base_url + request_path
    # request header and body
    now = get_time_stamp()
    header = get_header(apiKey, signature(now, 'GET', request_path, None, secreetKey), now, 'dxyDXY835472123')
    # do request
    response = requests.get(url, headers=header)
    print(response.json())
    return response.json()

def get_available_balance(currency):
    response = get_account_info(currency)
    unrealised_pnl = float(response['unrealized_pnl'])
    realised_pnl = float(response['realized_pnl'])
    margin_frozen = float(response['margin_frozen'])
    margin_for_unfilled = float(response['margin_for_unfilled'])
    total_avail_balance = float(response['total_avail_balance'])
    avail_balance = total_avail_balance+unrealised_pnl+realised_pnl-margin_frozen-margin_for_unfilled
    return avail_balance,unrealised_pnl

base_floatamountbuy = 6.5
base_floatamountsell = 5.5

def GetPrice(direction,instrument_id,unrealised_pnl):
    depth = get_depth(instrument_id,'200')
    amountBids = 0
    amountAsks = 0
    if direction=='buy':
        floatamountbuy = base_floatamountbuy
        for i in range(100):
            oldamount = amountBids
            amountBids = amountBids+depth['bids'][i][1]*0.025
            if amountBids>floatamountbuy and oldamount>floatamountbuy-(floatamountbuy/2.0):
                if i==0:
                    return +depth['bids'][i][0]
                else:
                    return +depth['bids'][i][0] + 0.01

    if direction=='sell':
        if unrealised_pnl<0:
            floatamountsell = base_floatamountsell*5
        else:
            floatamountsell = base_floatamountsell

        for i in range(100):
            oldamount = amountAsks
            amountAsks = amountAsks+depth['asks'][i][1]*0.025
            if amountAsks>floatamountsell and oldamount>(floatamountsell/2.0):
                if i==0:
                    return +depth['asks'][i][0]
                else:
                    return +depth['asks'][i][0] - 0.01

    return depth['bids'][i][4]+0.01

sell_order_id="-1"
buy_order_id="-1"
instrument_id = 'BTC-USD-190308'

def onTick():
    global sell_order_id
    global buy_order_id
    global instrument_id


    #可买的比特币量，_N()是平台的精度函数
    amountBuy,unrealised_pnl = get_available_balance('btc')
    print("amountBuy:%f" % amountBuy)
    amountBuy = amountBuy*5
    print("amountBuy:%f"%amountBuy)
    amountBuy = int(amountBuy/0.025)
    #可卖的比特币量，注意到没有仓位的限制，有多少就买卖多少，因为我当时的钱很少
    amountSell,long_avg_cost = get_available_qty(instrument_id)
    print("long_avg_cost:%f"%long_avg_cost)
    amountSell = int(amountSell)+1
    if amountSell>5:
        amountBuy=0
    buyPrice = GetPrice("buy",instrument_id,unrealised_pnl)
    sellPrice= GetPrice("sell",instrument_id,unrealised_pnl)
    if unrealised_pnl and sellPrice<long_avg_cost:
        sellPrice = long_avg_cost*1.005
    print("sell price:%f, buy price:%f"%(sellPrice,buyPrice))
    print("amountsell:%d,amountbuy:%d"%(amountSell,amountBuy))
    #把原有的单子全部撤销，实际上经常出现新的价格和已挂单价格相同的情况，此时不需要撤销
    if sell_order_id!='-1':
        cancel_order(sell_order_id,instrument_id)
    if buy_order_id != '-1':
        cancel_order(buy_order_id, instrument_id)


    if amountSell>0:
       sell_order_id =take_order(instrument_id,"sell",sellPrice,1);
    if amountBuy>0:
       buy_order_id= take_order(instrument_id, "buy", buyPrice, amountBuy);
    #休眠，进入下一轮循环
    time.sleep(10)

    print("\n\n\n")

global sell_order_id
global buy_order_id
global instrument_id




while True:
    try:
        onTick()
    except:
        time.sleep(5)
        continue
    else:
        continue


        