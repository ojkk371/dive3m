import time, math, json, config, argparse
from termcolor2 import colored
import asyncio, uvloop, uvicorn
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel
import ccxt


def set_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Bind socket to this host. [default: 0.0.0.0]")
    parser.add_argument("--port", type=int, default="80", help="Bind socket to this host. [default: 80]")
    parser.add_argument("--order_type", type=str, default="limit", help="Set order type. ['limit', 'market']")
    parser.add_argument("--trade_type", type=str, default="spot", help="Set trade type. ['spot', 'margin', 'future']")
    parser.add_argument("--take_profit", type=bool, default=False, help="Whether to use TP or not. [default: False]")
    parser.add_argument("--stop_loss", type=bool, default=False, help="Whether to use SL or not. [default: False]")
    parser.add_argument("--leverage", type=bool, default=False, help="Whether to use leverage or not. [default: False]")
    args = parser.parse_args()
    return args

ARGS = set_argument()

HOST = ARGS.host
PORT = ARGS.port

app = FastAPI()
#pipeline = None


class TradingViewHook(BaseModel):
    passphrase: str
    timestamp: str
    exchange: str
    ticker: str
    strategy: dict


class UserInfo(BaseModel):
    apiKey: str
    secret: str


# Client.py
class Client(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        trade_type: str = 'spot',
    ):
        cls = type(self)
        self.trade_type = trade_type
        self.config = config

        if not hasattr(cls, "_init"):
            self.client = ccxt.binance({
                'apiKey': self.config.API_KEY,
                'secret': self.config.API_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': self.trade_type,
                }
            })

    def get_account_info(self):
        self.account = self.client
        return self.account

    def set_lev(self, leverage: int, ticker: str = 'ETH/USDT'):
        self.client.load_markets()
        res = self.client.set_leverage(leverage, ticker)
        return res


# Order.py
class Order(Client):
    def __init__(self, trade_type: str = 'spot'):
        super().__init__(trade_type)
        
    def open_order(self, ticker: str, order_type: str, side: str, amount: float, price: float, isolated):
        """
        ticker: 'ETH/USDT'
        order_type: 'limit', 'market'
        side: 'buy', 'sell'
        amount: 1000
        price: 2345.67
        isolated: False
        """
        self.ticker = ticker
        self.order_type = order_type.upper()
        self.side = side
        self.amount = amount
        self.price = price
        self.isolated = isolated

        base, _ = split_ticker(self.ticker)
        if self.isolated is not None:
            trade_mode = str(self.isolated).upper()
            params = {"type": self.trade_type, 'isIsolated': trade_mode}
        else:
            params = {"type": self.trade_type}

        try:
            print(colored(f"sending {self.order_type} {self.side} {self.ticker} order - {self.amount}({base}) {self.price}({self.ticker})", "yellow", attrs=['bold']))
            order = self.client.create_order(symbol=self.ticker, type=self.order_type, side=self.side, amount=self.amount, price=self.price, params=params)
        except Exception as e:
            print(f"{self.order_type} an exception occured -", colored(f"{e}", "red", attrs=['bold']))
            return False
        return order
        
    def cancel_order(self, orderid, ticker):
        try:
            print(colored(f"{ticker}_{orderid} (ticker_orderId) 에 대한 주문 취소 요청 중입니다..."))
            result = self.client.cancel_order(id=orderid, symbol=ticker)
            if result is not None:
                print(colored(f"{ticker}_{orderid} 에 대한 주문건 취소되었습니다."))
        except Exception as e:
            print(f"{orderid} an exception occured -", colored(f"{e}", "red", attrs=['bold']))
            return False
        return result

    def cancel_pending(self, ticker):
        """
        ticker: 'ETH/USDT'
        """
        pass

    def dca_order(self, symbol: str, order_type: str, price: float, ticker: str, avbl: float, side: str, ratio: int):
        """
        symbol: 'ETH' or 'USDT'
        order_type: 'limit', 'market'
        price: 2345.67
        ticker: 'ETH/USDT'
        avbl: 123.4567
        side: 'buy'
        ratio: 0.1 (=10%)
        """
        if symbol == 'USDT':
            amount = math.floor(((avbl / price)*ratio)*10000)/10000
        else:
            amount = math.floor((avbl*ratio)*10000)/10000
        used_usdt = math.floor((amount*price)*100000000)/100000000
        if used_usdt >= 10.00000000: # MIN_NOTIONAL >= 10.8f
            order_response = self.open_order(ticker, order_type, side, amount, price, isolated=None)
            print(colored(f"avbl: {avbl} {symbol}", "blue", attrs=['bold']))
            print(colored(f"amount: {amount}, used_usdt: {used_usdt}", "blue", attrs=['bold']))
            return order_response


