__author__ = 'Ziyang'

import json, hashlib, struct, time, sys
import urllib.request


class zb_api:
    def __init__(self, mykey, mysecret):
        self.mykey = mykey
        self.mysecret = mysecret
        self.jm = ''

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
        params = "market=" + market + "&size=3"
        path = 'depth'
        obj = self.__data_api_call(path, params)
        return obj

    #  except Exception as ex:
    #      print(sys.stderr, 'zb query_account exception,', ex)
    #      return None
    def take_order(self, market, direction, price, size):
        if direction == "buy":
            trade_direction = 1
        else:
            trade_direction = 0
        params = "accesskey=" + self.mykey + "&amount=" + str(
            size) + "&currency=" + market + "&method=order&price=" + str(price) + "&tradeType=" + str(trade_direction)
        path = 'order'

        obj = self.__trade_api_call(path, params)
        # print(obj)
        id = obj.get("id", "-1")
        return id

    def get_order_info(self, market, id):
        params = "accesskey=" + self.mykey + "&currency=" + market + "&id=" + str(id) + "&method=getOrder"
        path = 'getOrder'

        obj = self.__trade_api_call(path, params)
        print(obj)
        return obj

    def is_order_complete(self, market, id):
        obj = self.get_order_info(market, id)
        if obj["status"] == 2:
            return True
        else:
            return False

    def get_available_balance(self, money, coin):
        obj = self.query_account()
        coin_list = obj["result"]["coins"]
        for item in coin_list:
            if item["enName"] == money:
                res_money = float(item["available"])
                res_freez_money = float(item["freez"])
            elif item["enName"] == coin:
                res_coin = float(item["available"])
                res_freez_coin = float(item["freez"])

        return res_money, res_coin, res_freez_money, res_freez_coin

    def get_buy1_and_sell_one(self, market):
        obj = self.get_depth(market)
        buy1 = obj["bids"][0][0]
        sell1 = obj["asks"][-1][0]
        return buy1, sell1

    def get_pending_orders(self, market):
        params = "accesskey=" + self.mykey + "&currency=" + market + "&method=getUnfinishedOrdersIgnoreTradeType&pageIndex=1&pageSize=10"
        path = 'getUnfinishedOrdersIgnoreTradeType'
        obj = self.__trade_api_call(path, params)
        # print(obj)
        return obj

    def cancel_order(self, market, id):
        params = "accesskey=" + self.mykey + "&currency=" + market + "&id=" + str(id) + "&method=cancelOrder"
        path = 'cancelOrder'
        obj = self.__trade_api_call(path, params)
        return obj

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

    def balance_account(self, money, coin):
        buy, ask = api.get_buy1_and_sell_one(market)
        avail_money, avail_coin, freez_money, freez_coin = api.get_available_balance(money, coin)
        ratio = (avail_money + freez_money) / (avail_money + freez_money + (avail_coin + freez_coin) * buy)
        print("ratio:%f" % ratio)
        if ratio < 0.48:
            sell_size = ((avail_money + avail_coin * buy) * 0.5 - avail_money) / ask
            api.take_order(market, "sell", ask, size=sell_size)
        elif ratio > 0.52:
            buy_size = (avail_money - (avail_money + avail_coin * buy) * 0.5) / buy
            api.take_order(market, "buy", buy, size=buy_size)

        while True:
            time.sleep(2.001)
            obj = api.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break

    def wait_pending_order(self, market):
        while True:
            time.sleep(2.001)
            obj = api.get_pending_orders(market)
            print(obj)
            if isinstance(obj, dict):
                break


    def create_cells(self,upper_price,lower_price,middle_high_price,middle_low_price,total_coin,cell_num):
        price_per_cell = (upper_price-lower_price)/cell_num
        upper_half_cell_num = int((upper_price-middle_high_price)/price_per_cell)
        hot_cell_num = int((middle_high_price-middle_low_price)/price_per_cell)
        lower_half_cell_num = cell_num-upper_half_cell_num-hot_cell_num
        money_for_each_area = total_coin/4
        base = 1
        d_for_upper_area = (money_for_each_area-base)/upper_half_cell_num
        base = base+upper_half_cell_num*d_for_upper_area
        d_for_hot_area = (3*money_for_each_area-base)/hot_cell_num
        base = base+hot_cell_num*d_for_hot_area
        d_for_lower_area =(total_coin-base)/lower_half_cell_num
        self.cell_money = list()
        self.cell_price = list()
        base = 1
        for i in range(upper_half_cell_num):
            self.cell_money.append(base+i*d_for_upper_area)
        base = self.cell_money[-1]+d_for_hot_area
        for i in range(hot_cell_num):
            self.cell_money.append(base+i*d_for_hot_area)
        base = self.cell_money[-1]+d_for_lower_area
        for i in range(lower_half_cell_num):
            self.cell_money.append(base+i*d_for_lower_area)

    def compute_current_num_of_coin_should_have(self,upper_price,lower_price,cell_num,current_price):
        if current_price<=lower_price:
            return self.cell_money[-1]
        if current_price>=upper_price:
            return 0
        index = int(((upper_price-current_price)/(upper_price-lower_price))*cell_num)
        print("current_price:%f"%current_price)
        print("index:%d"%index)
        print("coin_should_have:%f"%self.cell_money[index])
        return self.cell_money[index]









