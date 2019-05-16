from fcoin_api import *
import copy
import threading




def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2,_money,_coin,mutex1,total_filled_amount,mutex3,license_day,money_have,partition,coin_place
    counter=0
    while True:
        try:

            print("in aggregate")
            obj = api.get_depth(market)
            buy5 = obj["bids"][4 * 2]
            buy15 = obj["bids"][14 * 2]
            ask5 = obj["asks"][4 * 2]
            local_total_amount = 0

            buy_orders = list()
            buy_money = 0
            buy_amount = 0
            sell_money = 0
            sell_amount = 0
            sell_orders = list()
            local_pending_order = list()
            mutex2.acquire()
            local1_pend_order = copy.deepcopy(pending_orders)
            print("pending order length:%d"%len(pending_orders))
            need_remove_list = list()
            mutex2.release()

            while "-1" in local1_pend_order:
                local1_pend_order.remove("-1")

            for id in local1_pend_order:
                time.sleep(1)
                item = api.get_order_info(market,id)
                if item['state']=="filled" or "canceled" in item["state"]:
                    need_remove_list.append(id)
                    continue
                else:
                    local_pending_order.append(copy.deepcopy(item))
            mutex2.acquire()
            for id in need_remove_list:
                if id in pending_orders:
                    pending_orders.remove(id)
            mutex2.release()


            print("local_pending_order length:%d" % len(local_pending_order))
            for item in local_pending_order:
                print("side:%s"%item["side"])
                if item["side"]=="buy":
                    buy_orders.append(item)
                elif item["side"] =="sell":
                    sell_orders.append(item)


            print("buy_order_num:%d" % len(buy_orders))
            print("sell_order_num:%d" % len(sell_orders))

            '''
            for i, item in enumerate(buy_orders):
                amount = float(item["amount"]) - float(item["filled_amount"])
                price = float(item["price"])
                buy_money += amount * price
                buy_amount += amount
                api.cancel_order(market, item["id"])
                time.sleep(0.5)
            local_total_amount = buy_amount
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            time.sleep(1)
            new_buy_price = min(buy5,buy_money/buy_amount)
            id = api.take_order(market, "buy", new_buy_price, min(buy_amount,money/new_buy_price))
            mutex2.acquire()
            pending_orders.append(id)
            mutex2.release()
            '''



            for i, item in enumerate(sell_orders):
                amount = float(item["amount"]) - float(item["filled_amount"])
                price = float(item["price"])
                sell_money += amount * price
                sell_amount += amount
                if counter > 3600:
                    api.cancel_order(market, item["id"])
                    time.sleep(0.5)
            local_total_amount = sell_amount
            if counter > 3600:
                time.sleep(1)
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
                new_sell_price = max(ask5, sell_money / sell_amount)
                if local_total_amount>(2/3)*(money_have*partition/ask5):
                    api.take_order(market, "sell", buy15, min(sell_amount/2, coin),coin_place)
                    time.sleep(1)
                    id = api.take_order(market, "sell", new_sell_price, coin- min(sell_amount/2, coin),coin_place)

                else:
                    id = api.take_order(market, "sell", new_sell_price, min(sell_amount, coin),coin_place)

                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()
            mutex1.acquire()
            total_filled_amount = local_total_amount
            mutex1.release()
            time.sleep(20)
            if counter>3600:
                counter=0
            counter+=20
        except Exception as ex:
            print(sys.stderr, 'in check and aggrete: ', ex)
            continue



