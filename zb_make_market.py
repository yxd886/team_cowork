__author__ = 'Ziyang'

import json, hashlib, struct, time, sys
import urllib.request


class zb_api:
    def __init__(self, mykey, mysecret):
        self.mykey = mykey
        self.mysecret = mysecret
        self.jm = ''
        self.buy_order=list()
        self.sell_order=list()
        self.current_buy_order=None
        self.current_buy_order=None

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
        #print(value)
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
            #print(url)
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
        #print(txt)
        doc = json.loads(txt)
        return doc


    def query_account(self):

        params = "accesskey=" + self.mykey + "&method=getAccountInfo"
        path = 'getAccountInfo'

        obj = self.__trade_api_call(path, params)
        # print obj
        return obj


    def get_depth(self,market):
       # try:
            params = "market="+market+"&size=3"
            path = 'depth'
            obj = self.__data_api_call(path, params)
            return obj
      #  except Exception as ex:
      #      print(sys.stderr, 'zb query_account exception,', ex)
      #      return None
    def take_order(self,market,direction,price,size):
        if direction=="buy":
            trade_direction=1
        else:
            trade_direction=0
        params = "accesskey=" + self.mykey +"&amount="+str(size)+"&currency="+market+"&method=order&price="+str(price)+"&tradeType="+str(trade_direction)
        path = 'order'

        obj = self.__trade_api_call(path, params)
        #print(obj)
        id = obj.get("id","-1")
        return id


    def get_order_info(self,market,id):
        params = "accesskey=" + self.mykey +"&currency="+market+"&id="+str(id)+"&method=getOrder"
        path = 'getOrder'

        obj = self.__trade_api_call(path, params)
        print(obj)
        return obj


    def is_order_complete(self,market,id):
        obj = self.get_order_info(market,id)
        if obj["status"]==2:
            return True
        else:
            return False
    def get_available_balance(self,money,coin):
        obj = self.query_account()
        coin_list= obj["result"]["coins"]
        for item in coin_list:
            if item["enName"]==money:
                res_money = float(item["available"])
                res_freez_money = float(item["freez"])
            elif item["enName"] == coin:
                res_coin = float(item["available"])
                res_freez_coin = float(item["freez"])

        return res_money,res_coin,res_freez_money,res_freez_coin

    def get_buy1_and_sell_one(self,market):
        obj = self.get_depth(market)
        buy1 = obj["bids"][0][0]
        sell1=obj["asks"][-1][0]
        return buy1,sell1


    def get_pending_orders(self,market):
        params = "accesskey=" + self.mykey +"&currency="+market+"&method=getUnfinishedOrdersIgnoreTradeType&pageIndex=1&pageSize=10"
        path = 'getUnfinishedOrdersIgnoreTradeType'
        obj = self.__trade_api_call(path, params)
        #print(obj)
        return obj

    def cancel_order(self,market,id):
        params = "accesskey=" + self.mykey +"&currency="+market+"&id="+str(id)+"&method=cancelOrder"
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


    def balance_account(self,money,coin):
        buy,ask = api.get_buy1_and_sell_one(market)
        avail_money,avail_coin,freez_money,freez_coin = api.get_available_balance(money,coin)
        ratio = (avail_money+freez_money)/(avail_money+freez_money+(avail_coin+freez_coin)*buy)
        print("ratio:%f" % ratio)
        if ratio<0.48:
            sell_size = ((avail_money+avail_coin*buy)*0.5-avail_money)/ask
            api.take_order(market, "sell", ask, size=sell_size)
        elif ratio>0.52:
            buy_size = (avail_money - (avail_money+avail_coin*buy)*0.5)/buy
            api.take_order(market, "buy", buy, size=buy_size)
        
        while True:
            time.sleep(2.001)
            obj = api.get_pending_orders(market)
            print(obj)
            if isinstance(obj,dict):
                break
    def wait_pending_order(self,market):
        while True:
            time.sleep(2.001)
            obj = api.get_pending_orders(market)
            print(obj)
            if isinstance(obj,dict):
                break

    def enqueue_sell_order(self,price,size):
        self.sell_order.append((price,size))
        self.sell_order.sort(key= lambda a:a[0],reverse=False)
        self.current_sell_order = (price,size)

    def enqueue_buy_order(self,price,size):
        self.buy_order.append((price,size))
        self.buy_order.sort(key= lambda a:a[0],reverse=True)
        self.current_buy_order = (price, size)

    def dequeue_current_sell_order(self):
        if self.current_sell_order:
            self.sell_order.remove(self.current_sell_order)
            self.current_sell_order=None
    def dequeue_current_buy_order(self):
        if self.current_buy_order:
            self.buy_order.remove(self.current_buy_order)
            self.current_buy_order=None

    def handle_order_in_queue(self,market):
        print("handling sell_orders and buy orders in queue")
        for i,item in enumerate(self.sell_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = api.get_available_balance("QC", "USDT")
            price = item[0]
            size = item[1]
            if coin>=size:
                self.take_order(market=market,direction="sell",price=price,size=size)
                continue
            else:
                self.sell_order=self.sell_order[i:]
                break

        for i,item in enumerate(self.buy_order):
            time.sleep(1)
            money, coin, freez_money, freez_coin = api.get_available_balance("QC", "USDT")
            price = item[0]
            size = item[1]
            if money>=price*size:
                self.take_order(market=market,direction="buy",price=price,size=size)
                continue
            else:
                self.buy_order=self.buy_order[i:]
                break


if __name__ == '__main__':
    access_key = '8892c7da-2c95-41e7-b303-5703d011af9e'
    access_secret = 'ac058da7-7f18-4b8a-b86f-0cc3d9a8a752'
    market="USDT_QC"
    api = zb_api(access_key, access_secret)
    size = 10
    #api.wait_pending_order(market)
    buy,ask = api.get_buy1_and_sell_one(market)
    money,coin,freez_money,freez_coin = api.get_available_balance("QC","USDT")
    profit=0
    money_today = money+freez_money
    coin_today = coin+freez_coin

    lowest = 6.66
    higest =7.05

    money_have = money+freez_money+(coin+freez_coin)*buy

    #api.balance_account("QC","USDT")
    while True:
        try:
            time.sleep(1)
            api.handle_order_in_queue(market)
            buy,ask = api.get_buy1_and_sell_one(market)
            money,coin,freez_money,freez_coin = api.get_available_balance("QC","USDT")
            profit = money+freez_money+(coin+freez_coin)*buy-money_have
            print("!!!PROFIT:%f"%profit)
            print("!!!PROFIT: coin:%f,money:%f"%(coin+freez_coin-coin_today,money+freez_money-money_today))

            upper = ask
            lower = buy
            sell_id="-1"
            buy_id ="-1"
            
            if upper>lowest and lower<higest:
                if (money>=lower*size and coin>=size):
                    print("take pair order")
                    sell_id = api.take_order(market, "sell", upper, size=size)
                    buy_id = api.take_order(market, "buy", lower, size=size)
                elif(money>=lower*size and coin<size): #can buy but not sell
                    print("take buy order and enqueue sell order")
                   # sell_id = api.take_order(market, "sell", upper, size=size)
                    buy_id = api.take_order(market, "buy", lower, size=size)
                    api.enqueue_sell_order(price=upper,size=size)
                elif(money<lower*size and coin>=size):#can sell but not buy
                    print("take sell order and enqueue buy order")
                    sell_id = api.take_order(market, "sell", upper, size=size)
                    api.enqueue_buy_order(price=lower,size=size)
            elif upper<=lowest:
                buy_id = api.take_order(market, "buy", upper, size=size)
                time.sleep(1)
                continue
            elif lower>=higest:
                sell_id = api.take_order(market, "sell", lower, size=size)
                time.sleep(1)
                continue
            else:
                time.sleep(4)
                continue

        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(10)
            continue
        counter = 0
        while True:
            try:
                counter += 1
                time.sleep(4.001)
                print("in waiting order complete")
                print("!!!PROFIT:%f,price for this step:%f"%(profit,buy))
                print("!!!PROFIT: coin:%f,money:%f"%(coin+freez_coin-coin_today,money+freez_money-money_today))
                if sell_id=="-1" and buy_id=="-1":
                    break
                if sell_id != "-1":
                    if api.is_order_complete(market,sell_id):
                        break
                    elif counter>10 and buy_id=="-1":
                        api.cancel_order(market,sell_id)
                        api.dequeue_current_buy_order()
                        break
                    time.sleep(1)
                if buy_id != "-1":
                    if api.is_order_complete(market,buy_id):
                        break
                    elif counter>10 and sell_id=="-1":
                        api.cancel_order(market,buy_id)
                        api.dequeue_current_sell_order()
                        break
            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(5)
                continue
