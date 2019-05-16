if __name__ == '__main__':
    access_key = '5b9d8e1d3bb0e1603385ab4db4bfaa35'
    access_secret = '9pQIuik3qw1NtghYoC9fNX6Joea12xearS6fOjFLwH6VWRgaoDeILDpTJQoVEIQA'
    tradPWD = "dxydxy835472123"

    api = bit_api(access_key,access_secret,tradPWD)
    print(api.get_depth("btc_usdt"))
    print(api.query_account())
    print(api.get_order_status("btc_usdt",11111))