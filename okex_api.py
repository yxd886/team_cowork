import hmac
import base64
import requests
import json
import datetime
import time



# apiKey = "3c672666-d452-4bd1-9c91-f29d61ee49ee"
# secreetKey= "9B9B4DC755A9137ABCC4DF0C93C4BCFF"
class okex_api():
    def __init__(self,key,secret,phase):

        self.CONTENT_TYPE = 'Content-Type'
        self.OK_ACCESS_KEY = 'OK-ACCESS-KEY'
        self.OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
        self.OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
        self.OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
        self.APPLICATION_JSON = 'application/json'


        self.key=key
        self.secret = secret
        self.phase = phase
    def get_time_stamp(self):
        now = datetime.datetime.utcnow().isoformat()
        now = now[:-3]
        now = now + 'Z'
        return now


    # signature
    def signature(self,timestamp, method, request_path, body):
        if str(body) == '{}' or str(body) == 'None':
            body = ''
        message = str(timestamp) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)


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


    def take_order(self,instrument_id, direction, price, size):
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

        response = self.post_request(url,request_path,params)

        print(response.json())
        order_id = response.json().get('order_id', '-1')
        return order_id


    #########################################################
    # get order info

    def cancel_order(self,instrument_id,order_id ):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/cancel_orders/' + order_id
        # request params
        params = {'instrument_id': instrument_id}
        # request path
        url = base_url + request_path

        response = self.post_request(url,request_path,params)
        print(response.json())


    # get depth info
    def get_depth(self,instrument_id, size):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/instruments/' + instrument_id + '/book'

        params = {'size': str(size), 'depth': '0.0001', "instrument_id": 'btc_usdt'}

        # request path
        request_path = request_path + self.parse_params_to_str(params)
        url = base_url + request_path

        response = self.get_request(url, request_path)

        print(response.json())
        return response.json()


    def get_available_qty(self,instrument_id):
        response = self.get_position(instrument_id)
        aval_qty = response['holding'][0]['avail_position']
        long_avg_cost = response['holding'][0]['avg_cost']
        return float(aval_qty), float(long_avg_cost)


    def get_account_info(self,currency):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/accounts/'
        # request path
        url = base_url + request_path
        response = self.get_request(url, request_path)
        currency_list = response.json()
        print(response.json())
        for coin in currency_list:
            if coin['currency']==currency:
                return coin
        return 0


    def get_buy1_and_sell_one(self,instrument_id):
        obj = self.get_depth(instrument_id,1)
        sell = obj["asks"][0][0]
        buy = obj["bids"][0][0]
        return float(buy), float(sell)


    def get_available_balance(self,currency,coin):
        obj1= self.get_account_info(currency)
        time.sleep(1)
        obj2 = self.get_account_info(coin)
        available_money = obj1["available"]
        freez_money = obj1["holds"]
        available_coin = obj2["available"]
        freez_coin = obj2["holds"]
        return available_money,available_coin,freez_money,freez_coin



    def get_current_price(self,instrument_id):
        depth = self.get_depth(instrument_id,1);
        price = float(depth['asks'][0][0])
        return price


    def get_order_info(self,instrument_id,order_id):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/orders/'+order_id

        params = {"instrument_id": instrument_id}

        # request path
        request_path = request_path + self.parse_params_to_str(params)
        # request path
        url = base_url + request_path

        response = self.get_request(url, request_path)
        print(response.json())
        filled_notional = float(response.json().get('filled_notional',0))
        filled_size = float(response.json().get('filled_size',1))
        if filled_size==0:
            return 0,0
        price_avg = filled_notional/filled_size
        return price_avg,filled_size

    def get_order_status(self,instrument_id,order_id):
        base_url = 'https://www.okex.com'
        request_path = '/api/spot/v3/orders/'+order_id

        params = {"instrument_id": instrument_id}

        # request path
        request_path = request_path + self.parse_params_to_str(params)
        # request path
        url = base_url + request_path

        # request header and body
        response = self.get_request(url,request_path)
        status = response.json().get('status',None)
        print(response.json())
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
        if obj=="cancelled" or obj=="filled" or obj=="failure" or obj=="canceling":
            return True
        else:
            return False
if __name__ == '__main__':

    apiKey = "3a7993f8-840a-4340-af87-3ac7ea97478f"
    secreetKey = "A08D4589CB25C6E20052F6DACF391102"
    phase = "dxyDXY835472123"
    api = okex_api(apiKey,secreetKey,phase)
    print(api.get_buy1_and_sell_one("EOS_USDT"))