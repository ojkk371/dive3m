from typing import Any
import yaml, json



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

def load_config(path: str) -> dict:
    """
    input: yaml
    output: json
    """
    filename = path.split('.')
    ext = filename[-1]
    if ext == 'yaml':
        with open(path, encoding='utf-8') as y:
            config = yaml.safe_load(y)
            return config
    else:
        with open(path, 'r') as j:
            config = json.load(j)
            return config


if __name__ == "__main__":

    test = load_config('../../config/config.yaml')
    print(test)