# Fetch
class Fetch(Client):
    def __init__(self, trade_type: str = 'spot') -> None:
        super().__init__(trade_type)

    def fetch_pending(self, symbol:str) -> tuple:
        orders = self.client.fetch_orders(symbol=symbol)
        latest_orderdata = orders[-1]['info']
        status = latest_orderdata['status']
        orderid = latest_orderdata['orderId']
        side = latest_orderdata['side']
        pending = False
        if status == 'NEW':
            pending = True
        return pending, orderid, status

    def fetch_avbl_balance(self, symbol: str) -> float:
        balance = self.client.fetch_balance()
        avbl = math.floor(balance[symbol]['free'] * 100000000)/100000000
        return avbl

    def fetch_orderdata(self, ticker: str, visual: bool = True):
        market_structures = self.client.load_markets()
        market_structure = market_structures[ticker]
        if visual:
            orderdata = json.dumps(market_structure, indent=4)
        else:
            orderdata = market_structure
        return orderdata


# utils.py
def reformat_ticker(ticker: str) -> str:
    """
    input: 'ETHUSDTPERP'
    output: 'ETH/USDT'
    """
    if "PERP" in ticker:
        ticker = ticker.strip("PERP")
    idx = ticker.find("USDT")
    ticker = ticker[:idx]+'/'+ticker[idx:]
    return ticker

def split_ticker(ticker: str) -> tuple:
    """
    input: 'ETH/USDT'
    output: 'ETH', 'USDT'
    """
    assets = ticker.split('/')
    base_asset = assets[0]
    quote_asset = assets[1]
    return base_asset, quote_asset


@app.get('/userinfo/{passphrase}')
async def get_info(passphrase: str) -> list:
    if passphrase == config.WEBHOOK_PASSPHRASE:
        exchange = Client().get_account_info()
        balances = exchange.fetch_balance()
        own_coin = [[i,j] for i,j in balances['total'].items() if j != 0.0]
        return own_coin


@app.post('/strategy/{alertname}')
async def webhook(alertname: str, item: TradingViewHook) -> dict:
    data = item.dict()

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        print(data['ticker'], data['strategy']['order_id'])
        return {
            "code": "error",
            "data": "passphrase is not correct"
        }
    else:
        side = data['strategy']['order_action']     # 'buy' or 'sell'
        ticker = reformat_ticker(data['ticker'])    # 'ETH/USDT'
        price = math.floor((data['strategy']['order_price'])*100000000)/100000000   # 2345.67 ??
    
        order = Order(trade_type=ARGS.trade_type)
        fetch = Fetch(trade_type=ARGS.trade_type)

        base, quote = split_ticker(ticker)  # 'ETH', 'USDT'

        if side == 'buy':
            avbl = fetch.fetch_avbl_balance(data['ticker'])
            #import pdb;pdb.set_trace();
            return avbl
#            order_response = order.dca_order(quote, ARGS.order_type, price, ticker, avbl, side, ratio=1)
#            if order_response:
#                print(colored(f"{side} 주문신청 완료 _ price: {price}", "green", attrs=['bold']))
#                time.sleep(10)
#                pending, orderid, status = fetch.fetch_pending(quote)
#                if pending:
#                    order.cancel_order(orderid=orderid, ticker=ticker)
#                    print(colored("미체결건 취소완료", "yellow", attrs=['bold', 'underline']))
#                    return {
#                        "code": "미체결 취소완료",
#                        "data": data,
#                        "status": status
#                    }
#                else:
#                    print(colored("체결 완료", "cyan", attrs=['bold']))
#                    return {
#                        "code": "체결 완료",
#                        "data": data,
#                        "status": status
#                    }
#            else:
#                print(colored("주문 실패", "yellow", attrs=['bold']))
#                return {
#                    "code": "error",
#                    "message": "order failed"
#                }
#        else:
#            avbl = fetch.fetch_avbl_balance(base)
#            order_response = order.dca_order(base, ARGS.order_type, price, ticker, avbl, side, ratio=1)
#            if order_response:
#                print(colored(f"{side} 주문신청 완료 _ price: {price}", "magenta", attrs=['bold']))
#                _, _, status = fetch.fetch_pending(data['ticker'])
#                return {
#                    "code": "success",
#                    "data": data,
#                    "status": status
#                }
#            else:
#                print(colored("주문 실패", "yellow", attrs=['bold']))
#                return {
#                    "code": "error",
#                    "message": "order failed"
#                }



if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    uvicorn.run(app, host=HOST, port=PORT)
