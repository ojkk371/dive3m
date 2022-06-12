import json, math
from ..client import Client


class Fetch(Client):
    def __init__(self, trade_type: str = 'spot') -> None:
        """
        trade_type (str): 'spot', 'margin', or 'future'
        """
        super().__init__(trade_type)

    def fetch_pending(self, symbol: str) -> tuple:
        """
        symbol (str): 'ETH', 'BTC' or 'USDT', ...
        """
        orders = self.client.fetch_orders(symbol=symbol)
        latest_orderdata = orders[-1]['info']
        status = latest_orderdata['status']
        orderid = latest_orderdata['orderId']
        # TODO
        #side = latest_orderdata['side']
        pending = False
        if status == 'NEW':
            pending = True
        return pending, orderid, status

    def fetch_avbl_balance(self, symbol: str) -> float:
        """
        symbol: 'ETH', 'BTC', or 'USDT', ...
        """
        balance = self.client.fetch_balance()
        avbl = math.floor(balance[symbol]['free'] * 100000000)/100000000
        return avbl

    def fetch_own_balances(self):
        balances = self.client.fetch_balance()
        own_coin = [[i,j] for i,j in balances['total'].items() if j != 0.0]
        return own_coin

    def fetch_orderdata(self, ticker: str, visual: bool = True):
        """
        ticker (str): 'ETH/USDT'
        visual (bool): True / False
        """
        market_structures = self.client.load_markets()
        market_structure = market_structures[ticker]
        if visual:
            orderdata = json.dumps(market_structure, indent=4)
        else:
            orderdata = market_structure
        return orderdata
