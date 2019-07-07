import rsa
from base64 import b64decode
import os
import uuid
import tkinter
from fcoin_api import *
import threading
import base64
from Crypto.Cipher import AES
from multiprocessing import Process
import multiprocessing

'''
采用AES对称加密算法
'''


# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes


# 加密方法
def encrypt_oracle(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return (encrypted_text)


# 解密方法
def decrypt_oralce(text):
    # 秘钥
    key = 'fhkgg'
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return (decrypted_text)


class Section:
    # 粘贴的回调函数
    def onPaste(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    def onPaste1(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show1.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    def onPaste2(self):
        try:
            self.text = win.clipboard_get()
            # 获得系统粘贴板内容
        except tkinter.TclError:
            pass
        # 防止因为粘贴板没有内容报错
        show2.set(str(self.text))
        # 在文本框中设置刚刚获得的内容

    # 复制的回调函数
    def onCopy(self):
        self.text = T.get(1.0, tkinter.END)
        # 获得文本框内容
        win.clipboard_append(self.text)
        # 添加至系统粘贴板


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def check_and_save():
    signature = entry1.get().strip().encode()
    # print("Signature")
    # print(signature)
    new_msg = msg1 + gap + "lyaegjdfuyeu"
    try:
        rsa.verify(new_msg.encode(), b64decode(signature), public)
    except:
        print("wrong license!!!")
        a = input("")
        sys.exit()
    with open(yanzheng_file_name, 'w') as f:
        f.write(encrypt_oracle(msg1 + ":::::" + signature.decode()))
        # f.write("\n")
        # f.write(encrypt_oracle(signature.decode()))
        # f.write(msg1+"\n")
        # f.write(signature.decode())
    win.destroy()


def buy_main_body(mutex2, api, expire_time, created_time, license_day, bidirection, partition, _money, _coin, min_size,
                  money_have, coin_place):
    market = _coin + _money
    local_created_time = created_time
    local_license_day = license_day

    while True:
        try:
            if (time.time()) > expire_time:
                print("expired!!!")
                return
            buy_id0 = "-1"
            buy_id1 = "-1"
            buy_id2 = "-1"
            buy_id3 = "-1"
            buy_id4 = "-1"
            sell_id_0 = "-1"
            sell_id_1 = "-1"
            sell_id_2 = "-1"
            sell_id_3 = "-1"
            sell_id_4 = "-1"
            mutex2.acquire()
            api.cancel_all_pending_order(market)
            counter = 0
            current_time = time.time()
            obj = api.get_depth(market)
            buy1 = obj["bids"][0 * 2]
            buy4 = obj["bids"][3 * 2]
            buy5 = obj["bids"][4 * 2]
            buy9 = obj["bids"][8 * 2]
            buy13 = obj["bids"][12 * 2]
            ask1 = obj["asks"][0 * 2]
            ask4 = obj["asks"][3 * 2]
            ask5 = obj["asks"][4 * 2]
            ask13 = obj["asks"][12 * 2]
            ask9 = obj["asks"][8 * 2]

            buy_id0 = api.take_order(market, "buy", buy1, min_size, coin_place)

            sell_id_0 = api.take_order(market, "sell", ask1, min_size, coin_place)
            money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)

            buy_price1 = buy5
            buy_price2 = buy13
            buy_price3 = buy4
            buy_price4 = buy9
            sell_price1 = ask5
            sell_price2 = ask13
            sell_price3 = ask4
            sell_price4 = ask9

            current_money_have = money_have - coin * buy1
            available_coin1_space = current_money_have / 2 / buy_price1
            available_coin2_space = current_money_have / 2 / buy_price2
            available_coin3_space = current_money_have / 2 / buy_price3
            available_coin4_space = current_money_have / 2 / buy_price4

            money1 = min(money_have, money) / 8
            money2 = min(money_have, money) / 8
            money3 = min(money_have, money) / 8
            money4 = min(money_have, money) / 8

            coin1_can_buy = money1 / buy_price1
            coin2_can_buy = money2 / buy_price2
            coin3_can_buy = money3 / buy_price3
            coin4_can_buy = money4 / buy_price4

            print("level 1 coin can buy:%f" % coin1_can_buy)
            print("level 2 coin can buy:%f" % coin2_can_buy)

            print("available_coin1_space:%f" % available_coin1_space)
            print("available_coin2_space:%f" % available_coin2_space)

            if available_coin1_space > min_size and coin1_can_buy > min_size:
                print("take buy order 1")
                buy_id1 = api.take_order(market, "buy", buy_price1,
                                         (min(available_coin1_space, coin1_can_buy)),
                                         coin_place)
            if available_coin2_space > min_size and coin2_can_buy > min_size:
                print("take buy order 2")
                buy_id2 = api.take_order(market, "buy", buy_price2,
                                         (min(available_coin2_space, coin2_can_buy)),
                                         coin_place)
            if available_coin3_space > min_size and coin3_can_buy > min_size:
                print("take buy order 3")
                buy_id3 = api.take_order(market, "buy", buy_price3,
                                         (min(available_coin1_space, coin3_can_buy)),
                                         coin_place)
            if available_coin4_space > min_size and coin4_can_buy > min_size:
                print("take buy order 4")
                buy_id4 = api.take_order(market, "buy", buy_price4,
                                         (min(available_coin2_space, coin4_can_buy)),
                                         coin_place)

            coin1_can_sell = coin / 8
            coin2_can_sell = coin / 8
            coin3_can_sell = coin / 8
            coin4_can_sell = coin / 8

            if coin1_can_sell > min_size:
                sell_id_1 = api.take_order(market, "sell", sell_price1, coin1_can_sell, coin_place)
            if coin2_can_sell > min_size:
                sell_id_2 = api.take_order(market, "sell", sell_price2, coin2_can_sell, coin_place)
            if coin3_can_sell > min_size:
                sell_id_3 = api.take_order(market, "sell", sell_price3, coin3_can_sell, coin_place)
            if coin4_can_sell > min_size:
                sell_id_4 = api.take_order(market, "sell", sell_price4, coin4_can_sell, coin_place)

            mutex2.release()

            # api.balance_account("QC","USDT")
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            try:
                mutex2.release()
            except:
                print("exception")

            continue
        interval = 0.1
        while True:
            try:
                time.sleep(2)
                current_time = time.time()
                obj = api.get_depth(market)
                buy1 = obj["bids"][0 * 2]
                buy4 = obj["bids"][3 * 2]
                buy5 = obj["bids"][4 * 2]
                buy9 = obj["bids"][8 * 2]
                buy13 = obj["bids"][12 * 2]
                ask1 = obj["asks"][0 * 2]
                ask4 = obj["asks"][3 * 2]
                ask5 = obj["asks"][4 * 2]
                ask13 = obj["asks"][12 * 2]
                ask9 = obj["asks"][8 * 2]

                tmp = api.take_order(market, "buy", buy1, min_size, coin_place)
                api.cancel_order(market, buy_id0)
                buy_id0 = tmp

                tmp = api.take_order(market, "sell", ask1, min_size, coin_place)
                api.cancel_order(market, sell_id_0)
                sell_id_0 = tmp
                time.sleep(interval)
                money, coin, freez_money, freez_coin = api.get_available_balance(_money, _coin)

                buy_price1 = buy5
                buy_price2 = buy13
                buy_price3 = buy4
                buy_price4 = buy9
                sell_price1 = ask5
                sell_price2 = ask13
                sell_price3 = ask4
                sell_price4 = ask9

                current_money_have = money_have - coin * buy1
                available_coin1_space = current_money_have / 2 / buy_price1
                available_coin2_space = current_money_have / 2 / buy_price2
                available_coin3_space = current_money_have / 2 / buy_price3
                available_coin4_space = current_money_have / 2 / buy_price4

                money1 = min(money_have, money) / 4
                money2 = min(money_have, money) / 4
                money3 = min(money_have, money) / 4
                money4 = min(money_have, money) / 4

                coin1_can_buy = money1 / buy_price1
                coin2_can_buy = money2 / buy_price2
                coin3_can_buy = money3 / buy_price3
                coin4_can_buy = money4 / buy_price4

                print("trade pair:%s" % market)

                if available_coin1_space > min_size and coin1_can_buy > min_size:
                    # print("take buy order 1")
                    time.sleep(interval)
                    tmp = api.take_order(market, "buy", buy_price1,
                                         (min(available_coin1_space, coin1_can_buy)),
                                         coin_place)
                    api.cancel_order(market, buy_id1)
                    buy_id1 = tmp
                if available_coin2_space > min_size and coin2_can_buy > min_size:
                    # print("take buy order 2")
                    time.sleep(interval)
                    tmp = api.take_order(market, "buy", buy_price2,
                                         (min(available_coin2_space, coin2_can_buy)),
                                         coin_place)
                    api.cancel_order(market, buy_id2)
                    buy_id2 = tmp
                if available_coin3_space > min_size and coin3_can_buy > min_size:
                    # print("take buy order 2")
                    time.sleep(interval)
                    tmp = api.take_order(market, "buy", buy_price3,
                                         (min(available_coin3_space, coin3_can_buy)),
                                         coin_place)
                    api.cancel_order(market, buy_id3)
                    buy_id3 = tmp

                if available_coin4_space > min_size and coin4_can_buy > min_size:
                    # print("take buy order 2")
                    time.sleep(interval)
                    tmp = api.take_order(market, "buy", buy_price4,
                                         (min(available_coin4_space, coin4_can_buy)),
                                         coin_place)
                    api.cancel_order(market, buy_id4)
                    buy_id4 = tmp

                coin1_can_sell = coin / 4
                coin2_can_sell = coin / 4
                coin3_can_sell = coin / 4
                coin4_can_sell = coin / 4

                if coin1_can_sell > min_size:
                    time.sleep(interval)
                    tmp = api.take_order(market, "sell", sell_price1, coin1_can_sell, coin_place)
                    api.cancel_order(market, sell_id_1)
                    sell_id_1 = tmp
                if coin2_can_sell > min_size:
                    time.sleep(interval)
                    tmp = api.take_order(market, "sell", sell_price2, coin2_can_sell, coin_place)
                    api.cancel_order(market, sell_id_2)
                    sell_id_2 = tmp

                if coin3_can_sell > min_size:
                    time.sleep(interval)
                    tmp = api.take_order(market, "sell", sell_price3, coin3_can_sell, coin_place)
                    api.cancel_order(market, sell_id_3)
                    sell_id_3 = tmp
                if coin4_can_sell > min_size:
                    time.sleep(interval)
                    tmp = api.take_order(market, "sell", sell_price4, coin4_can_sell, coin_place)
                    api.cancel_order(market, sell_id_4)
                    sell_id_4 = tmp
                counter += time.time() - current_time
                print("counter:%d" % counter)
                if counter > 300:
                    break


            except Exception as ex:
                print(sys.stderr, 'zb request ex: ', ex)
                break


def load_record():
    global load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place
    with open(config_file, 'r') as f:
        tmp = f.read()
        tmp = decrypt_oralce(tmp)
        parameters = tmp.split(gap)
        load_access_key = parameters[0]
        load_access_secret = parameters[1]
        load_money = parameters[2]
        load_coin = parameters[3]
        load_parition = parameters[4]
        load_total_money = parameters[5]
        load_bidirection = parameters[6]
        load_coin_place = parameters[7]


def tick(load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection,
         load_coin_place, created_time, license_day, expire_time):
    try:
        mutex2 = threading.Lock()
        access_key = load_access_key.strip()
        access_secret = load_access_secret.strip()
        _money = load_money.strip().lower()
        tmp = load_coin.strip().lower()
        if " " in tmp:
            coins = tmp.split(" ")
        else:
            coins = [tmp]
        markets = [_coin + _money for _coin in coins]
        print(markets)
        partition = int(load_parition.strip())
        assert (partition != 0)
        money_have = float(load_total_money.strip())

        market_exchange_dict = {"bbgcusdt": "renren", "btmusdt": "jingxuanremenbi", "zipusdt": "servicex",
                                "fiusdt": "fiofficial", "dogeusdt": "tudamu", "aeusdt": "servicex", "zrxusdt": "tudamu",
                                "batusdt": "jiucai", "linkusdt": "jingxuanremenbi", "icxusdt": "allin",
                                "omgusdt": "ninthzone", "zilusdt": "langchao"}

        bidirection = int(load_bidirection.strip())
        coin_place_list = [market_exchange_dict.get(item, "main") for item in markets]

        api = fcoin_api(access_key, access_secret)
        min_size = api.set_demical(_money, coins)
        print("start cancel existing pending orders")
        for market in markets:
            time.sleep(0.1)
            api.cancel_all_pending_order(market)
        print("cancel pending orders completed")
        for i, market in enumerate(markets):
            time.sleep(0.1)
            thread = threading.Thread(target=buy_main_body, args=(
            mutex2, api, expire_time, created_time, license_day, bidirection, partition, _money, coins[i],
            min_size[market], money_have / len(markets), coin_place_list[i]))
            thread.setDaemon(True)
            thread.start()
        time.sleep(3600)
        print("tick exit!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    except Exception as ex:
        print(sys.stderr, 'tick: ', ex)
        # a= input()


def save_record():
    global global_config, load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place

    load_access_key = save_access_key = entry1.get().strip()
    load_access_secret = save_access_secret = entry2.get().strip()
    load_money = save__money = entry4.get().strip().lower()
    load_coin = save__coin = entry5.get().strip().lower()
    load_parition = save_parition = entry6.get().strip()
    load_total_money = save_total_money = (entry7.get().strip())
    load_bidirection = save_bidirection = (entry8.get().strip())
    load_coin_place = save_coin_place = (entry9.get().strip())

    tmp = save_access_key + gap + save_access_secret + gap + save__money + gap + save__coin + gap + save_parition + gap + save_total_money + gap + save_bidirection + gap + save_coin_place
    global_config = encrypt_oracle(tmp)

    win.destroy()


def delete_record():
    if os.path.exists(config_file):
        os.remove(config_file)


def is_need_record():
    label1 = tkinter.Label(win, text="是否记住本次配置便于下次重启或多开？:")
    label1.pack()
    button1 = tkinter.Button(win, text="是", command=save_record)  # 收到消息执行这个函数
    button1.pack()  # 加载到窗体，
    button2 = tkinter.Button(win, text="否", command=delete_record)  # 收到消息执行这个函数
    button2.pack()  # 加载到窗体，


def get_license_day():
    global license_day
    license_day = float(entryday.get().strip())
    # license_day  = 0.00069
    win.destroy()


# 导入密钥

if __name__ == '__main__':
    multiprocessing.freeze_support()

    print("begin")

    load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection, load_coin_place = None, None, None, None, None, None, None, None
    win1 = None
    license_day = 0
    emerency = False

    mutex1 = threading.Lock()
    mutex3 = threading.Lock()
    mutex4 = threading.Lock()
    mutex5 = threading.Lock()

    access_key = None
    access_secret = None

    _money = None
    coins = None
    min_size = None
    money_have = None

    api = None
    partition = 0
    bidirection = 3
    coin_place = "main"
    total_amount_limit = 0
    yanzheng_file_name = "multi_coin_yanzheng.txt"
    gap = "multicoin"
    config_file = "multi_coinlastconfig.txt"

    need_exit = False
    coins = list()
    coin_place_list = list()
    markets = list()

    pem = '''-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAKw+pVBfpmDwg2hQj6aShNlaprI/6cSv994XaFsk2I5h7ysvvXrOhZTm
unpk2/1AjV2ieh7wxw96QeiVVrvriLEz1lzZYBPT1yCU7mOcg5RiQQZqAzN9Tqvc
aKuWxd6Dzm5IWK4kxpUwgKTC8En4h5YPiM+QcjkJIVBBX1R7NyDRAgMBAAE=
-----END RSA PUBLIC KEY-----
'''
    public = rsa.PublicKey.load_pkcs1(pem)

    if os.path.exists(yanzheng_file_name):
        try:
            with open(yanzheng_file_name, 'r') as f:
                txt = f.read()
                decrypt_txt = decrypt_oralce(txt.strip())
                msg1 = decrypt_txt.split(":::::")[0]
                machine_code_from_txt = msg1.split(gap)[0]
                real_machine_code = get_mac_address()
                assert (machine_code_from_txt == real_machine_code)
                # print("msg1")
                # print(msg1)
                signature = decrypt_txt.split(":::::")[1]
                # print("Signature")
                # print(signature)
                new_msg = msg1 + gap + "lyaegjdfuyeu"
                verify = rsa.verify(new_msg.encode(), b64decode(signature), public)
        except:
            print("wrong license!!!")
            os.remove(yanzheng_file_name)
            # a = input("")
            sys.exit()

        created_time = int(msg1.split(gap)[1])
        time_now = int(time.time())
        time_spend = time_now - created_time
        license_day = float(msg1.split(gap)[2])

        print("license type:%f day" % license_day)
        licensed_time = 3600 * 24 * license_day
        if (time_spend > licensed_time):
            print("license expired!!!")
            os.remove(yanzheng_file_name)
            a = input("")
            sys.exit()


    else:
        win = tkinter.Tk()
        win.title("注册")
        label = tkinter.Label(win, text="请输入激活天数：")
        label.pack()
        entryday = tkinter.Entry(win, width=50, bg="white", fg="black")
        entryday.pack()

        button = tkinter.Button(win, text="确定", command=get_license_day)  # 收到消息执行这个函数
        button.pack()  # 加载到窗体，
        win.mainloop()



        _time = int(time.time())
        machine_code = get_mac_address()
        msg1 = machine_code + gap + str(_time) + gap + str(license_day)
        # print(msg1)
        win = tkinter.Tk()
        win.title("注册")
        label = tkinter.Label(win, text="请把该代码输入进付款软件:")
        label.pack()
        T = tkinter.Text(win, height=1, width=33)
        T.pack()
        T.insert(tkinter.END, msg1)
        labe2 = tkinter.Label(win, text="请在下方输入付款软件提供的注册码:")
        labe2.pack()
        show = tkinter.StringVar()
        entry1 = tkinter.Entry(win, textvariable=show, width=50, bg="white", fg="black")
        entry1.pack()
        button = tkinter.Button(win, text="确定", command=check_and_save)  # 收到消息执行这个函数
        button.pack()  # 加载到窗体，

        section = Section()
        # 实例化刚刚写的类

        menu = tkinter.Menu(win, tearoff=0)
        # tearoff设置成0就不会有开头的虚线，也不会让你的菜单可以单独成为窗口，可以自己试验一下

        menu.add_command(label="复制", command=section.onCopy)


        def popupmenu(event):
            menu.post(event.x_root, event.y_root)


        # 添加三个按钮，command设置回调函数
        T.bind("<Button-3>", popupmenu)
        menu0 = tkinter.Menu(win, tearoff=0)
        menu0.add_command(label="粘贴", command=section.onPaste)


        def popupmenu0(event):
            menu0.post(event.x_root, event.y_root)


        entry1.bind("<Button-3>", popupmenu0)
        win.mainloop()
    try:
        with open(yanzheng_file_name, 'r') as f:
            txt = f.read()
            decrypt_txt = decrypt_oralce(txt.strip())
            msg1 = decrypt_txt.split(":::::")[0]
            machine_code_from_txt = msg1.split(gap)[0]
            real_machine_code = get_mac_address()
            assert (machine_code_from_txt == real_machine_code)
            # print("msg1")
            # print(msg1)
            signature = decrypt_txt.split(":::::")[1]
            # print("Signature")
            # print(signature)
            new_msg = msg1 + gap + "lyaegjdfuyeu"
            verify = rsa.verify(new_msg.encode(), b64decode(signature), public)
    except:
        print("wrong license!!!")
        os.remove(yanzheng_file_name)
        a = input("")
        sys.exit()

    created_time = int(msg1.split(gap)[1])
    time_now = int(time.time())
    time_spend = time_now - created_time
    license_day = float(msg1.split(gap)[2])
    print("license type:%f day" % license_day)
    licensed_time = 3600 * 24 * license_day
    expired_time = created_time + licensed_time

    if (time_now > expired_time):
        print("license expired!!!")
        a = input("")
        sys.exit()
    '''
    expired_time=1562834709
    created_time=0
    license_day=0
    print(time.time())

    if (time.time() > expired_time):
        print("license expired!!!")
        a = input("")
        sys.exit()
    '''
    has_record = False
    if os.path.exists(config_file):
        has_record = True
        load_record()

    win = tkinter.Tk()
    win.title("币选小资金挖矿")
    label = tkinter.Label(win, text="请在下面输入框输入您的API key:")
    label.pack()
    if has_record:
        show1 = tkinter.StringVar(value=load_access_key)
    else:
        show1 = tkinter.StringVar()
    entry1 = tkinter.Entry(win, textvariable=show1, width=50, show="*", bg="white", fg="black")

    entry1.pack()
    section = Section()
    menu1 = tkinter.Menu(win, tearoff=0)
    menu1.add_command(label="粘贴", command=section.onPaste1)


    def popupmenu1(event):
        menu1.post(event.x_root, event.y_root)


    entry1.bind("<Button-3>", popupmenu1)

    label = tkinter.Label(win, text="请在下面输入框输入您的API secret:")
    label.pack()

    if has_record:
        show2 = tkinter.StringVar(value=load_access_secret)
    else:
        show2 = tkinter.StringVar()

    entry2 = tkinter.Entry(win, textvariable=show2, width=50, show="*", bg="white", fg="black")
    entry2.pack()

    menu2 = tkinter.Menu(win, tearoff=0)
    menu2.add_command(label="粘贴", command=section.onPaste2)


    def popupmenu2(event):
        menu2.post(event.x_root, event.y_root)


    entry2.bind("<Button-3>", popupmenu2)

    label = tkinter.Label(win, text="使用前请把USDT放入交易账户，此软件会自动选择多个交易对挂单，并且只会使用总额最多100USDT,请不要放入过多的USDT在账户：")
    # label.pack()
    entry4 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry4.insert(tkinter.END, load_money)
    # entry4.pack()

    label = tkinter.Label(win, text="请输入虚拟货币种类(可以输入多个货币，中间用1个空格隔开。如etc btc eos)：")
    # label.pack()
    entry5 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry5.insert(tkinter.END, load_coin)

    # entry5.pack()

    label = tkinter.Label(win, text="请输入挂单类型（1 或 2）1.只挂6-15档（矿损少，收益少一点）, 2.同时挂2-5档和6-15档（收益大，矿损大一点）：")
    # label.pack()
    entry6 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry6.insert(tkinter.END, load_parition)

    # entry6.pack()

    label = tkinter.Label(win, text="请输入刷单金额(单位：usdt)：")
    label.pack()
    entry7 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry7.insert(tkinter.END, load_total_money)
    entry7.pack()

    label = tkinter.Label(win, text="请选择挂单方向（1,2或3）1.只挂买单 2.只挂卖单 3.双向挂单")
    # label.pack()
    entry8 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry8.insert(tkinter.END, load_bidirection)
    #   entry8.pack()

    label = tkinter.Label(win, text="请输入交易区（1 或 2）1.主板,2.Fone：")
    # label.pack()
    entry9 = tkinter.Entry(win, width=50, bg="white", fg="black")
    if has_record:
        entry9.insert(tkinter.END, load_coin_place)
    #  entry9.pack()

    button = tkinter.Button(win, text="确定", command=save_record)  # 收到消息执行这个函数
    button.pack()  # 加载到窗体，
    win.mainloop()

    load_money = "usdt"
    load_coin = "eos etc ltc bch trx eth xrp ft xlm zec ada dash bsv iota btc"
    load_parition = "2"
    # load_total_money="100"
    load_bidirection = "3"
    load_coin_place = "1"
    while True:
        p1 = Process(target=tick, args=(
        load_access_key, load_access_secret, load_money, load_coin, load_parition, load_total_money, load_bidirection,
        load_coin_place, created_time, license_day, expired_time))
        p1.daemon = True
        p1.start()
        p1.join(timeout=3600)
        print("terminate")
        p1.terminate()
        print("main exit")

#  period_restart()









