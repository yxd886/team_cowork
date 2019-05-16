__author__ = 'Ziyang'
from zb_api import  *
import os
import pickle

if __name__ == '__main__':
    access_key = '16e04c69-2d0d-4f1d-8304-55983930c485'
    access_secret = '435a1a5a-986a-4d0a-8168-507a707e1237'
    market = "USDT_QC"
    time_list = list()
    balance_list = list()
    profit_list = list()
    price_list = list()

    fig_path = "figures/new_new_sub_account3.png"
    file_name = "pkls/new_new_sub_account3.pkl"
    api = zb_api(access_key, access_secret)

    if os.path.exists(file_name):
        with open(file_name,"rb") as fh:
            _dict=pickle.load(fh)
            balance_list=_dict["balance"]
            time_list = _dict["time"]
            price_list = _dict["price"]

        for i in range(len(balance_list)):
            profit_list.append(balance_list[i]-balance_list[0])


    while True:
        try:
            time_now = int(time.time())
            time_local = time.localtime(time_now)

            dt = (time.strftime("%m/%d-%H:%M:%S", time_local))
            Total_balance=api.get_total_balance()
            buy, ask = api.get_buy1_and_sell_one(market)
            price_list.append(buy)
            print(dt)
            time_list.append(dt)
            balance_list.append(Total_balance)
            profit_list.append(Total_balance-balance_list[0])
            print(time_list)

            xticks = list(range(0, len(time_list), 12*60))
            xlabels = [time_list[x] for x in xticks]
            xticks.append(len(time_list))
            xlabels.append(time_list[-1])

            plt.figure(figsize = (7, 10))


            ax=plt.subplot(311)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, price_list, label="Coin Price")
            plt.legend()
            #plt.gcf().autofmt_xdate()  # 自动旋转日期标记
            ax.set_xticks(xticks)
            ax.set_xticklabels(xlabels, rotation=20)


            ax=plt.subplot(312)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, balance_list, label="Balance")

            plt.legend()
            #plt.gcf().autofmt_xdate()  # 自动旋转日期标记
            ax.set_xticks(xticks)
            ax.set_xticklabels(xlabels, rotation=20)

            ax=plt.subplot(313)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, profit_list, label="Profit")
            plt.legend()
            #plt.gcf().autofmt_xdate()  # 自动旋转日期标记
            ax.set_xticks(xticks)
            ax.set_xticklabels(xlabels, rotation=20)


            plt.gcf().subplots_adjust(bottom=0.08)
            plt.gcf().subplots_adjust(top=0.98)
            plt.gcf().subplots_adjust(hspace=0.35)

            plt.savefig(fig_path)
            plt.close()
            with open(file_name, "wb") as fh:
                _dict = dict()
                _dict["balance"] = balance_list
                _dict["time"] = time_list
                _dict["price"] = price_list
                pickle.dump(_dict,fh)
            time.sleep(60)

        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            with open(file_name, "wb") as fh:
                _dict = dict()
                _dict["balance"] = balance_list
                _dict["time"] = time_list
                _dict["price"] = price_list
                pickle.dump(_dict,fh)
            continue
