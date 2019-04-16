__author__ = 'Ziyang'

import json, hashlib, struct, time, sys
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
SERVER = 'api.fcoin.com'
PORT = 80
HT= 'https://%s/v2/'
HTMRK = 'https://%s/v2/market/'
HTPBL = 'https://%s/v2/public/'
HTORD = 'https://%s/v2/orders/'
HTACT = 'https://%s/v2/accounts/'
WS = 'wss://%S/v2/ws/'

ST = 'server-time'
SYMBOLS = 'symbols'
CURRENCY = 'currencies'
TICKER = 'ticker/%s'

POST = 'POST'
GET = 'GET'

KDATA = 'candles/%s/%s'
KDATA_COLUMNS = ['id', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']
KDATA_REAL_COL = ['datetime', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']

import hmac
import hashlib
import pandas as pd
import requests
import time
import base64


class DataAPI():
    def __init__(self, key='', secret=''):
        self.http = HT % SERVER
        self.http_public = HTPBL % SERVER
        self.http_market = HTMRK % SERVER
        self.http_orders = HTORD % SERVER
        self.http_account = HTACT % SERVER
        self.key = key
        self.secret = bytes(secret,encoding = "utf8")
    def authorize(self, key='', secret=''):
        self.key = key
        self.secret = bytes(secret,encoding = "utf8")

    def signed_request(self, method, url, **params):
        param = ''
        if params:
            sort_pay = list(params.items())
            sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))

        if method == GET:
            if param:
                url = url + '?' + param
            sig_str = method + url + timestamp
        elif method == POST:
            sig_str = method + url + timestamp + param

        signature = self.get_signed(sig_str)


        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }
        #print(url)

        try:
            r = requests.request(method, url, headers=headers, json=params)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()

    def public_request(self, method, url, **params):
        try:
            r = requests.request(method, url, params=params)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        if r.status_code == 200:
            return r.json()

    def get_signed(self, sig_str):
        #print(sig_str)
        sig_str = bytes(sig_str,encoding = "utf8")
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        return signature

    def server_time(self):
        return self.public_request(GET, self.http_public + ST)['data']

    def currencies(self):
        return self.public_request(GET, self.http_public + CURRENCY)['data']

    def symbols(self):
        js = self.public_request(GET, self.http_public + SYMBOLS)['data']
        df = pd.DataFrame(js)
        return df

    def get_ticker(self, symbol):
        return self.public_request(GET, self.http_market + TICKER % symbol)

    def get_kdata(self, freq='M1', symbol=''):
        js = self.public_request(GET, self.http_market + KDATA % (freq, symbol))
        df = pd.DataFrame(js['data'])
        df['id'] = df['id'].map(lambda x: int2time(x))
        df = df[KDATA_COLUMNS]
        df.columns = KDATA_REAL_COL
        return df

    def get_balance(self):
        """get user balance"""
        return self.signed_request(GET, self.http_account + 'balance')

    def list_orders(self, **payload):
        """get orders"""
        return self.signed_request(GET, self.http_orders, **payload)

    def create_order(self, **payload):
        """create order"""
        return self.signed_request(POST, self.http_orders, **payload)

    def buy(self, symbol, price, amount):
        """buy someting"""
        return self.create_order(symbol=symbol, side='buy', type='limit', price=str(price), amount=amount)

    def sell(self, symbol, price, amount):
        """sell someting"""
        return self.create_order(symbol=symbol, side='sell', type='limit', price=str(price), amount=amount)

    def get_order(self, order_id):
        """get specfic order"""
        return self.signed_request(GET, self.http_orders + order_id)

    def cancel_order(self, order_id):
        """cancel specfic order"""
        return self.signed_request(POST, self.http_orders + '%s/submit-cancel' % order_id)

    def order_result(self, order_id):
        """check order result"""
        return self.signed_request(GET, self.http_orders + '%s/match-results' % order_id)

    def get_depth(self, level, symbol):
        """get market depth"""
        return self.public_request(GET, self.http_market + 'depth/%s/%s' % (level, symbol))

    def get_trades(self, symbol):
        """get detail trade"""
        return self.public_request(GET, self.http_market + 'trades/%s' % symbol)


def int2time(timestamp):
    timestamp = int(timestamp)
    value = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)
    return dt


