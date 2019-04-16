from zb_api import *


if __name__ == '__main__':
    access_key = '16e04c69-2d0d-4f1d-8304-55983930c485'
    access_secret = '435a1a5a-986a-4d0a-8168-507a707e1237'
    _coin="USDT"
    _money = "QC"
    market = _coin+"_"+_money
    api = zb_api(access_key, access_secret)

    upper_price = 7.04
    middle_price = 6.95
    lower_price = 6.7
    total_coin = 830
    cell_num = 100
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
            time.sleep(2)
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
        except Exception as ex:
            print(sys.stderr, 'First_exception: ', ex)
            continue
            time.sleep(5)
        while True:
            try:
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
                if sell_order_id != "-1" and api.is_order_complete(market, sell_order_id):# order success
                    trade_time+=1
                    print("sell order complete")
                    api.cancel_order(market,buy_order_id)
                    buy_price=sell_trade_price-step
                    sell_price=sell_trade_price+step
                    break
                if buy_order_id!="-1" and api.is_order_complete(market, buy_order_id):# order success
                    trade_time+=1
                    print("buy order complete")
                    api.cancel_order(market,sell_order_id)
                    buy_price=buy_trade_price-step
                    sell_price=buy_trade_price+step
                    break

                print("order not complete")
                continue

            except Exception as ex:
                print(sys.stderr, 'second_exception: ', ex)
                time.sleep(5)
                continue