def buy_main_body(type):
    global access_key, access_secret, _money, _coin, market, partition,min_size, money_have, api,pending_orders,mutex2,total_filled_amount,mutex1,mutex3,bidirection,license_day,coin_place,total_amount_limit
    last_buy_id = "-1"
    while True:
        try:
            counter=0
            # api.wait_pending_order(market)
            obj = api.get_depth(market)
            ask5 = obj["asks"][4*2]
            buy1 = obj["bids"][0*2]
            buy4 = obj["bids"][3 * 2]
            buy5 = obj["bids"][4*2]
            buy7 = obj["bids"][6*2]
            buy10 = obj["bids"][9*2]
            buy12 = obj["bids"][11 * 2]
            buy15 = obj["bids"][14* 2]
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            buy_id = "-1"
            if type == 1:
                price = buy12
            else:
                price = buy5
            filled_amount=0
            if bidirection==False:
                if last_buy_id!="-1":
                    time.sleep(0.1)
                    item = api.get_order_info(market,last_buy_id)
                    last_buy_id = "-1"
                    filled_amount = float(item['filled_amount'])
                    last_price = float(item['price'])
                    if filled_amount>min_size:
                        sell_order = api.take_order(market, "sell", last_price, min(filled_amount,coin),coin_place)
                        if sell_order!="-1":
                            mutex2.acquire()
                            pending_orders.append(sell_order)
                            mutex2.release()
                        time.sleep(1)
                mutex1.acquire()
                local_total_filled_amount = total_filled_amount+filled_amount
                mutex1.release()
            print("coin can buy:%f"%(min(money_have,money)/ price))
            #print("filled amount:%f"%(local_total_filled_amount/partition))
            #if (min(money_have,money)/ price -local_total_filled_amount/partition) > min_size:
            if total_amount_limit-(coin+freez_coin)>min_size:
                if bidirection == False:
                    buy_id = api.take_order(market, "buy", price, (min(money_have,money)/price-local_total_filled_amount/partition),coin_place)
                else:
                    buy_id = api.take_order(market, "buy", price,
                                            (min(total_amount_limit-(coin+freez_coin),money/price)),
                                            coin_place)
            if buy_id=="-1":
                time.sleep(1)
                continue
            # api.balance_account("QC","USDT")
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(10)
            continue
        while True:
            try:
                print("counter:%d"%counter)
                obj = api.get_depth(market)
                buy5 = obj["bids"][4 * 2]
                buy15 = obj["bids"][14 * 2]
                buy4 = obj["bids"][3 * 2]
                buy11 = obj["bids"][10 * 2]
                buy10 = obj["bids"][9 * 2]
                if type==1:
                    upper = buy11
                    lower = buy15
                else:
                    upper = buy4
                    lower = buy5
                print("price:%f" % price)
                print("buy4:%f" % buy4)
                print("buy10:%f" % buy10)
                if buy_id=="-1":
                    time.sleep(4)
                    break

                if counter>300:
                    last_buy_id = buy_id
                    api.cancel_order(market,buy_id)
                    time.sleep(1)
                    break
                if price>upper:
                    last_buy_id = buy_id
                    api.cancel_order(market,buy_id)
                    time.sleep(20)

                    break
                elif price<lower:
                    last_buy_id = buy_id
                    api.cancel_order(market, buy_id)

                    time.sleep(4)
                    break
                else:
                    counter+=0.2
                    time.sleep(0.2)

            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(10)
                continue


def sell_main_body():
    global access_key, access_secret, _money, _coin, market, partition,min_size, money_have, api,pending_orders,mutex2,total_filled_amount,mutex1,mutex3,bidirection,license_day,coin_place,total_amount_limit

    while True:
        try:
            counter=0
            # api.wait_pending_order(market)
            obj = api.get_depth(market)
            ask5 = obj["asks"][4*2]
            ask12 = obj["asks"][11 * 2]

            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            sell_id_1 = "-1"
            sell_id_2="-1"
            price1 = ask12
            price2 = ask5
            if (coin/2)>min_size:
                sell_id_1 = api.take_order(market, "sell", price1, coin/2,coin_place)
                sell_id_2 = api.take_order(market, "sell", price2, coin/2, coin_place)
            if sell_id_1=="-1" and sell_id_2=="-1":
                time.sleep(1)
                continue
            # api.balance_account("QC","USDT")
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(10)
            continue
        while True:
            try:
                print("counter:%d"%counter)
                obj = api.get_depth(market)
                ask5 = obj["asks"][4 * 2]
                ask15 = obj["asks"][14 * 2]
                ask4 = obj["asks"][3 * 2]
                ask11 = obj["asks"][10 * 2]
                ask10 = obj["asks"][9 * 2]


                if counter>300:
                    if sell_id_1!="-1":
                        api.cancel_order(market,sell_id_1)
                        time.sleep(0.5)
                    if sell_id_2 != "-1":
                        api.cancel_order(market, sell_id_2)
                    time.sleep(1)
                    break
                if price1>ask15 or price2>ask5:
                    if sell_id_1!="-1":
                        api.cancel_order(market,sell_id_1)
                        time.sleep(0.5)
                    if sell_id_2 != "-1":
                        api.cancel_order(market, sell_id_2)
                    time.sleep(2)

                    break
                elif price1<ask11 or price2<ask4:
                    if sell_id_1!="-1":
                        api.cancel_order(market,sell_id_1)
                        time.sleep(0.5)
                    if sell_id_2 != "-1":
                        api.cancel_order(market, sell_id_2)
                    time.sleep(10)
                    break
                else:
                    counter+=0.2
                    time.sleep(0.2)

            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(10)
                continue

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    partition=2
    money_have = 400
    _money = "tusd"
    _coin = "btc"

    bidirection=True
    coin_place="main"

    total_filled_amount=0
    api = fcoin_api(access_key, access_secret)
    # api.send_heart_beat()
    mutex2 = threading.Lock()
    mutex1 = threading.Lock()
    mutex3 = threading.Lock()
    pending_orders = list()


    market = _coin + _money
    api = fcoin_api(access_key, access_secret)
    min_size = 1 / pow(10, api.set_demical(_money, _coin))


    api.cancel_all_pending_order(market)

    money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
    time.sleep(0.5)
    obj = api.get_depth(market)
    buy1 = obj["bids"][0 * 2]
    total_amount_limit = coin+(money_have*partition)/buy1


    if bidirection==False:
        thread = threading.Thread(target=check_and_aggregate_orders, args=(api, market,))
        thread.start()
    else:
        thread = threading.Thread(target=sell_main_body)
        thread.start()

    for i in range(partition):
        type = i+1
        thread = threading.Thread(target=buy_main_body, args=(type,))
        thread.start()
        time.sleep(1)
