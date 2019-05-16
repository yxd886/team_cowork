from zb_api import *


def calculate_percentage(price, kline_list):
    start = 0
    end = 0
    for i in range(len(kline_list)):
        if price>kline_list[i]:
            start = i
        else:
            break
    for i in range(len(kline_list)):
        if price >= kline_list[i]:
            end = i
        else:
            break
    print("start",start)
    print("end",end)
    return (start+end)/2/len(kline_list)


access_key = '8892c7da-2c95-41e7-b303-5703d011af9e'
access_secret = 'ac058da7-7f18-4b8a-b86f-0cc3d9a8a752'
_coin = "USDT"
_money = "QC"
market = _coin + "_" + _money
market2="BTC_USDT"
api = zb_api(access_key, access_secret)

obj = api.get_kline(market,"1day",size="1000")
print(obj)
kline_list = [item[-2] for item in obj["data"]]
kline_list.sort()
print(kline_list)


obj = api.get_kline(market2,"1day",size="1000")
print(obj)
kline_list2 = [item[-2] for item in obj["data"]]
kline_list2.sort()
print(kline_list2)
print(len(kline_list2))

buy, ask = api.get_buy1_and_sell_one(market2)
percentage_position = calculate_percentage(buy, kline_list2)
print("percentage:%f" % percentage_position)

'''
while True:
    money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
    money_have = money+freez_money
    coin_have = coin+freez_coin
    buy, ask = api.get_buy1_and_sell_one(market)
    ratio = coin_have*buy/(money_have+coin_have*buy)

    percentage_position =calculate_percentage(buy,kline_list)
    print("percentage:%f"%percentage_position)



'''