class fcoin_api:
    def __init__(self, mykey, mysecret):
        self.mykey = mykey
        self.mysecret = mysecret
        reqTime = (int)(time.time() * 1000)
        self._api = DataAPI(mykey,mysecret )
        #self._ws = fcoin.init_ws()
        self.buy_order = list()
        self.sell_order = list()
        self.current_buy_order = None
        self.current_buy_order = None

    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    def __doXOr(self, s, value):
        slist = list(s.decode('utf-8'))
        for index in range(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    def __hmacSign(self, aValue, aKey):
        keyb = struct.pack("%ds" % len(aKey), aKey.encode('utf-8'))
        value = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad.encode('utf-8'))
        m.update(value)
        dg = m.digest()

        m = hashlib.md5()
        m.update(k_opad.encode('utf-8'))
        subStr = dg[0:16]
        m.update(subStr)
        dg = m.hexdigest()
        return dg

    def __digest(self, aValue):
        value = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        # print(value)
        h = hashlib.sha1()
        h.update(value)
        dg = h.hexdigest()
        return dg

    def __trade_api_call(self, path, params=''):
        try:
            SHA_secret = self.__digest(self.mysecret)
            sign = self.__hmacSign(params, SHA_secret)
            self.jm = sign
            reqTime = (int)(time.time() * 1000)
            params += '&sign=%s&reqTime=%d' % (sign, reqTime)
            url = 'https://trade.zb.com/api/' + path + '?' + params
            # print(url)
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req, timeout=2)
            doc = json.loads(res.read().decode('utf-8'))
            return doc
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            return None

    def __data_api_call(self, path, params=''):

        reqTime = (int)(time.time() * 1000)
        url = 'http://api.zb.cn/data/v1/' + path + '?' + params
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=2)
        txt = res.read().decode('utf-8')
        # print(txt)
        doc = json.loads(txt)
        return doc

    def query_account(self):

        params = "accesskey=" + self.mykey + "&method=getAccountInfo"
        path = 'getAccountInfo'

        obj = self.__trade_api_call(path, params)
        # print obj
        return obj

    def get_depth(self, market):
        # try:
        obj = self._api.get_depth("L20",market)
        return obj.get("data",None)
        #  except Exeption as ex:
        #      print(sys.stderr, 'zb query_account exception,', ex)
        #      return None

    def take_order(self, market, direction, price, size):
        while True:
            size = round(size,4)
            price=round(price,4)
            print(size)
            print(price)
            if direction == "buy":
                obj = self._api.buy(symbol=market, price=price, amount=size)
            else:
                obj = self._api.sell(symbol=market, price=price, amount=size)
            #print(obj)
            if obj:
                break
            else:
                time.sleep(1)
                continue

        id = obj.get("data", "-1")
        return id

    def get_order_info(self, market, id):
        obj = self._api.get_order(order_id=id)
        print(obj)
        return obj["data"]

    def is_order_complete(self, market, id):
        obj = self.get_order_info(market, id)
        if obj["state"]=="filled" or "canceled" in obj["state"]:
            return True
        else:
            return False

    def get_available_balance(self, money, coin):
        obj = self._api.get_balance()
        coin_list = obj["data"]
        #print(coin_list)
        for item in coin_list:
            if item["currency"] == money:
                res_money = float(item["available"])
                res_freez_money = float(item["frozen"])
            elif item["currency"] == coin:
                res_coin = float(item["available"])
                res_freez_coin = float(item["frozen"])

        return res_money, res_coin, res_freez_money, res_freez_coin

    def get_buy1_and_sell_one(self, market):
        obj = self.get_depth(market)
        buy1 = obj["bids"][0]
        sell1 = obj["asks"][0]
        return buy1, sell1

    def get_pending_orders(self, market):
        params = "accesskey=" + self.mykey + "&currency=" + market + "&method=getUnfinishedOrdersIgnoreTradeType&pageIndex=1&pageSize=10"
        path = 'getUnfinishedOrdersIgnoreTradeType'
        obj = self.__trade_api_call(path, params)
        # print(obj)
        return obj

    def cancel_order(self, market, id):
        if id=="-1":
            return None
        obj = self._api.cancel_order(id)
        return obj


    def get_total_balance(self):
        obj = self._api.get_balance()
        coin_list = obj["data"]
        #print(coin_list)
        money =0
        for item in coin_list:
            coin = item["currency"]
            available = float(item["available"])
            frozen = float(item["frozen"])
            if available<0.0001 and frozen<0.0001:
                continue
            else:
                time.sleep(0.5)
                if coin=="usdt":
                    buy1=1
                else:
                    buy1,_=self.get_buy1_and_sell_one(coin+"usdt")
                money+=(available+frozen)*buy1

        return money

        return res_money, res_coin, res_freez_money, res_freez_coin


    '''
    def balance_account(self,money,coin):
        buy,ask = api.get_buy1_and_sell_one(market)
        avail_money,avail_coin,freez_money,freez_coin = api.get_available_balance(money,coin)
        ratio = (avail_money+freez_money)/(avail_money+freez_money+(avail_coin+freez_coin)*buy)
        print("ratio:%f" % ratio)
        while(ratio>0.52 or ratio<0.48):
            buy, ask = api.get_buy1_and_sell_one(market)
            avail_money,avail_coin,freez_money,freez_coin = api.get_available_balance(money, coin)
            ratio = (avail_money+freez_money)/(avail_money+freez_money+(avail_coin+freez_coin)*buy)
            print("ratio:%f" % ratio)
            if ratio<0.48:
                sell_order_id = api.take_order(market, "sell", buy, size=1)
                time.sleep(2)
                if not api.is_order_complete(market,sell_order_id):
                    api.cancel_order(market,sell_order_id)
            elif ratio>0.52:
                buy_order_id = api.take_order(market, "buy", ask, size=1)
                time.sleep(2)
                if not api.is_order_complete(market,buy_order_id):
                    api.cancel_order(market,buy_order_id)

    '''

    def balance_account(self, money, coin,market):
        buy, ask = self.get_buy1_and_sell_one(market)
        avail_money, avail_coin, freez_money, freez_coin = self.get_available_balance(money, coin)
        ratio = (avail_money + freez_money) / (avail_money + freez_money + (avail_coin + freez_coin) * buy)
        print("ratio:%f" % ratio)
        if ratio < 0.48:
            sell_size = ((avail_money + avail_coin * buy) * 0.5 - avail_money) / ask
            self.take_order(market, "sell", ask, size=sell_size)
        elif ratio > 0.52:
            buy_size = (avail_money - (avail_money + avail_coin * buy) * 0.5) / buy
            self.take_order(market, "buy", buy, size=buy_size)

        while True:
            time.sleep(2.001)
            obj = self.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break

    def wait_pending_order(self, market):
        while True:
            time.sleep(2.001)
            obj = self.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break

    def enqueue_sell_order(self, price, size):
        self.sell_order.append((price, size))
        self.sell_order.sort(key=lambda a: a[0], reverse=False)
        self.current_sell_order = (price, size)

    def enqueue_buy_order(self, price, size):
        self.buy_order.append((price, size))
        self.buy_order.sort(key=lambda a: a[0], reverse=True)
        self.current_buy_order = (price, size)

    def dequeue_current_sell_order(self):
        if self.current_sell_order:
            self.sell_order.remove(self.current_sell_order)
            self.current_sell_order = None

    def dequeue_current_buy_order(self):
        if self.current_buy_order:
            self.buy_order.remove(self.current_buy_order)
            self.current_buy_order = None

    def handle_order_in_queue(self, market):
        print("handling sell_orders and buy orders in queue")
        for i, item in enumerate(self.sell_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = self.get_available_balance("usdt", "tusd")
            buy, ask = self.get_buy1_and_sell_one(market)
            price = item[0]
            size = item[1]
            if coin >= size:
                price = max(price,ask)
                self.take_order(market=market, direction="sell", price=price, size=size)
                continue
            else:
                self.sell_order = self.sell_order[i:]
                break

        for i, item in enumerate(self.buy_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = self.get_available_balance("usdt", "tusd")
            buy, ask = self.get_buy1_and_sell_one(market)
            price = item[0]
            size = item[1]
            if money >= price * size:
                price = min(buy,price)
                self.take_order(market=market, direction="buy", price=price, size=size)
                continue
            else:
                self.buy_order = self.buy_order[i:]
                break

    def create_cells(self, upper_price, lower_price, middle_price, total_coin, cell_num):
        price_per_cell = (upper_price - lower_price) / cell_num
        upper_half_cell_num = int((upper_price - middle_price) / price_per_cell)
        lower_half_cell_num = cell_num - upper_half_cell_num
        money_for_each_area = total_coin / 2
        base = 0
        d_for_upper_area = 2 * (money_for_each_area - base) / (upper_half_cell_num * (upper_half_cell_num - 1))
        base = money_for_each_area + (upper_half_cell_num) * d_for_upper_area
        d_for_lower_area = 2 * (total_coin - base) / (lower_half_cell_num * (lower_half_cell_num - 1))
        self.cell_money = list()
        self.cell_step = list()
        base = 0
        for i in range(upper_half_cell_num):
            if i == 0:
                self.cell_money.append(base)
            else:
                self.cell_money.append(self.cell_money[-1] + d_for_upper_area * (i + 1))
            self.cell_step.append(d_for_upper_area * (i + 1))
        base = money_for_each_area + (upper_half_cell_num) * d_for_upper_area
        for i in range(lower_half_cell_num):
            if i == 0:
                self.cell_money.append(base)
            else:
                self.cell_money.append(self.cell_money[-1] + d_for_lower_area * (lower_half_cell_num - i))
            self.cell_step.append(d_for_lower_area * (lower_half_cell_num - i))

        print(self.cell_step)
        print(self.cell_money)

    def compute_current_num_of_coin_should_have(self, upper_price, lower_price, cell_num, current_price):
        if current_price <= lower_price:
            return self.cell_money[-1]
        if current_price >= upper_price:
            return 0
        index = int(((upper_price - current_price) / (upper_price - lower_price)) * cell_num)
        # print("current_price:%f" % current_price)
        # print("index:%d" % index)
        # print("coin_should_have:%f" % self.cell_money[index])
        return self.cell_money[index]

    def compute_current_num_coin_step(self, upper_price, lower_price, cell_num, current_price):
        if current_price <= lower_price:
            return 0
        if current_price >= upper_price:
            return 0
        index = int(((upper_price - current_price) / (upper_price - lower_price)) * cell_num)
        # print("current_price:%f" % current_price)
        # print("index:%d" % index)
        # print("coin_should_have:%f" % self.cell_money[index])
        return self.cell_step[index]


