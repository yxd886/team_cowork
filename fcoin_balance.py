__author__ = 'Ziyang'
from fcoin_api import  *
import os
import pickle

if __name__ == '__main__':
    access_key = '3d606364177e4edcabd29019229317b4'
    access_secret = 'c84923d2aa8d47dab75e6655c3ac78c0'
    market = "tusdusdt"
    api = fcoin_api(access_key, access_secret)
    obj = (api._api.get_balance())
    obj = obj["data"]
    for item in obj:
        if item["currency"]=="ft":
            print(item)
            break