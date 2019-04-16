from zb_api import *
import pickle
import os


if __name__ == '__main__':
    access_key = '16e04c69-2d0d-4f1d-8304-55983930c485'
    access_secret = '435a1a5a-986a-4d0a-8168-507a707e1237'
    market = "USDT_QC"
    time_list = list()
    balance_list = list()
    profit_list = list()

    fig_path = "figures/sub_account3.png"
    file_name = "pkls/sub_account3.pkl"

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
            plt.figure(12)
            plt.subplot(121)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, balance_list, label="Balance")
            plt.legend()
            plt.gcf().autofmt_xdate()  # 自动旋转日期标记

            plt.subplot(122)
            plt.cla()
            plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
            plt.plot(time_list, profit_list, label="Profit")
            plt.legend()
            plt.gcf().autofmt_xdate()  # 自动旋转日期标记

            plt.savefig(fig_path)
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
