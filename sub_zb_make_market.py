from zb_api import *

import threading
import copy

trade_time=0
pending_orders=list()
future_list=list()


def check_and_aggregate_orders(api, market):
    global  pending_orders, mutex2
    while True:
        try:
            time.sleep(1)
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
                time.sleep(2)
                item = api.get_order_info(market,id)
                if  "message" in item.keys() or str(item['status'])=="1" or str(item["status"])=="2":
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
                if str(item["type"])=="1":
                    buy_orders.append(item)
                elif str(item["type"]) =="0":
                    sell_orders.append(item)


            print("buy_order_num:%d" % len(buy_orders))
            print("sell_order_num:%d" % len(sell_orders))

            if len(buy_orders) > 1:
                for i, item in enumerate(buy_orders):
                    time.sleep(1)
                    amount = float(item["total_amount"]) - float(item["trade_amount"])
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
                    time.sleep(1)
                    amount = float(item["total_amount"]) - float(item["trade_amount"])
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
            time.sleep(1)
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

def future_process(api):
    global future_list,mutex3,pending_orders,mutex2
    while True:
        try:
            time.sleep(5)
            item=None
            mutex3.acquire()
            length = len(future_list)
            if length:
                item = future_list[0]
            mutex3.release()
            if(length==0):
                continue
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            market = item[0]
            direction=item[1]
            price = item[2]
            size = item[3]
            id="-1"
            if direction=="buy":
                if money>size*price:
                    id = api.take_order(market,direction,price,size)
            else:
                if coin>size:
                    id = api.take_order(market, direction, price, size)
            if id!="-1":
                mutex3.acquire()
                future_list.remove(item)
                mutex3.release()
                mutex2.acquire()
                pending_orders.append(id)
                mutex2.release()



        except Exception as ex:
            print(sys.stderr, 'future_process exception: ', ex)
            continue




if __name__ == '__main__':
    access_key = 'c9a579cf-5e0a-4f01-abd2-386cc127a4ad'
    access_secret = 'de38de17-aabb-4d33-a687-5677d0de0a53'

    access_key1 = "ba635b76-22f1-440e-a61d-1b447590d5e2"
    access_secret1 = "88ed80ea-6ca6-4c28-a3f5-97fb8e630b0e"


    access_key2="25c459f8-07a5-475c-949a-440958ec3722"
    access_secret2="1dec655b-aea0-40c9-aff7-f6a86316bbf9"

    access_key3="0df41cfc-953a-44f8-995a-0260fabaee8f"
    access_secret3="0165c1e0-6352-435c-b04a-d38625bf5cc0"

    market = "USDT_QC"
    api = zb_api(access_key, access_secret)
    api1=zb_api(access_key1,access_secret1) #for pending
    api2 = zb_api(access_key2,access_secret2) #for record
    api3 = zb_api(access_key3,access_secret3) #for future process
    _coin = "USDT"
    _money = "QC"
    market = _coin +"_"+ _money
    mutex1 = threading.Lock()
    mutex2 = threading.Lock()
    mutex3 = threading.Lock()
    process_time = 0
    # api.send_heart_beat()
    thread1 = threading.Thread(target=check_and_aggregate_orders, args=(api1, market,))
    thread1.start()
    thread2 = threading.Thread(target=future_process, args=(api3,))
    thread2.start()

    while True:
        try:
            time.sleep(2)
            sell_id="-1"
            buy_id="-1"
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)
            size = 5
            buy, ask = api.get_buy1_and_sell_one(market)
            if money<buy*size and coin<size:
                print("-----------------------------------------------------------------")
                print("process_time:%d" % process_time)
                mutex1.acquire()
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)
                print("no money and coin!")
                continue
            elif money>=buy*size and coin>=size:
                sell_id = api.take_order(market, "sell", ask, size)
                buy_id = api.take_order(market, "buy", buy, size)
                process_time += 2
                print("-----------------------------------------------------------------")
                print("process_time:%d" % process_time)
                mutex1.acquire()
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)

                thread = threading.Thread(target=record, args=(api2, market, sell_id, buy_id,))
                thread.start()
            elif money<buy*size and coin>=size:# can sell but not buy
                sell_id = api.take_order(market, "sell", ask, size)
                process_time += 2
                print("-----------------------------------------------------------------")
                print("process_time:%d" % process_time)
                mutex1.acquire()
                trade_time += 2
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)
                print("only sell")
                mutex3.acquire()
                future_list.append((market, "buy", buy, size))
                mutex3.release()
            elif money>=buy*size and coin<size: #can buy but not sell
                buy = api.take_order(market, "buy", buy, size)
                process_time += 2
                print("-----------------------------------------------------------------")
                print("process_time:%d" % process_time)
                mutex1.acquire()
                trade_time += 2
                print("trade_time:%d" % trade_time)
                mutex1.release()
                print("sell price:%f" % ask)
                print(" buy price:%f" % buy)
                print("only buy")
                mutex3.acquire()
                future_list.append((market, "sell", ask, size))
                mutex3.release()

        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            time.sleep(5)
            continue

        while True:
            try:
                buy, ask = api.get_buy1_and_sell_one(market)
                print("current_sell:%f" % ask)
                print("current_buy :%f" % buy)
                print("process_time:%d" % process_time)
                mutex1.acquire()
                print("trade_time:%d" % trade_time)
                mutex1.release()
                if sell_id == "-1" and buy_id == "-1":
                    break
                if sell_id != "-1" and api.is_order_complete(market, sell_id):  # order success
                    print("sell order complete")
                    break
                if buy_id != "-1" and api.is_order_complete(market, buy_id):  # order success
                    print("buy order complete")
                    break
                print("order not complete")
                time.sleep(5)

            except Exception as ex:
                print(sys.stderr, 'second_exception: ', ex)
                time.sleep(5)
                continue


