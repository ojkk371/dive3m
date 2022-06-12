<p align="center">
    <img src="../assets/logo.png", height="200x">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9.x-blue?style=flat-square">
  <img src="https://img.shields.io/badge/fastapi-0.78.0-green?style=flat-square">
  <img src="https://img.shields.io/badge/ccxt-1.84.27-green?style=flat-square">
  <a href="https://github.com/ccxt/ccxt/wiki/Exchange-Markets">
      <img src="https://img.shields.io/badge/exchanges-115-green?style=flat-square">
  </a>
</p>  
  
----

`dive3m` is an automatic trading system.  

## Structure
```
dive3m
.
├── README.py
├── __about__.py
├── __init__.py
├── client : binance api 로그인 모듈
│   ├── __init__.py
│   └── client.py
├── fetch : 조회에 관련된 모듈
│   ├── __init__.py
│   └── fetch.py
├── order : 주문에 관련된 모듈
│   ├── __init__.py
│   └── order.py
└── utils : 파싱과 관련된 유틸함수
    ├── __init__.py
    ├── command_poller.py
    ├── formatting.py
    └── logger.py
```
