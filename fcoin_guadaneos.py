from fcoin_api import *
import copy
import threading



def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2,_money,_coin,mutex1,total_filled_amount
    while True:
        try:
            print("in aggregate")
            obj = api.get_depth(market)
            buy5 = obj["bids"][4 * 2]
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

            if len(buy_orders) >= 1:
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


            if len(sell_orders) >= 1:
                for i, item in enumerate(sell_orders):
                    amount = float(item["amount"]) - float(item["filled_amount"])
                    price = float(item["price"])
                    sell_money += amount * price
                    sell_amount += amount
                    api.cancel_order(market, item["id"])
                    time.sleep(0.5)
                local_total_amount = sell_amount

                new_sell_price = max(ask5,sell_money/sell_amount)
                time.sleep(1)
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
                id = api.take_order(market, "sell", new_sell_price, min(sell_amount,coin))
                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()
            mutex1.acquire()
            total_filled_amount = local_total_amount
            mutex1.release()
            time.sleep(20)
        except Exception as ex:
            print(sys.stderr, 'in check and aggrete: ', ex)
            continue

def main_body(type):
    global access_key, access_secret, _money, _coin, market, partition,min_size, money_have, api,pending_orders,mutex2,total_filled_amount,mutex1
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
            buy15 = obj["bids"][14* 2]
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            buy_id = "-1"
            if type == 1:
                price = buy10
            else:
                price = buy5
            filled_amount=0
            if last_buy_id!="-1":
                time.sleep(0.1)
                item = api.get_order_info(market,last_buy_id)
                last_buy_id = "-1"
                filled_amount = float(item['filled_amount'])
                last_price = float(item['price'])
                if filled_amount>min_size:
                    sell_order = api.take_order(market, "sell", last_price, size=min(filled_amount,coin))
                    if sell_order!="-1":
                        mutex2.acquire()
                        pending_orders.append(sell_order)
                        mutex2.release()
                    time.sleep(1)
            mutex1.acquire()
            local_total_filled_amount = total_filled_amount+filled_amount
            mutex1.release()
            print("coin can buy:%f"%(min(money_have,money)/ price))
            print("filled amount:%f"%(local_total_filled_amount/partition))
            if (min(money_have,money)/ price -local_total_filled_amount/partition) > min_size:
                buy_id = api.take_order(market, "buy", price, size=(min(money_have,money)/price-local_total_filled_amount/partition))
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
                time.sleep(0.3)
                print("counter:%d"%counter)
                obj = api.get_depth(market)
                buy7 = obj["bids"][6 * 2]
                buy15 = obj["bids"][14 * 2]
                buy4 = obj["bids"][3 * 2]
                buy10 = obj["bids"][9 * 2]
                if type==1:
                    upper = buy7
                    lower = buy15
                else:
                    upper = buy4
                    lower = buy10
                print("price:%f" % price)
                print("buy4:%f" % buy4)
                print("buy10:%f" % buy10)
                if buy_id=="-1":
                    time.sleep(4)
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
                    counter+=0.3

            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(10)
                continue

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    partition=2
    money_have = 400
    total_filled_amount=0
    api = fcoin_api(access_key, access_secret)
    # api.send_heart_beat()
    mutex2 = threading.Lock()
    mutex1 = threading.Lock()
    pending_orders = list()

    _money = "pax"
    _coin = "eos"
    market = _coin + _money
    api = fcoin_api(access_key, access_secret)
    min_size = 1 / pow(10, api.set_demical(_money, _coin))
    thread = threading.Thread(target=check_and_aggregate_orders, args=(api, market,))
    thread.start()

    thread = threading.Thread(target=main_body, args=(1,))
    thread.start()
    time.sleep(1)
    thread = threading.Thread(target=main_body, args=(2,))
    thread.start()


