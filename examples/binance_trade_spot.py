import time
import math
import argparse
from typing import List
import asyncio, uvloop, uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from dive3m.order import Order
from dive3m.fetch import Fetch
from dive3m.utils import *



def set_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Bind socket to this host. [default: 0.0.0.0]"
    )
    parser.add_argument(
            "--port",
            type=int,
            default="80",
            help="Bind socket to this host. [default: 80]"
    )
    parser.add_argument("--config",
            type=str,
            default="../config/config.yaml",
            help="Enter your config.yaml path. [default: '../config/config.yaml']"
    )
    parser.add_argument("--order_type",
            type=str,
            default="limit",
            help="Set order type. ['limit', 'market']"
    )
    parser.add_argument(
            "--trade_type",
            type=str,
            default="spot",
            help="Set trade type. ['spot', 'margin', 'future']"
    )
    parser.add_argument(
            "--take_profit",
            type=bool,
            default=False,
            help="Whether to use TP or not. [default: False]"
    )
    parser.add_argument(
            "--stop_loss",
            type=bool,
            default=False,
            help="Whether to use SL or not. [default: False]"
    )
    parser.add_argument(
            "--leverage",
            type=bool,
            default=False,
            help="Whether to use leverage or not. [default: False]"
    )
    args = parser.parse_args()
    return args


ARGS = set_argument()

HOST = ARGS.host
PORT = ARGS.port
CONF = ARGS.config

app = FastAPI()

order = Order(trade_type=ARGS.trade_type)
fetch = Fetch(trade_type=ARGS.trade_type)
config = load_config(CONF)


class TradingViewHook(BaseModel):
    passphrase: str
    timestamp: str
    exchange: str
    ticker: str
    strategy: dict


@app.get('/')
async def home() -> str:
    return "dive3m_with_FastAPI"


@app.get('/userinfo/{passphrase}')
async def get_userinfo(passphrase: str):
    if passphrase == config['WEBHOOK_PASSPHRASE']:
        own = fetch.fetch_own_balances()
        return own


@app.post('/strategy/{strategy_name}')
async def webhook(strategy_name: str, alert: TradingViewHook) -> dict:
    data = alert.dict()

    if data['passphrase'] != config['WEBHOOK_PASSPHRASE']:
        print(data['ticker'], data['strategy']['order_id'])
        return {
            "code": "error",
            "data": "passphrase is not correct"
        }
    else:
        side = data['strategy']['order_action']     # 'buy' or 'sell'
        ticker = reformat_ticker(data['ticker'])    # 'ETH/USDT'
        price = math.floor((data['strategy']['order_price'])*100000000)/100000000   # 2345.67: (float)

        base, quote = split_ticker(ticker)  # 'ETH', 'USDT'

        if side == 'buy':
            avbl = fetch.fetch_avbl_balance(quote)
            order_response = order.dca_order(
                    symbol=quote,
                    order_type=ARGS.order_type,
                    price=price,
                    ticker=ticker,
                    avbl=avbl,
                    side=side,
                    ratio=1
            )
            if order_response:
                #Logger.info(f"{side} 주문신청 완료 - price: {price}")
                time.sleep(10)
                pending, orderid, status = fetch.fetch_pending(data['ticker'])
                if pending:
                    order.cancel_order(orderid=orderid, ticker=ticker)
                    Logger.info("미체결건 취소완료")
                    return {
                        "code": "미체결 취소완료",
                        "data": data,
                        "status": status
                    }
                else:
                    Logger.info("체결 완료")
                    return {
                        "code": "체결 완료",
                        "data": data,
                        "status": status
                    }
            else:
                Logger.error("주문 실패")
                return {
                    "code": "error",
                    "message": "order failed"
                }
        else:
            avbl = fetch.fetch_avbl_balance(base)
            order_response = order.dca_order(
                    symbol=base,
                    order_type=ARGS.order_type,
                    price=price,
                    ticker=ticker,
                    avbl=avbl,
                    side=side,
                    ratio=1
            )
            if order_response:
                Logger.info(f"{side} 주문신청 완료 - Price: {price}")
                _, _, status = fetch.fetch_pending(data['ticker'])
                return {
                    "code": "success",
                    "data": data,
                    "status": status
                }
            else:
                Logger.error("주문 실패")
                return {
                    "code": "error",
                    "message": "order failed"
                }



if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    uvicorn.run(app, host=HOST, port=PORT)
