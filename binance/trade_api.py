import json
import random
import decimal
import math
class BinanceTradeApi:
    # 下单
    def palce_order(self,exchange,symbol,type,side,amount,level,tdMode,price,logger):
        # 撤销未完成的订单
        response = {
        "code":200,
        "msg":""
        }
        cancelRes = exchange.cancel_all_orders(symbol)
        logger.info(cancelRes)
        # 如果账户存在仓位则市价平仓
        # self.close_positions(exchange,symbol)
        # 设置杠杆倍数
        level = exchange.set_leverage(int(level),symbol)
        logger.info(level)
        # 设置逐仓还是全仓 
        try:
            mode = exchange.set_margin_mode(tdMode,symbol)
            logger.info(mode)
        except Exception as e:
            logger.info("设置仓位模式异常信息:")
            logger.info(e)  
        # 设置持仓模式 单向持仓 还是双向持仓
        # 这里设置为单仓模式
        try:
            dual = exchange.set_position_mode(False)
            logger.info(dual)
        except Exception as e:
            logger.info("设置持仓模式异常信息:")
            logger.info(e)
        logger.info("下单结果信息:")
        try:
            res =  exchange.create_order(symbol=symbol,type=type,side=side,amount=amount,price=price,params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
            logger.info(res)
            response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logger.info("下单异常:")
            logger.info(e)
            # exc = json.loads(str(e.args[0])[7:].strip())
            # logger.info(exc)
            # logger.info(exc["code"])
            # logger.info(exc["msg"])
            response["code"] = 3000
            response["msg"]= str(e.args[0])
        return response
    
    # 多笔下单
    def multi_palce_order(self,exchange,symbol,type,side,amount,level,tdMode,price,logger):
        # 撤销未完成的订单
        response = {
        "code":200,
        "msg":""
        }
        cancelRes = exchange.cancel_all_orders(symbol)
        logger.info(cancelRes)
        # 如果账户存在仓位则市价平仓
        # self.close_positions(exchange,symbol)
        # 设置杠杆倍数
        level = exchange.set_leverage(int(level),symbol)
        logger.info(level)
        # 设置逐仓还是全仓 
        try:
            mode = exchange.set_margin_mode(tdMode,symbol)
            logger.info(mode)
        except Exception as e:
            logger.info("设置仓位模式异常信息:")
            logger.info(e)  
        # 设置持仓模式 单向持仓 还是双向持仓
        # 这里设置为单仓模式
        try:
            dual = exchange.set_position_mode(False)
            logger.info(dual)
        except Exception as e:
            logger.info("设置持仓模式异常信息:")
            logger.info(e)
        logger.info("下单结果信息:")
        try:
            res =  exchange.create_order(symbol=symbol,type=type,side=side,amount=amount,price=price,params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
            logger.info(res)
            response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logger.info("下单异常:")
            logger.info(e)
            # exc = json.loads(str(e.args[0])[7:].strip())
            # logger.info(exc)
            # logger.info(exc["code"])
            # logger.info(exc["msg"])
            response["code"] = 3000
            response["msg"]= str(e.args[0])
        return response

    # 随机数
    def uuid22(self,length=22):
        return format(random.getrandbits(length * 4), 'x')
    # 市价平仓
    def close_positions(self,exchange,symbol,logger):
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
                   logger.info(res)
                   response["msg"] = res["info"]["orderId"]
                else:
                    res = exchange.create_order(symbol=symbol,type="market",side="sell",amount=float(sz),price="",params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
                    logger.info(res)
                    response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logger.info("平仓异常:")
            logger.info(e)
            # exc = json.loads(str(e.args[0])[7:].strip())
            # logger.info(exc)
            # logger.info(exc["code"])
            # logger.info(exc["msg"])
            response["code"] = 3000
            response["msg"]= str(e.args[0])
        return response
    
    # 多笔市价平仓
    def close_multi_positions(self,exchange,symbol,proportion,logger):
        response = {
        "code":200,
        "msg":""
        }
        try:
            positions = exchange.fetch_positions([symbol])
            for pos in positions:
                _amount = pos["contracts"]*proportion
                logger.info(type(_amount))
                logger.info(_amount)
                sz = decimal.Decimal(str(_amount)).quantize(decimal.Decimal('0.000'), rounding=decimal.ROUND_DOWN)
                # sz = math.floor(_amount*1000)/1000
                logger.info("平仓数量--")
                logger.info(sz)
                side = pos["side"]
                if(side == "short"):
                   res = exchange.create_order(symbol=symbol,type="market",side="buy",amount=float(sz),price="",params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
                   logger.info(res)
                   response["msg"] = res["info"]["orderId"]
                else:
                    res = exchange.create_order(symbol=symbol,type="market",side="sell",amount=float(sz),price="",params={"newClientOrderId":"x-FZUXxJ8Q"+self.uuid22()})
                    logger.info(res)
                    response["msg"] = res["info"]["orderId"]
        except Exception as e:
            logger.info("平仓异常:")
            logger.info(e)
            # exc = json.loads(str(e.args[0])[7:].strip())
            # logger.info(exc)
            # logger.info(exc["code"])
            # logger.info(exc["msg"])
            response["code"] = 3000
            response["msg"]= str(e.args[0])
        return response