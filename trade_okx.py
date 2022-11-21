import re
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
    logging.info("配置文件 config.json 不存在，程序即将退出")
    exit()

# 服务配置
apiSec = config['service']['api_sec']
# type your api mesage
api_key = "test"
secret_key = "test"
passphrase = "test"
flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading

# 格式化日志
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d/ %H:%M:%S %p"
logging.basicConfig(filename='okx_trade.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# account api
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# trade api
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
# funding api
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
# public api
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)




# 测试用例
# 合约下单
# instId="ADA-USDT-SWAP"
# type="market"
# side="buy"
# amount="1"
# price=None
# tdMode="isolated"
# ret = tradeAPI.place_order(instId=instId,tdMode=tdMode,side=side,ordType=type,sz=amount,px=price)
# logging.info(json.dumps(ret))

# 查看账户配置  Get Account Configuration
# result = accountAPI.get_account_config()
# logging.info(json.dumps(result))

#获取订单的状态
# result = tradeAPI.get_orders('ADA-USDT-SWAP', '512737372757426176')
# logging.info(json.dumps(result))

# 获取交易产品的基础信息
# mesage  = publicAPI.get_instruments(instType="SWAP",instId="ADA-USDT-SWAP")
# logging.info(json.dumps(mesage))

# 获取最新的标记价格
# markPrice = publicAPI.get_mark_price(instType="SWAP",instId="ADA-USDT-SWAP")
# logging.info(json.dumps(markPrice))


# 市价仓位全平  Close Positions
# result = tradeAPI.close_positions('ADA-USDT-SWAP', 'isolated')
# logging.info(json.dumps(result))

# 设置持仓模式  Set Position mode
# long_short_mode：双向持仓 net_mode：单向持仓仅适用交割/永续
# result = accountAPI.get_position_mode('net_mode')
# logging.info(json.dumps(result))

# 张币转换
# ret = publicAPI.amount_sz_convert(type="1",instId="ADA-USDT-SWAP",sz="100")
# logging.info(json.dumps(ret))

# 合约策略下单
# instId="ADA-USDT-SWAP"
# ordType="oco"
# side="sell"
# amount="1"
# # price=None
# tdMode="isolated"
# tpTriggerPx="0.35"
# tpOrdPx="-1"
# slTriggerPx="0.3"
# slOrdPx="-1"
# result=tradeAPI.place_algo_order(instId=instId,tdMode=tdMode,side=side,ordType=ordType,sz=amount,tpTriggerPx=tpTriggerPx,tpOrdPx=tpOrdPx,slTriggerPx=slTriggerPx,slOrdPx=slOrdPx)
# logging.info(json.dumps(result))


# 取消未成交的挂单
def cancel_pending_orders(instId,algoOrderType):
    # 先获取未成交的订单信息
    _instId = instId.upper()
    _symbolSplit = _instId.split("-")
    pendingOrders=tradeAPI.get_order_list(instType= _symbolSplit[2])
    pendingAlgoOrders = tradeAPI.order_algos_list(instType= _symbolSplit[2],ordType=algoOrderType)
    logging.info("当前未成交的订单:")
    logging.info(pendingOrders)
    logging.info(pendingAlgoOrders)
    # 循环遍历未成交的订单然后撤销订单
    for order in pendingOrders["data"]:
            cancelOrdersRes = tradeAPI.cancel_multiple_orders([{"instId":instId,"ordId":order["ordId"]}])
            logging.info("取消未成交的订单:")
            logging.info(cancelOrdersRes)
    # 循环遍历未成交的策略订单然后撤销订单
    for algoOrder in pendingAlgoOrders["data"]:
            cancelAlgoOrdersRes = tradeAPI.cancel_algo_order([{"instId":instId,"algoId":algoOrder["algoId"]}])
            logging.info("取消未成交的订单:")
            logging.info(cancelAlgoOrdersRes)
    return "cancel orders successfuly"

# 市价平仓（根据用户的持仓模式去平仓）
def close_position(_instId, _tdMode):
    accountConf = accountAPI.get_account_config()
    logging.info(accountConf)
    accountPosMode = accountConf["data"][0]["posMode"]
    logging.info("账户的持仓模式:")
    logging.info(accountPosMode)
    if(accountPosMode == "net_mode"):
        logging.info("单向模式平仓:")
        closeNetRes = tradeAPI.close_positions(_instId, _tdMode)
        logging.info(closeNetRes)
    else:
        logging.info("双向模式平仓:")
        closeShortRes = tradeAPI.close_positions(_instId, _tdMode,"short")
        closeLongRes = tradeAPI.close_positions(_instId, _tdMode,"long")
        logging.info(closeShortRes)
        logging.info(closeLongRes)

