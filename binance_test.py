import random
from re import S
from turtle import position
from binance.binance_exchange import BinanceExchange
import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.subAccount_api as SubAccount
import okx.status_api as Status
import json
from flask import Flask
from flask import request, abort
import os
import _thread
import configparser
import urllib.request
import requests
from binance.trade_api import BinanceTradeApi
import json
import ccxt

# 读取设置
config = {}
if os.path.exists('./config.json'):
    config = json.load(open('./config.json',encoding="UTF-8"))
elif os.path.exists('./config.ini'):
    conf = configparser.ConfigParser()
    conf.read("./config.ini", encoding="UTF-8")
    for i in dict(conf._sections):
        config[i] = {}
        for j in dict(conf._sections[i]):
            config[i][j] = conf.get(i, j)
else:
    print("配置文件 config.json 不存在，程序即将退出")
    exit()

# 服务配置
apiSec = config['service']['api_sec']
# type your api mesage
api_key = ""
secret_key = ""
# flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading

# 币安交易所初始化
client = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': api_key,
    'secret': secret_key,
    'options': { 'defaultType': 'future' },
})
# client.set_sandbox_mode(True)

# 下单
def palce_order(exchange,symbol,type,side,amount,level,tdMode,price):
    response = {
        "code":200,
        "msg":""
    }
    # 撤销未完成的订单
    cancelRes = exchange.cancel_all_orders(symbol)
    print(cancelRes)
    # 如果账户存在仓位则市价平仓
    close_positions(exchange,symbol)
    # 设置杠杆倍数
    level = exchange.set_leverage(int(level),symbol)
    print(level)
    # 设置逐仓还是全仓
    try:
        mode = exchange.set_margin_mode(tdMode,symbol)
        print(mode)
    except Exception as e:
        print("设置仓位模式异常信息:")
        print(e)  
    # 设置持仓模式 单向持仓 还是双向持仓
    # 这里设置为单仓模式
    try:
        dual = exchange.set_position_mode(False)
        print(dual)
    except Exception as e:
        print("设置持仓模式异常信息:")
        print(e)
    print("下单结果信息:")
    try:
        res =  exchange.create_order(symbol=symbol,type=type,side=side,amount=amount,price=price)
        response["msg"] = res["info"]["orderId"]
    except Exception as e:
        print("下单异常:")
        exc = json.loads(str(e.args[0])[7:].strip())
        print(exc)
        print(exc["code"])
        print(exc["msg"])
        response["code"] = exc["code"]
        response["msg"]= exc["msg"]
    return response

# 市价平仓
def close_positions(exchange,symbol):
    try:
        positions = exchange.fetch_positions([symbol])
        for pos in positions:
            sz = pos["contracts"]
            side = pos["side"]
            if(side == "short"):
                exchange.create_order(symbol=symbol,type="market",side="buy",amount=float(sz),price="")
            else:
                exchange.create_order(symbol=symbol,type="market",side="sell",amount=float(sz),price="")
    except Exception as e:
        print(e)

def current_positions(symbol):
    positions = client.fetch_positions(symbol)
    print(positions)


# symbol,type,side,amount,level,tdMode,price
# res = palce_order(client,symbol="BTCUSDT",type="market",side="buy",amount="0.001",level="1",tdMode="isolated",price="")
# print(res)
# 平仓
# close_positions(client,"BTCUSDT")
# 当前的仓位
# current_positions(["BTCUSDT"])

# 获取账户的可用余额
# balance = client.fetch_balance({"type":"future"})
# print(balance["total"])
# print(balance["free"])
# print(balance["used"])

# cancelResult = client.cancel_all_orders("BTCUSDT")
# print(cancelResult)

# price = client.fetch_ticker("BTCUSDT")
# print(price["info"]["lastPrice"])
# income = client.fapiPrivateGetIncome({"incomeType":"API_REBATE"})
# print(json.dumps(income))

# hh = client.fapiPrivateGetApiReferralIfNewUser({"brokerId":"FZUXxJ8Q"})
# print(hh)
# def uuid22(length=22):
#     return format(random.getrandbits(length * 4), 'x')

# print(uuid22())

# history = client.fetch_orders(symbol="BTCUSDT")
# print(history)

print(client)
