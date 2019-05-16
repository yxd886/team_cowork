from zb_api import *
import os
import pickle

if __name__ == '__main__':
    access_key = 'c9a579cf-5e0a-4f01-abd2-386cc127a4ad'
    access_secret = 'de38de17-aabb-4d33-a687-5677d0de0a53'
    market = "USDT_QC"
    time_list = list()
    balance_list = list()
    profit_list = list()

    fig_path = "figures/sub_account2.png"
    file_name = "pkls/sub_account2.pkl"

    if os.path.exists(file_name):
        with open(file_name,"rb") as fh:
            _dict=pickle.load(fh)
            balance_list=_dict["balance"]
            time_list = _dict["time"]
        for i in range(len(balance_list)):
            profit_list.append(balance_list[i]-balance_list[0])




    api = zb_api(access_key, access_secret)



    while True:
        try:
            time_now = int(time.time())
            time_local = time.localtime(time_now)

            dt = (time.strftime("%m/%d-%H:%M:%S", time_local))
            Total_balance=api.get_total_balance()
            print(dt)
            time_list.append(dt)
            balance_list.append(Total_balance)
            profit_list.append(Total_balance-balance_list[0])
            print(time_list)
            xticks = list(range(0, len(time_list), 24))
            xlabels = [time_list[x] for x in xticks]
            xticks.append(len(time_list))
            xlabels.append(time_list[-1])

            plt.figure(figsize = (7, 7))

            ax=plt.subplot(211)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, balance_list, label="Balance")

            plt.legend()
            #plt.gcf().autofmt_xdate()  # 自动旋转日期标记
            ax.set_xticks(xticks)
            ax.set_xticklabels(xlabels, rotation=20)

            ax=plt.subplot(212)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, profit_list, label="Profit")
            plt.legend()
            #plt.gcf().autofmt_xdate()  # 自动旋转日期标记
            ax.set_xticks(xticks)
            ax.set_xticklabels(xlabels, rotation=20)

            plt.gcf().subplots_adjust(bottom=0.12)
            plt.gcf().subplots_adjust(top=0.98)
            plt.gcf().subplots_adjust(hspace=0.35)
            plt.savefig(fig_path)
            plt.close()
            with open(file_name, "wb") as fh:
                _dict = dict()
                _dict["balance"] = balance_list
                _dict["time"] = time_list
                pickle.dump(_dict, fh)
            time.sleep(3600)
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            with open(file_name, "wb") as fh:
                _dict = dict()
                _dict["balance"] = balance_list
                _dict["time"] = time_list
                pickle.dump(_dict, fh)
            continue
