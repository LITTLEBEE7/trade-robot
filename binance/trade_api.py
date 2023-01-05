import logging
import json
import random
class BinanceTradeApi:
    # 下单
    def palce_order(self,exchange,symbol,type,side,amount,level,tdMode,price):
        # 撤销未完成的订单
        response = {
        "code":200,
        "msg":""
        }
        cancelRes = exchange.cancel_all_orders(symbol)
        logging.info(cancelRes)
        # 如果账户存在仓位则市价平仓
        # self.close_positions(exchange,symbol)
        # 设置杠杆倍数
        level = exchange.set_leverage(int(level),symbol)
        logging.info(level)
        # 设置逐仓还是全仓
        try:
            mode = exchange.set_margin_mode(tdMode,symbol)
            logging.info(mode)
        except Exception as e:
            logging.info("设置仓位模式异常信息:")
            logging.info(e)  
        # 设置持仓模式 单向持仓 还是双向持仓
        # 这里设置为单仓模式
        try:
            dual = exchange.set_position_mode(False)
            logging.info(dual)
        except Exception as e:
            logging.info("设置持仓模式异常信息:")
            logging.info(e)
        logging.info("下单结果信息:")
        try:
            res =  exchange.create_order(symbol=symbol,type=type,side=side,amount=amount,price=price,params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
            logging.info(res)
            response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logging.info("下单异常:")
            exc = json.loads(str(e.args[0])[7:].strip())
            logging.info(exc)
            logging.info(exc["code"])
            logging.info(exc["msg"])
            response["code"] = exc["code"]
            response["msg"]= exc["msg"]
        return response

    # 随机数
    def uuid22(self,length=22):
        return format(random.getrandbits(length * 4), 'x')
    # 市价平仓
    def close_positions(self,exchange,symbol):
        response = {
        "code":200,
        "msg":""
        }
        try:
            positions = exchange.fetch_positions([symbol])
            for pos in positions:
                sz = pos["contracts"]
                side = pos["side"]
                if(side == "short"):
                   res = exchange.create_order(symbol=symbol,type="market",side="buy",amount=float(sz),price="",params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
                   logging.info(res)
                   response["msg"] = res["info"]["orderId"]
                else:
                    res = exchange.create_order(symbol=symbol,type="market",side="sell",amount=float(sz),price="",params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
                    logging.info(res)
                    response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logging.info("平仓异常:")
            logging.info(e)
            exc = json.loads(str(e.args[0])[7:].strip())
            logging.info(exc)
            logging.info(exc["code"])
            logging.info(exc["msg"])
            response["code"] = exc["code"]
            response["msg"]= exc["msg"]
        return response