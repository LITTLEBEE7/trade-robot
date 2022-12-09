import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.subAccount_api as SubAccount
import okx.status_api as status

# type your api mesage
#okx real api
api_key = "30d56652-3a4d-49c2-a14e-4a00c343d567"
secret_key = "A74B2B30E721C90168489A103CE5FBC7"
passphrase = "Fan@121216"
# flag = '1'  # 模拟盘 demo trading
flag = '0'  # 实盘 real trading


# okx account api
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# okx trade api
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
#okx funding api
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
# okx public api
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
# okx market api
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)



#获取用户账户余额
# balance =  accountAPI.get_account(ccy="USDT")
# print("账户余额")
# print(balance)

# print("可用保证金")
# print(balance["data"][0]["details"][0]["availEq"])

# 获取币种的当前价格
# currentPrice = marketAPI.get_ticker("BTC-USDT-SWAP")["data"][0]["last"]
# print(currentPrice)
instId = "BTC-USDT"
_instId = instId.upper()
_symbolSplit = _instId.upper().split("-")

print(_symbolSplit[0]+_symbolSplit[1])
print(instId+"-SWAP")