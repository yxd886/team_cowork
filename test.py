from zb_api import *


if __name__ == '__main__':
    access_key = '0996f2f2-0bc6-4d1b-ba3d-e5f6349dc896'
    access_secret = '65304341-2666-4590-b5ef-4a8c61bcb0b8'
    _coin="USDT"
    _money = "QC"
    market = _coin+"_"+_money
    api = zb_api(access_key, access_secret)
    print(api.get_kline(market,"1min",size="10"))