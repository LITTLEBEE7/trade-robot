import re
from binance.binance_exchange import BinanceExchange
from binance.trade_api import BinanceTradeApi
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

# 格式化日志
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d/ %H:%M:%S %p"
logging.basicConfig(filename='my_trade.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


# 取消未成交的挂单
def cancel_pending_orders(tradeAPI,instId,algoOrderType):
    # 先获取未成交的订单信息
    try:
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
    except Exception as e:
        logging.info("cancel orders fail")
        logging.info(e)
        return "cancel orders fail"

# 市价平仓（根据用户的持仓模式去平仓）
def close_position(accountAPI,tradeAPI,_instId, _tdMode):
    try:
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
    except Exception as e:
        logging.info("市价平仓失败")
        logging.info(e)

# 设置止盈止损单
def set_tp_or_slOrd(tradeAPI,params,sz,lastOrdId):
    try:
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
    except Exception as e:
        logging.info("设置止盈止损失败")
        logging.info(e)

    
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
    if "symbol" not in _params or _params["symbol"] == "":
        res['msg'] = "未设置交易币种对"
        res["statusCode"] = 2002
        return res
    if "amount" not in _params or _params["amount"] == "":
        res['msg'] = "未设置交易数量"
        res["statusCode"] = 2003
        return res
    if "tdMode" not in _params or _params["tdMode"] == "":
        res['msg'] = "未设置交易模式"
        res["statusCode"] = 2004
        return res
    if "side" not in _params or _params["side"] == "":
        res['msg'] = "未设置订单方向"
        res["statusCode"] = 2006
        return res
    api_key = _params["exchange"]['api_key']
    secret_key = _params["exchange"]['secret_key']
    passphrase = _params["exchange"]['passphrase']
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
    _exchange = _params["exchange"]["name"]
    print(_exchange)
    # 开仓
    # okx交易所
    logging.info("准备开仓")
    if(_exchange == "okx"):
        logging.info("okx交易所")
        flag = '1'  # 模拟盘 demo trading
        # flag = '0'  # 实盘 real trading
        # okx account api
        accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        # okx trade api
        tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        #okx funding api
        fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
        # okx public api
        publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
        try:
            # 取消未成交的订单(一般订单和策略订单)
            cancel_pending_orders(tradeAPI,_instId,"oco")
            # 市价平仓
            close_position(accountAPI,tradeAPI,_instId,_tdMode)
            # 设置持仓模式
            posModeRes = accountAPI.set_position_mode("net_mode")
            logging.info("设置账户的持仓模式:")
            logging.info(posModeRes)
            # 开仓的杠杆倍数
            setLevelRes = accountAPI.set_leverage(instId=_instId, lever=_level, mgnMode=_tdMode)
            logging.info("开的杠杆倍数:")
            logging.info(setLevelRes)
            # 币张转换
            # sz 当交割、永续、期权买入和卖出时，指合约张数。
            converRes =  publicAPI.amount_sz_convert(1,_instId,_sz)
            logging.info("币张转换:")
            logging.info(converRes)
            sz = converRes["data"][0]["sz"]
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
                    set_tp_or_slOrd(tradeAPI,_params,sz,lastOrderId)
        except Exception as e:
            logging.info(e)
            res["statusCode"] = 2005
            res['msg'] = "服务器内部错误"
    # 币安交易所
    elif(_exchange == "binance"):
        try:
            logging.info("币安交易所")
            binanceClient = BinanceExchange(apiKey=api_key,secret=secret_key).client()
            # 是否是测试环境
            binanceClient.set_sandbox_mode(True)
            binanceExchange = BinanceTradeApi()
            res['msg'] =  binanceExchange.palce_order(exchange=binanceClient,symbol=_instId,type=_orderType,side=_side,amount=_sz,level=_level,tdMode=_tdMode,price=_px)
        except Exception as e:
            logging.info(e)
            res["statusCode"] = 2005
            res['msg'] = "服务器内部错误"
    else:
        res['msg']="交易所不存在"
    
    return res


if __name__ == '__main__':
    try:
        # 启动服务
        app.run(port=5000)
    except Exception as e:
        logging.info(e)
        pass