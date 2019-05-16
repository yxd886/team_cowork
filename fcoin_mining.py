from fcoin_api import *
import threading
import copy

trade_time=0
pending_orders=list()


def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2
    counter=0
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
            counter+=20
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


    while True:
        try:
            time.sleep(5)
            jump = True
            if sell_complete or api.is_order_complete(market, sell_id):
                if not sell_complete:
                    sell_complete=True
                    mutex2.acquire()
                    if sell_id in pending_orders:
                        pending_orders.remove(sell_id)
                    mutex2.release()
            else:
                jump=False
            if buy_comlete or api.is_order_complete(market, buy_id):
                if not buy_comlete:
                    buy_comlete=True
                    mutex2.acquire()
                    if buy_id in pending_orders:
                        pending_orders.remove(buy_id)
                    mutex2.release()
            else:
                jump=False
            if jump:
                mutex1.acquire()
                trade_time += 2
                mutex1.release()
                break
        except Exception as ex:
            print(sys.stderr, 'record ex: ', ex)
            continue


if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    _coin="eos"
    _money = "usdt"
    market = _coin+_money

    api = fcoin_api(access_key, access_secret)
    mutex1 = threading.Lock()
    mutex2 = threading.Lock()
    process_time=0
   # api.send_heart_beat()
    thread = threading.Thread(target=check_and_aggregate_orders, args=(api, market,))
    thread.start()

    while True:
        try:
            time.sleep(2)
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            size = 2
            buy, ask = api.get_buy1_and_sell_one(market)
            price = (ask+buy)/2
            real_size = min(size,money/price,coin)
            if price-buy>=0.0001 and ask-price>=0.0001 and real_size>0.01:
                sell_id = api.take_order(market,"sell",price,real_size)
                buy_id = api.take_order(market,"buy",price,real_size)
                process_time+=2
                print("-----------------------------------------------------------------")
                print("process_time:%d"%process_time)
                mutex1.acquire()
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)
                print("chance coming!!!")
            else:
                print("-----------------------------------------------------------------")
                print("process_time:%d" % process_time)
                mutex1.acquire()
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)
                print("no chance!")
                continue



            thread=threading.Thread(target=record, args=(api,market,sell_id,buy_id,))
            thread.start()




        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(5)

            continue
