import ccxt
import yaml
from typing import Any
from ..utils import Logger


class Client(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        trade_type: str = 'spot',
        private_file: str = '../config/config.yaml'
    ) -> None:
        """
        Args:
            trade_type (str): 'spot', 'margin' or 'future'
            private_file (str): Enter your config.json path
        """
        cls = type(self)
        self.trade_type = trade_type
        self.private_file = private_file

        if not hasattr(cls, "_init"):
            with open(self.private_file) as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.client = ccxt.binance({
                'apiKey': self.config['API_KEY'],
                'secret': self.config['API_SECRET'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': self.trade_type,
                }
            })

    @property
    def account_info(self) -> Any:
        return self.client

    @property
    def leverage(self):
        try:
            return self.__leverage
        except Exception as e:
            Logger.exception(e)

    @leverage.setter
    def leverage(self, leverage: int, ticker: str = 'ETH/USDT'):
        """
        leverage (int): 1 ~ 50
        ticker (str): 'ETH/USDT'
        """
        client = self.account_info
        if self.trade_type != 'spot':
            self.__leverage = leverage
            client.load_markets()
            res = client.set_leverage(self.__leverage, ticker)
            return res
        else:
            Logger.error(f"trade_type '{self.trade_type}' does not support leverage.")