if __name__ == '__main__':
    access_key = '8892c7da-2c95-41e7-b303-5703d011af9e'
    access_secret = 'ac058da7-7f18-4b8a-b86f-0cc3d9a8a752'
    market = "USDT_QC"
    api = zb_api(access_key, access_secret)

    upper_price = 7.1
    middle_high_price = 6.96
    middle_low_price = 6.8
    lower_price = 6.5
    total_coin = 1200
    cell_num = 200
    current_coin_have=270
    step = (upper_price-lower_price)/cell_num

    sell_time=0
    buy_time=0
    api.create_cells(upper_price=upper_price,
                     lower_price=lower_price,
                     middle_high_price=middle_high_price,
                     middle_low_price=middle_low_price,
                     total_coin=total_coin,
                     cell_num=cell_num)



    time.sleep(1)
    buy, ask = api.get_buy1_and_sell_one(market)
    coin_should_have = api.compute_current_num_of_coin_should_have(upper_price=upper_price,lower_price=lower_price,cell_num=cell_num,current_price=buy)
    if current_coin_have-coin_should_have>0.1:
        current_coin_have = coin_should_have
        api.take_order(market, "sell", buy, size=current_coin_have-coin_should_have)
    elif current_coin_have-coin_should_have<-0.1:
        current_coin_have = coin_should_have
        api.take_order(market, "buy", ask, size=coin_should_have-current_coin_have)





    while True:
        try:
            time.sleep(1)
            buy, ask = api.get_buy1_and_sell_one(market)
            money, coin, freez_money, freez_coin = api.get_available_balance("QC", "USDT")

            coin_should_have_for_buy = api.compute_current_num_of_coin_should_have(upper_price=upper_price,
                                                                                   lower_price=lower_price,
                                                                                   cell_num=cell_num,
                                                                                   current_price=buy - step)
            coin_should_have_for_sell = api.compute_current_num_of_coin_should_have(upper_price=upper_price,
                                                                                    lower_price=lower_price,
                                                                                    cell_num=cell_num,
                                                                                    current_price=ask + step)

            print("take pair order")
            if money > (buy - step) * (coin_should_have_for_buy - current_coin_have) and coin > (
                    current_coin_have - coin_should_have_for_sell):
                sell_id = api.take_order(market, "sell", ask+step, size=current_coin_have-coin_should_have_for_sell+0.1)

                buy_id = api.take_order(market, "buy", buy-step, size=coin_should_have_for_buy-current_coin_have+0.1)
            else:
                time.sleep(4)
                continue
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(10)
            continue
        while True:
            try:
                time.sleep(4.001)
                print("current_coin_have:%f"%current_coin_have)
                print("current price:%f"%buy)
                if sell_id == "-1" or buy_id == "-1":
                    break
                if api.is_order_complete(market, sell_id):
                    current_coin_have = coin_should_have_for_sell
                    break
                time.sleep(1)
                if api.is_order_complete(market, buy_id):
                    current_coin_have = coin_should_have_for_buy
                    break
            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(5)
                continue

