import ccxt

class BinanceExchange:
    _paiKey=""
    _secret=""
    def __init__(self,apiKey,secret):
        self._paiKey = apiKey
        self._secret = secret

    def client(self):
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey': self._paiKey,
            'secret': self._secret,
            'options': { 'defaultType': 'future' },
        })
        return exchange
