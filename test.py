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
api_key = "df3b1c52f37a9d983329addd74e539e531286f247fbd01afaeca6899ed9e61ab"
secret_key = "6b97a974860a309ff524f955e66baf3edd40b3e70544e82115d89c1db9eea73d"
# flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading

# 币安交易所初始化
client = BinanceExchange(apiKey=api_key,secret=secret_key).client()
client.set_sandbox_mode(True)

# 下单
def palce_order(exchange,symbol,type,side,amount,level,tdMode,price):
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
    res =  exchange.create_order(symbol=symbol,type=type,side=side,amount=amount,price=price)
    print(res)

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

# symbol,type,side,amount,level,tdMode,price
# exchange = BinanceTradeApi()
# exchange.palce_order(client,symbol="BTCUSDT",type="market",side="sell",amount="0.1",level="3",tdMode="isolated",price="")