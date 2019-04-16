from fcoin_api import *

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    _coin="pax"
    _money = "usdt"
    market = _coin+_money

    api = fcoin_api(access_key, access_secret)
   # api.send_heart_beat()


    upper_price = 1.02
    middle_price = 1.00
    lower_price = 0.98
    total_coin = 700
    cell_num = 500
    step = round((upper_price - lower_price) / cell_num,4)


    sell_time = 0
    buy_time = 0
    api.create_cells(upper_price=upper_price,
                     lower_price=lower_price,
                     middle_price=middle_price,
                     total_coin=total_coin,
                     cell_num=cell_num)
    money,coin,freez_money,freez_coin = api.get_available_balance(_money,_coin)
    money_today = money+freez_money
    coin_today = coin+freez_coin

    time.sleep(1)

    buy, ask = api.get_buy1_and_sell_one(market)
    profit=0
    money,coin,freez_money,freez_coin = api.get_available_balance(_money,_coin)
    money_have = money+freez_money+(coin+freez_coin)*buy
    current_coin_have = coin+freez_coin


    print("current_coin_have:%f" % current_coin_have)
    print("available_money:%f"%money)
    print("freez_money:%f" % freez_money)

    coin_should_have = api.compute_current_num_of_coin_should_have(upper_price=upper_price, lower_price=lower_price,
                                                                   cell_num=cell_num, current_price=buy)
    print("coin should have now:%f"%coin_should_have)
    if current_coin_have - coin_should_have > 0.1:
        api.take_order(market, "sell", ask, size=current_coin_have - coin_should_have)
    elif current_coin_have - coin_should_have < -0.1:
        api.take_order(market, "buy", buy, size=coin_should_have - current_coin_have)


    buy_price = buy-step
    sell_price = ask+step
    trade_time=0

    while True:
        try:
            time.sleep(1)
            current_coin_step_for_buy = api.compute_current_num_coin_step(upper_price=upper_price,
                                                                          lower_price=lower_price,
                                                                          cell_num=cell_num,
                                                                          current_price=buy_price)

            current_coin_step_for_sell = api.compute_current_num_coin_step(upper_price=upper_price,
                                                                           lower_price=lower_price,
                                                                           cell_num=cell_num,
                                                                           current_price=sell_price)


            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            buy, ask = api.get_buy1_and_sell_one(market)

            buy_order_id="-1"
            sell_order_id="-1"
            buy_trade_price=buy
            sell_trade_price=ask
            if money > buy_price * current_coin_step_for_buy:
                if buy_price>buy:
                    buy_trade_price=buy
                else:
                    buy_trade_price=buy_price
                buy_order_id = api.take_order(market, "buy", buy_trade_price,
                                        size=current_coin_step_for_buy)
                print("set buy order!!!")
            if coin > current_coin_step_for_sell:
                if sell_price<ask:
                    sell_trade_price = ask
                else:
                    sell_trade_price=sell_price
                sell_order_id = api.take_order(market, "sell", sell_trade_price,
                                         size=current_coin_step_for_sell)
                print("set sell order!!!")

            time_now = int(time.time())
            time_local = time.localtime(time_now)
            dt = time.strftime("--------------------%Y-%m-%d %H:%M:%S------------------------", time_local)
            print(dt)
            current_coin_have = coin + freez_coin
            print("current_coin_have:%f" % current_coin_have)
            print("available_money:%f" % money)
            print("freez_money:%f" % freez_money)

            profit = money+freez_money+(coin+freez_coin)*buy-money_have
            print("!!!PROFIT: coin:%f,money:%f"%(coin+freez_coin-coin_today,money+freez_money-money_today))
            print("!!!PROFIT:%f,current_price_for_step:%f"%(profit,buy))

            print("sell_price:%f"%(sell_price))
            print("buy_price :%f" % (buy_price))

            print("current_sell:%f" % ask)
            print("current_buy :%f"%buy)

            print("trade_time:%d"%trade_time)

            while True:
                time.sleep(5)

                buy, ask = api.get_buy1_and_sell_one(market)
                profit = money + freez_money + (coin + freez_coin) * buy - money_have
                print(
                    "!!!PROFIT: coin:%f,money:%f" % (coin + freez_coin - coin_today, money + freez_money - money_today))
                print("!!!PROFIT:%f,current_price_for_step:%f" % (profit, buy))
                print("sell_price:%f" % (sell_price))
                print("buy_price :%f" % (buy_price))

                print("current_sell:%f" % ask)
                print("current_buy :%f" % buy)

                print("trade_time:%d" % trade_time)


                if sell_order_id == "-1" and buy_order_id=="-1":
                    break
                if  sell_order_id != "-1" and api.is_order_complete(market, sell_order_id):# order success
                    trade_time+=1
                    print("sell order complete")
                    api.cancel_order(market,buy_order_id)
                    buy_price=sell_trade_price-step
                    sell_price=sell_trade_price+step
                    break
                if  buy_order_id!="-1" and api.is_order_complete(market, buy_order_id):# order success
                    trade_time+=1
                    print("buy order complete")
                    api.cancel_order(market,sell_order_id)
                    buy_price=buy_trade_price-step
                    sell_price=buy_trade_price+step
                    break

                print("order not complete")
                continue

        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(5)

            continue
