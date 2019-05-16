from fcoin_api import *
import copy
import threading

_money = "pax"
_coin = "eos"

def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2
    while True:
        try:
            print("in aggregate")
            obj = api.get_depth(market)
            buy5 = obj["bids"][4 * 2]
            ask5 = obj["asks"][4 * 2]

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
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
                time.sleep(1)
                new_buy_price = buy5
                id = api.take_order(market, "buy", new_buy_price, min(buy_amount,money/new_buy_price)-0.0001)
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

                new_sell_price = ask5
                time.sleep(1)
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
                id = api.take_order(market, "sell", new_sell_price, min(sell_amount,coin)-0.0001)
                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()
            time.sleep(20)
        except Exception as ex:
            print(sys.stderr, 'in check and aggrete: ', ex)
            continue

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    market = "eospax"
    api = fcoin_api(access_key, access_secret)
    mutex2 = threading.Lock()
    pending_orders = list()

    coin_have = 205.95
    min_size = 0.1
   # api.send_heart_beat()

    thread = threading.Thread(target=check_and_aggregate_orders, args=(api, market,))
    thread.start()
    last_ask_id="-1"

    while True:
        try:
            counter=0
            # api.wait_pending_order(market)
            obj = api.get_depth(market)
            ask5 = obj["asks"][4*2]
            buy2 = obj["bids"][1 * 2]
            buy5 = obj["bids"][4*2]

            money, coin, freez_money, freez_coin = api.get_available_balance("pax", "eos")
            sell_id = "-1"
            price = ask5
            filled_amount = 0
            if last_ask_id!="-1":
                time.sleep(0.1)
                item = api.get_order_info(market,last_ask_id)
                last_ask_id="-1"
                filled_amount = float(item['filled_amount'])
                if filled_amount>0.001:
                    buy_order = api.take_order(market, "buy", buy5, size=min(filled_amount,money/buy5)-0.0001)
                    if buy_order!="-1":
                        mutex2.acquire()
                        pending_orders.append(buy_order)
                        mutex2.release()
                    time.sleep(1)
            if (min(coin_have,coin)-filled_amount - 0.0001) > min_size:
                sell_id = api.take_order(market, "sell", price, size=min(coin_have,coin)-filled_amount-0.0001)
            if sell_id=="-1":
                time.sleep(1)
                continue

            # api.balance_account("QC","USDT")

        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(10)
            continue
        while True:
            try:
                time.sleep(0.2)
                print("counter:%d"%counter)
                obj = api.get_depth(market)

                sell4 = obj["asks"][3 * 2]
                sell10 = obj["asks"][9*2]
                print("price:%f" % price)
                print("buy4:%f" % sell4)
                print("buy10:%f" % sell10)
                if sell_id == "-1":
                    time.sleep(1)
                    break
                if price<sell4:
                    api.cancel_order(market,sell_id)
                    last_ask_id = sell_id
                    time.sleep(20)
                    break
                elif price>sell10:
                    api.cancel_order(market,sell_id)
                    last_ask_id = sell_id
                    time.sleep(4)
                    break
                else:
                    counter+=0.2

            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                time.sleep(10)
                continue


