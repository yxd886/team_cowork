from zb_api import *

import threading
import copy

trade_time=0
pending_orders=list()


def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2
    while True:
        try:
            print("in aggregate")
            buy_orders = list()
            buy_money = 0
            buy_amount = 0
            sell_money = 0
            sell_amount = 0
            sell_orders = list()
            local1_pend_order = list()
            local_pending_order = list()
            mutex2.acquire()
            local1_pend_order = copy.deepcopy(pending_orders)
            print("pending order length:%d"%len(pending_orders))
            need_remove_list = list()
            mutex2.release()

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

            if len(buy_orders) > 1:
                for i, item in enumerate(buy_orders):
                    amount = float(item["amount"]) - float(item["filled_amount"])
                    price = float(item["price"])
                    buy_money += amount * price
                    buy_amount += amount
                    api.cancel_order(market, item["id"])
                    time.sleep(0.5)

                new_buy_price = buy_money / buy_amount-0.0001
                id = api.take_order(market, "buy", new_buy_price, buy_amount)
                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()


            if len(sell_orders) > 1:
                for i, item in enumerate(sell_orders):
                    amount = float(item["amount"]) - float(item["filled_amount"])
                    price = float(item["price"])
                    sell_money += amount * price
                    sell_amount += amount
                    api.cancel_order(market, item["id"])
                    time.sleep(0.5)

                new_sell_price = sell_money / sell_amount+0.0001
                id = api.take_order(market, "sell", new_sell_price, sell_amount)
                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()
            time.sleep(20)
        except Exception as ex:
            print(sys.stderr, 'in check and aggrete: ', ex)
            continue


def record(api,market,sell_id,buy_id):
    global trade_time,pending_orders,mutex1,mutex2
    mutex2.acquire()
    pending_orders.append(sell_id)
    pending_orders.append(buy_id)
    mutex2.release()
    sell_complete=False
    buy_comlete=False



if __name__ == '__main__':
    access_key = 'c9a579cf-5e0a-4f01-abd2-386cc127a4ad'
    access_secret = 'de38de17-aabb-4d33-a687-5677d0de0a53'
    market = "USDT_QC"
    api = zb_api(access_key, access_secret)
    size = 20
    # api.wait_pending_order(market)
    buy, ask = api.get_buy1_and_sell_one(market)
    money, coin, freez_money, freez_coin = api.get_available_balance("QC","USDT")
    profit = 0
    money_today = money + freez_money
    coin_today = coin + freez_coin

    lowest = 6.66
    higest = 7.05

    money_have = money + freez_money + (coin + freez_coin) * buy

    # api.balance_account("QC","USDT")



    while True:
        try:
            time.sleep(1)
            api.handle_order_in_queue(market)
            buy, ask = api.get_buy1_and_sell_one(market)
            money, coin, freez_money, freez_coin = api.get_available_balance("QC", "USDT")
            ratio = (money + freez_money) / (money + freez_money + (coin + freez_coin) * buy)
            if ratio<0.25:
                api.check_and_aggregate_orders(market)
            profit = money + freez_money + (coin + freez_coin) * buy - money_have
            print("!!!PROFIT:%f" % profit)
            print("!!!PROFIT: coin:%f,money:%f" % (coin + freez_coin - coin_today, money + freez_money - money_today))

            upper = ask
            lower = buy
            sell_id = "-1"
            buy_id = "-1"

            if upper > lowest and lower < higest:
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
            elif upper <= lowest:
                buy_id = api.take_order(market, "buy", upper, size=size)
                time.sleep(1)
                continue
            elif lower >= higest:
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
                print("!!!PROFIT:%f,price for this step:%f" % (profit, buy))
                print(
                    "!!!PROFIT: coin:%f,money:%f" % (coin + freez_coin - coin_today, money + freez_money - money_today))
                if sell_id == "-1" and buy_id == "-1":
                    break
                if sell_id != "-1":
                    if api.is_order_complete(market, sell_id):
                        break
                    elif counter > 10 and buy_id == "-1":
                        api.cancel_order(market, sell_id)
                        api.dequeue_current_buy_order()
                        break
                    time.sleep(1)
                if buy_id != "-1":
                    if api.is_order_complete(market, buy_id):
                        break
                    elif counter > 10 and sell_id == "-1":
                        api.cancel_order(market, buy_id)
                        api.dequeue_current_sell_order()
                        break
            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(5)
                continue

