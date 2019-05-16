__author__ = 'Ziyang'

import hmac
import base64
import requests
import json
import datetime
import time
import configparser
import hashlib
import time
import random




class bit_api():
    def __init__(self,key,secret,tradePWD):

        self.URL = "https://api.bitzapi.com/Market/"
        self.tradeURL = "https://api.bitzapi.com/Trade/"
        self.assetsURL = "https://api.bitzapi.com/Assets/"


        self.key=key
        self.secret = secret
        self.tradePWD = tradePWD
    def get_time_stamp(self):
        now = datetime.datetime.utcnow().isoformat()
        now = now[:-3]
        now = now + 'Z'
        return now


    # signature
    def signature(self,params):

        """
        Args:
            params: 需要进行签名的字典型参数
            secret_or_appkey: secret 是API的值    appkey是登录需要的值
        Returns: 数字指纹
        """

        iniSign = ''

        # 对字典参数进行排序
        for key in sorted(params.keys()):
            # 如果 value 为空不参与加密
            if params[key] != "":
                iniSign += key + '=' + str(params[key]) + '&'
        signs = iniSign[:-1]

        data = "%s%s" % (signs, str(self.secret))
        # 进行MD5加密
        digital = hashlib.md5(data.encode("utf8")).hexdigest().lower()

        return digital

    def api_signature(self,request_params=None):
        """
        API 接口签名
        Args:
        	request_params: 请求参数
        Returns:
        	签名完成的请求参数
        """

        params = {}
        params['apiKey'] = self.key
        params['secret'] = self.secret
        params['timeStamp'] = str(int(time.time()))
        params['nonce'] = str(random.randint(100000, 999999))
        if request_params != None:
            params.update(request_params)

        secret = params['secret']
        # 字典中去除 secret 不参与排序
        params.pop("secret")

        # 对字典参数进行签名
        params['sign'] = self.signature(params=params)

        return params


    # set request header
    def get_header(self, sign, timestamp):
        header = dict()
        header[self.CONTENT_TYPE] = self.APPLICATION_JSON
        header[self.OK_ACCESS_KEY] = self.key
        header[self.OK_ACCESS_SIGN] = sign
        header[self.OK_ACCESS_TIMESTAMP] = str(timestamp)
        header[self.OK_ACCESS_PASSPHRASE] = self.phase
        return header


    def parse_params_to_str(self,params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'

        return url[0:-1]



    ########################################################
    def get_position(self,instrument_id):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/' + instrument_id + '/position'

        # request path
        url = base_url + request_path

        response = self.get_request(url, request_path)

        return (response.json())

    def __trade_api_call(self,path,params):
        url = self.tradeURL + path
        print(url)
        response=requests.post(url,data=params)
        # print(txt)
        doc = response.json()
        return doc
    def __assets_api_call(self,path,params):
        url = self.assetsURL + path
        print(url)
        response=requests.post(url,data=params)
        # print(txt)
        doc = response.json()
        return doc
    def query_account(self):

        real_params = self.api_signature()
        path = 'getUserAssets'

        obj = self.__assets_api_call(path, real_params)
        # print obj
        return obj

    def take_order(self, market, direction, price, size):
        if direction == "buy":
            trade_direction = "1"
        else:
            trade_direction ="2"
        params = dict()
        params["type"] = trade_direction
        params["price"] = price
        params["number"] =size
        params["symbol"] = market
        params["tradePwd"]=self.tradePWD
        real_params = self.api_signature(params)
        path = 'addEntrustSheet'

        obj = self.__trade_api_call(path, real_params)
        print(obj)
        obj = obj.get("data",None)
        if obj:
            id = obj.get("id", "-1")
        else:
            id="-1"
        return id


    #########################################################
    # get order info

    def cancel_order(self,instrument_id,order_id ):
        path = "cancelEntrustSheet"

        params = {"entrustSheetId": order_id}
        real_params = self.api_signature(params)
        # request header and body
        response = self.__trade_api_call(path,real_params)


    def __data_api_call(self,path,params):
        reqTime = (int)(time.time() * 1000)
        url = self.URL + path + '?' + params
        print(url)
        response=requests.get(url)
        # print(txt)
        doc = response.json()
        return doc
    # get depth info
    def get_depth(self, market):
        # try:
        params = "symbol=" + market
        path = 'depth'
        obj = self.__data_api_call(path, params)
        return obj["data"]


    def get_available_qty(self,instrument_id):
        response = self.get_position(instrument_id)
        aval_qty = response['holding'][0]['avail_position']
        long_avg_cost = response['holding'][0]['avg_cost']
        return float(aval_qty), float(long_avg_cost)



    def get_buy1_and_sell_one(self,instrument_id):
        obj = self.get_depth(instrument_id)
        #print(obj)
        sell = obj["asks"][-1][0]
        buy = obj["bids"][0][0]
        return float(buy), float(sell)


    def get_current_price(self,instrument_id):
        depth = self.get_depth(instrument_id,1)
        price = float(depth['asks'][0][0])
        return price


    def get_available_balance(self, money, coin):
        obj = self.query_account()
        coin_list = obj["data"]["info"]
        #print(coin_list)
        res_money=0
        res_coin=0
        res_freez_money=0
        res_freez_coin=0
        for item in coin_list:
            if item["name"] == money:
                res_money = float(item["over"])
                res_freez_money = float(item["lock"])
            elif item["name"] == coin:
                res_coin = float(item["over"])
                res_freez_coin = float(item["lock"])

        return res_money, res_coin, res_freez_money, res_freez_coin



    def get_order_status(self,instrument_id,order_id):
        path = "getEntrustSheetInfo"

        params = {"entrustSheetId": order_id}
        real_params = self.api_signature(params)
        # request header and body
        response = self.__trade_api_call(path,real_params)
        print(response)
        status = response.get('data',None)
        return status

    def get_request(self,url,request_path):
        now = self.get_time_stamp()
        header =self.get_header( self.signature(now, 'GET', request_path, None), now)
        response = requests.get(url, headers=header)
        return response

    def post_request(self,url,request_path,params):
        body = json.dumps(params)
        now = self.get_time_stamp()
        header = self.get_header(self.signature(now, 'POST', request_path, body), now)
        response = requests.post(url, data=body, headers=header)
        return response
    def is_order_complete(self,instrument_id,order_id):
        obj =self.get_order_status(instrument_id,order_id)
        if not obj:
            return True
        status = str(obj["status"])
        if status=="2" or status=="3":
            return True
        else:
            return False