# 设置止盈止损单
def set_tp_or_slOrd(params,sz,lastOrdId):
    global lastOrdType,lastAlgoOrdId
    algoParams = {
        "instId": params["symbol"],
        "tdMode": params["tdMode"],
        "side": "sell",
        "ordType": "oco",
        "sz": sz
    }
    # 委托价格为-1时，执行市价止损
    if  params['enable_stop_loss']:
        algoParams['slTriggerPx'] = params['slTriggerPx']
        algoParams['slOrdPx'] = "-1"
    if  params['enable_stop_gain']:
        algoParams['tpTriggerPx'] = params['tpTriggerPx']
        algoParams['tpOrdPx'] = "-1"
    # 获取上笔交易的信息
    # 根据上笔交易的状态，设置止盈止损订单
    lastOrderMesage = tradeAPI.get_orders(params["symbol"], lastOrdId)
    logging.info("上笔订单信息:")
    logging.info(lastOrderMesage)
    if lastOrderMesage['data'][0]['state'] == "filled" or lastOrderMesage['data'][0]['state'] == "live":
        algoRes = tradeAPI.place_algo_order(instId=algoParams["instId"],tdMode=algoParams["tdMode"],side=algoParams["side"],ordType=algoParams["ordType"],sz=algoParams["sz"],tpTriggerPx=algoParams["tpTriggerPx"],tpOrdPx=algoParams["tpOrdPx"],slTriggerPx=algoParams["slTriggerPx"],slOrdPx=algoParams["slOrdPx"])
        logging.info("策略订单信息:")
        logging.info(algoRes)
        if 'code' in algoRes and algoRes['code'] == '0':
            lastAlgoOrdId = algoRes['data'][0]['algoId']
    elif lastOrderMesage['data'][0]['state'] == "canceled":
        logging.info("todo")

    
app = Flask(__name__)


@app.before_request
def before_req():
    if request.json is None:
        abort(400)
    # if request.remote_addr not in ipWhiteList:
    #     abort(403)
    if "apiSec" not in request.json or request.json["apiSec"] != apiSec:
        abort(401)


# 接收post请求-下单
@app.route('/trade', methods=['POST'])
def start_trade():
    res = {
        "statusCode":2000,
        "msg":""

    }
    # 获取请求体
    _params = request.json
    logging.info("请求参数：")
    logging.info(_params)
    if "apiSec" not in _params or _params["apiSec"] != apiSec:
        res['msg'] = "apiSec错误"
        res["statusCode"] = 2001
        return res
    if "symbol" not in _params:
        res['msg'] = "未设置交易币种对"
        res["statusCode"] = 2002
        return res
    if "amount" not in _params:
        res['msg'] = "未设置交易数量"
        res["statusCode"] = 2003
        return res
    if "tdMode" not in _params:
        res['msg'] = "未设置交易模式"
        res["statusCode"] = 2004
        return res
    if "side" not in _params:
        res['msg'] = "未设置订单方向"
        res["statusCode"] = 2005
        return res
    _instId = _params["symbol"]
    _orderType = _params["type"]
    _side = _params["side"]
    _sz = _params["amount"]
    if(_orderType == "limit"):
        _px = _params["price"]
    else:
        _px = None
    _tdMode = _params["tdMode"]
    _level = _params["level"]
    # 开仓
    logging.info("准备开仓")
    global lastOrdType
    if _params['side'].lower() in ["buy", "sell"]:
        # 取消未成交的订单(一般订单和策略订单)
        cancel_pending_orders(_instId,"oco")
        # 市价平仓
        close_position(_instId,_tdMode)
        # 设置持仓模式
        posModeRes = accountAPI.set_position_mode("net_mode")
        logging.info("设置账户的持仓模式:")
        logging.info(posModeRes)
        # 开仓的杠杆倍数
        setLevelRes = accountAPI.set_leverage(instId=_instId, lever=_level, mgnMode=_tdMode)
        logging.info("开的杠杆倍数:")
        logging.info(setLevelRes)
        # 币张转换
        converRes =  publicAPI.amount_sz_convert(1,_instId,_sz)
        logging.info(converRes)
        sz = converRes["data"][0]["sz"]
        logging.info("币张转换:")
        if int(sz) < 1:
            res['msg'] = 'Amount is too small. Please increase amount.'
        else:
            # 下单
            orderRes = tradeAPI.place_order(instId=_instId,tdMode= _tdMode,side= _side,ordType= _orderType,sz= sz,px=_px)
            logging.info("下单信息：")
            logging.info(orderRes)
            lastOrderId = orderRes["data"][0]["ordId"]
            res['msg'] = orderRes
            # 设置止盈止损
            if _params['enable_stop_loss'] and _params['enable_stop_gain']:
                set_tp_or_slOrd(_params,sz,lastOrderId)
                lastOrdType = _params['side']
    return res

# 接收post请求-撤单
@app.route('/cancel', methods=['POST'])
def cancel_order():
    res = {
        "statusCode":2000,
        "msg":""

    }
    # 获取请求体
    _params = request.json
    logging.info("请求参数：")
    logging.info(_params)
    _instId = _params["symbol"]
    # 取消未成交的订单(一般订单和策略订单)
    res["msg"] = cancel_pending_orders(_instId,"oco")
    return res

# 接收post请求-平仓
@app.route('/close', methods=['POST'])
def close():
    res = {
        "statusCode":2000,
        "msg":""

    }
     # 获取请求体
    _params = request.json
    logging.info("请求参数：")
    logging.info(_params)
    _instId = _params["symbol"]
    _tdMode = _params["tdMode"]
    res["msg"] = close_position(_instId,_tdMode)
    return res

@app.route('/order', methods=['POST'])
def order():
    res = {
        "statusCode":2000,
        "msg":""

    }
      # 获取请求体
    _params = request.json
    logging.info("参数打印:")
    logging.info(_params)
    return  res

if __name__ == '__main__':
    try:
        # 启动服务
        app.run()
    except Exception as e:
        logging.info(e)
        pass