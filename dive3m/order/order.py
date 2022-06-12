import math
from typing import Any
from ..client import Client
from ..utils import split_ticker, Logger


class Order(Client):
    def __init__(self, trade_type: str = 'spot') -> None:
        self.trade_type = trade_type
        super().__init__(self.trade_type)
       
    def open_order(
        self,
        test: bool = False,
        isolated: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        ticker (str): 'ETH/USDT'
        order_type (str): 'limit', 'market'
        side (str): 'buy', 'sell'
        amount (float): 1000
        price (float): 2345.67
        test (bool): False
        isolated (bool): False
        """
        ticker = kwargs['ticker']
        order_type = kwargs['order_type']
        side = kwargs['side']
        amount = kwargs['amount']
        price = kwargs['price']

        base, _ = split_ticker(ticker)
        if isolated:   # trade_type = margin or future
            trade_mode = str(isolated).upper()
            params = {
                    "type": self.trade_type,
                    "isIsolated": trade_mode,
                    "test": test
            }
        else:   # trade_type = spot
            params = {
                    "type": self.trade_type,
                    "test": test
            }

        try:
            order_response = self.client.create_order(
                    symbol=ticker,
                    type=order_type,
                    side=side,
                    amount=amount,
                    price=price,
                    params=params
            )
            if order_response is not None:
                Logger.info(
                    f"{order_type} {side} {ticker} 에 대한 주문 요청 "
                    f"Amount: {amount}({base}), Price: {price}({ticker})"
                )
        except Exception as e:
            Logger.error(f"{order_type} an exception occured - {e}")
            return False
        return order_response
  
    def cancel_order(self, orderid: int, ticker: str = 'ETH/USDT'):
        """
        orderid (int): 123412313
        ticker (str): 'ETH/USDT'
        """
        try:
            Logger.warning(
                f"미체결 주문 Ticker: {ticker}, Orderid: {orderid} 취소 요청"
            )
            result = self.client.cancel_order(id=orderid, symbol=ticker)
            if result is not None:
                Logger.info(
                    f"미체결 주문 Ticker: {ticker}, Orderid: {orderid} 취소 완료"
                )
        except Exception as e:
            Logger.error(f"{orderid} an exception occured - {e}")
            return False
        return result

    # TODO
    def cancel_pending(self, ticker: str):
        """
        ticker (str): 'ETH/USDT'
        """
        pass

    def dca_order(
        self,
        ratio: float,
        **kwargs: Any,
    ):
        """
        symbol (str): 'ETH' or 'USDT'
        order_type (str): 'limit', 'market'
        price (float): 2345.67
        ticker (str): 'ETH/USDT'
        avbl (float): 123.4567
        side (str): 'buy'
        ratio (float): 0.1 (=10%)
        """
        symbol = kwargs['symbol']
        order_type = kwargs['order_type']
        price = kwargs['price']
        ticker = kwargs['ticker']
        avbl = kwargs['avbl']
        side = kwargs['side']

        if symbol == 'USDT':
            amount = math.floor(((avbl / price)*ratio)*10000)/10000
        else:
            amount = math.floor((avbl*ratio)*10000)/10000
        used_usdt = math.floor((amount*price)*100000000)/100000000
        if used_usdt >= 10.00000000: # MIN_NOTIONAL >= 10.8f
            try:
                order_response = self.open_order(
                        ticker=ticker,
                        order_type=order_type,
                        side=side,
                        amount=amount,
                        price=price
                )
                if order_response is not None:
                    Logger.info(f"Available_balance: {avbl} {symbol}")
                    Logger.info(f"Amount: {amount}({ratio*100}%), Used_balance: {used_usdt}")
                    Logger.info(f"분할매매 Ticker: {ticker}, Price: {price} 주문 성공")
                    return order_response
            except Exception as e:
                Logger.error("")
                return False
