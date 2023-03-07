import random
import re
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
import logging
from logging.handlers import TimedRotatingFileHandler
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


# 格式化日志
# currentPath = os.getcwd().replace('\\','/')
# log_path = os.path.join(currentPath,"my_trade.log")
# file_handler = TimedRotatingFileHandler(
#     filename=log_path, when="MIDNIGHT", interval=1, backupCount=30
# )
# file_handler.suffix = "%Y-%m-%d.log"
# # extMatch是编译好正则表达式，用于匹配日志文件名后缀
# # 需要注意的是suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。
# file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
# # 定义日志输出格式
# file_handler.setFormatter(
#     logging.Formatter(
#         "[%(asctime)s] [%(process)d] [%(levelname)s] - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"
#     )
# )
# logger = logging.getLogger("my_trade.log").addHandler(file_handler)
# # LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# # DATE_FORMAT = "%Y/%m/%d/ %H:%M:%S %p"
# # logging.basicConfig(filename='log/my_trade.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def setup_log(log_name):
    # 创建logger对象。传入logger名字
    logger = logging.getLogger(log_name)
    currentPath = os.getcwd().replace('\\','/')
    log_path = os.path.join(currentPath+"/log",log_name)
    # 设置日志记录等级
    logger.setLevel(logging.INFO)
    # interval 滚动周期，
    # when="MIDNIGHT", interval=1 表示每天0点为更新点，每天生成一个文件
    # backupCount  表示日志保存个数
    file_handler = TimedRotatingFileHandler(
        filename=log_path, when="MIDNIGHT", interval=1, backupCount=30
    )
    # filename="mylog" suffix设置，会生成文件名为mylog.2020-02-25.log
    file_handler.suffix = "%Y-%m-%d.log"
    # extMatch是编译好正则表达式，用于匹配日志文件名后缀
    # 需要注意的是suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    # 定义日志输出格式
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(process)d] [%(levelname)s] - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"
        )
    )
    logger.addHandler(file_handler)
    return logger

# 服务配置
apiSec = config['service']['api_sec']
# type your api mesage
api_key = "HYnhaQ4kmPNiWEqP22UkYvsQDXFa4ogUUUFMRmuGJmvpZgJCXOJPL2mLP9SARDNW"
secret_key = "Uucdbt3Pl8eyVZszzROIqGIDhKKYQBv15yXGO2Syz0hTnVoPjF9UT1FlYuuQDcbv"
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
# 可用保证金
# print("可用保证金")
# print(balance["free"]["USDT"])


# cancelResult = client.cancel_all_orders("BTCUSDT")
# print(cancelResult)

# price = client.fetch_ticker("BTCUSDT")
# print(price["info"]["lastPrice"])
# income = client.fapiPrivateGetIncome({"incomeType":"API_REBATE"})
# print(json.dumps(income))

# 获取返佣数据总览
# overview = client.fapiPrivateGetApiReferralOverview()
# print(json.dumps(overview))
# # 获取交易者每天交易明细 

# traderSummary = client.fapiPrivate_get_apireferral_tradersummary()
# print(json.dumps(traderSummary))

# customization = client.fapiPrivate_get_apireferral_customization()
# print(json.dumps(customization))

# 获取交易者数量
# traderNum = client.fapiPrivate_get_apireferral_tradernum()
# print(json.dumps(traderNum))

# hh = client.fapiPrivateGetApiReferralIfNewUser({"brokerId":"FZUXxJ8Q"})
# print(hh)
# def uuid22(length=22):
#     return format(random.getrandbits(length * 4), 'x')

# print(uuid22())

# history = client.fetch_orders(symbol="BTCUSDT")
# print(history)


# 获取用户的交易记录

# logger = setup_log("my_trade")
# history2 = client.fapiPrivateGetUserTrades({"symbol":"BTCUSDT"})
# print(json.dumps(history2))
# order1 = client.fetch_order(id="126090619157",symbol="BTCUSDT")
# print(json.dumps(order1))
order2 = client.fetch_order(id="126095854155",symbol="BTCUSDT")
print(json.dumps(order2))

# 用户当前的持仓
# positions = client.fapiPrivateGetAccount()
# print(json.dumps(positions))
