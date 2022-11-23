
class BinanceTradeApi:
    # 下单
    def palce_order(self,exchange,symbol,type,side,amount,level,tdMode,price):
        # 撤销未完成的订单
        cancelRes = exchange.cancel_all_orders(symbol)
        print(cancelRes)
        # 如果账户存在仓位则市价平仓
        self.close_positions(exchange,symbol)
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
    def close_positions(self,exchange,symbol):
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