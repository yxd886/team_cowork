from fcoin_api import *

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    market = "tusdusdt"
    api = fcoin_api(access_key, access_secret)
   # api.send_heart_beat()


    size = 20
    # api.wait_pending_order(market)
    buy, ask = api.get_buy1_and_sell_one(market)
    money, coin, freez_money, freez_coin = api.get_available_balance("usdt", "tusd")
    profit = 0
    money_today = money + freez_money
    coin_today = coin + freez_coin

    lowest = 0.98
    higest = 1.02

    money_have = money + freez_money + (coin + freez_coin) * buy

    # api.balance_account("QC","USDT")


    while True:
        try:
            time.sleep(1)
            api.handle_order_in_queue(market)
            buy, ask = api.get_buy1_and_sell_one(market)
            money, coin, freez_money, freez_coin = api.get_available_balance("usdt", "tusd")
            print("money have:%f.coin have:%f"%(money + freez_money,coin + freez_coin))
            profit = money + freez_money + (coin + freez_coin) * buy - money_have
            print("!!!PROFIT:%f" % profit)
            print("!!!PROFIT: coin:%f,money:%f" % (coin + freez_coin - coin_today, money + freez_money - money_today))

            upper = ask
            lower = buy
            sell_id = "-1"
            buy_id = "-1"

            if lower > lowest and upper < higest:
                if (money >= lower * size and coin >= size):
                    print("take pair order")
                    sell_id = api.take_order(market, "sell", upper, size=size)
                    buy_id = api.take_order(market, "buy", lower, size=size)
                elif (money >= lower * size and coin < size):  # can buy but not sell
                    print("take buy order and enqueue sell order")
                    # sell_id = api.take_order(market, "sell", upper, size=size)
                    buy_id = api.take_order(market, "buy", lower, size=size)
                    api.enqueue_sell_order(price=upper, size=size)
                elif (money < lower * size and coin >= size):  # can sell but not buy
                    print("take sell order and enqueue buy order")
                    sell_id = api.take_order(market, "sell", upper, size=size)
                    api.enqueue_buy_order(price=lower, size=size)
            elif lower <= lowest:
                buy_id = api.take_order(market, "buy", lower, size=size)
                time.sleep(1)
                continue
            elif upper >= higest:
                sell_id = api.take_order(market, "sell", upper, size=size)
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
                money, coin, freez_money, freez_coin = api.get_available_balance("usdt", "tusd")
                profit = money + freez_money + (coin + freez_coin) * buy - money_have
                print("!!!PROFIT:%f,price for this step:%f" % (profit, buy))
                print(
                    "!!!PROFIT: coin:%f,money:%f" % (coin + freez_coin - coin_today, money + freez_money - money_today))
                if sell_id == "-1" and buy_id == "-1":
                    break
                if sell_id != "-1":
                    if api.is_order_complete(market, sell_id):
                        break
                    elif counter > 2 and buy_id == "-1":
                        api.cancel_order(market, sell_id)
                        api.dequeue_current_buy_order()
                        break
                    time.sleep(1)
                if buy_id != "-1":
                    if api.is_order_complete(market, buy_id):
                        break
                    elif counter > 2 and sell_id == "-1":
                        api.cancel_order(market, buy_id)
                        api.dequeue_current_sell_order()
                        break
            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(5)
                continue

