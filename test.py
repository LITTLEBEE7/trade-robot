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
api_key = "test"
secret_key = "test"
passphrase = "test"
flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading

# account api
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# trade api
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
# funding api
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
# public api
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)

# 设置持仓模式
posModeRes = accountAPI.set_position_mode("net_mode")
print("设置账户的持仓模式:")
print(posModeRes)