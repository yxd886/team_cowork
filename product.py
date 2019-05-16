from fcoin_api import *
import tkinter
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


def tick():
    access_key = entry1.get()
    access_key = access_key.strip()
    access_secret = entry2.get()
    access_secret = access_secret.strip()

    _money =entry4.get()
    _money = _money.strip()
    _coin = entry5.get()
    _coin = _coin.strip()
    market = _coin+_money
    api = fcoin_api(access_key, access_secret)

    upper_price = float(entry6.get())

    lower_price = float(entry7.get())
    middle_price = (upper_price+lower_price)/2
    cell_num = int(entry8.get())
    total_coin = float(entry9.get())


    print(access_key)
    print(access_secret)
    print(_money)
    print(_coin)
    print(upper_price)
    print(lower_price)
    print(cell_num)
    print(total_coin)

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


    print("目前拥有币数:%f" % current_coin_have)
    print("可使用资金:%f"%money)
    print("冻结资金:%f" % freez_money)

    coin_should_have = api.compute_current_num_of_coin_should_have(upper_price=upper_price, lower_price=lower_price,
                                                                   cell_num=cell_num, current_price=buy)
    print("目前应该持有的币数:%f"%coin_should_have)
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
                print("设置买单!!!")
            if coin > current_coin_step_for_sell:
                if sell_price<ask:
                    sell_trade_price = ask
                else:
                    sell_trade_price=sell_price
                sell_order_id = api.take_order(market, "sell", sell_trade_price,
                                         size=current_coin_step_for_sell)
                print("设置卖单!!!")

            time_now = int(time.time())
            time_local = time.localtime(time_now)
            dt = time.strftime("--------------------%Y-%m-%d %H:%M:%S------------------------", time_local)
            print(dt)
            current_coin_have = coin + freez_coin
            print("目前拥有的币数:%f" % current_coin_have)
            print("可用资金:%f" % money)
            print("冻结资金:%f" % freez_money)

            profit = money+freez_money+(coin+freez_coin)*buy-money_have

            print("当前卖一价:%f" % ask)
            print("当前买一价 :%f"%buy)

            print("交易次数:%d"%trade_time)
        except Exception as ex:
            print(sys.stderr, 'First_exception: ', ex)
            continue
            time.sleep(5)
        time.sleep(1)
        while True:
            try:


                buy, ask = api.get_buy1_and_sell_one(market)
                profit = money + freez_money + (coin + freez_coin) * buy - money_have

                print("当前卖一价:%f" % ask)
                print("当前买一价 :%f" % buy)

                print("交易次数:%d" % trade_time)


                if sell_order_id == "-1" and buy_order_id=="-1":
                    break
                if sell_order_id != "-1" and api.is_order_complete(market, sell_order_id):# order success
                    trade_time+=1
                    print("卖单完成")
                    api.cancel_order(market,buy_order_id)
                    buy_price=sell_trade_price-step
                    sell_price=sell_trade_price+step
                    break
                if buy_order_id!="-1" and api.is_order_complete(market, buy_order_id):# order success
                    trade_time+=1
                    print("买单完成")
                    api.cancel_order(market,sell_order_id)
                    buy_price=buy_trade_price-step
                    sell_price=buy_trade_price+step
                    break

                time.sleep(5)

            except Exception as ex:
                print(sys.stderr, 'second_exception: ', ex)
                time.sleep(5)
                continue


if __name__ == '__main__':

    win = tkinter.Tk()
    label = tkinter.Label(win, text="请在下面输入框输入您的API key:")
    label.pack()
    entry1 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry1.pack()

    label = tkinter.Label(win, text="请在下面输入框输入您的API secret:")
    label.pack()
    entry2 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry2.pack()


    #label = tkinter.Label(win, text="请输入交易所代码:(ZB:1, Fcoin:2)")
    #label.pack()
    #entry3 = tkinter.Entry(win, width=50, bg="white", fg="black")
    #entry3.pack()


    label = tkinter.Label(win, text="请输入现金种类：")
    label.pack()
    entry4 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry4.pack()

    label = tkinter.Label(win, text="请输入虚拟货币种类：")
    label.pack()
    entry5 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry5.pack()


    label = tkinter.Label(win, text="请输入网格最高价：")
    label.pack()
    entry6 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry6.pack()

    label = tkinter.Label(win, text="请输入网格最低价：")
    label.pack()
    entry7 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry7.pack()

    label = tkinter.Label(win, text="请输入网格数目：")
    label.pack()
    entry8 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry8.pack()


    label = tkinter.Label(win, text="请输入投入总币量（将总金额换算成总币数）：")
    label.pack()
    entry9 = tkinter.Entry(win, width=50, bg="white", fg="black")
    entry9.pack()

    button = tkinter.Button(win, text="确定", command=tick)  # 收到消息执行这个函数
    button.pack()  # 加载到窗体，
    win.mainloop()

