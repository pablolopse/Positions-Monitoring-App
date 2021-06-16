import streamlit as st
import datetime as dt
import hmac
import hashlib
import requests as rq
import pandas as pd
from math import trunc
import time


api_key = KEY
secret_key = S_KEY

baseurl = "https://fapi.binance.com"

st.title("Binance Open Positions")

def color(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

def get_open_positions(api_key, secret_key, baseurl):

    # GET POSITIONS INFORMATION
    time = trunc(dt.datetime.now().timestamp() * 1000)
    headers={'X-MBX-APIKEY':api_key}
    msg = 'recvWindow=50000&timestamp='+str(time)

    signature = hmac.new(
        bytes(secret_key , 'latin-1'),
        msg=bytes(msg, 'latin-1'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    params={'recvWindow':50000, 'timestamp':time, 'signature':signature}
    r02 = rq.get(baseurl+"/fapi/v2/positionRisk", headers=headers, params=params).json()

    # Get the tickers with current open positions
    positions = [i for i in r02 if float(i['positionAmt']) != 0]

    return positions

def get_balance(api_key, secret_key, baseurl):
    # Get the USDT balance
    time = trunc(dt.datetime.now().timestamp() * 1000)
    headers={'X-MBX-APIKEY':api_key}
    msg = 'recvWindow=50000&timestamp='+str(time)

    signature = hmac.new(
        bytes(secret_key , 'latin-1'),
        msg=bytes(msg, 'latin-1'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    params={'recvWindow':50000, 'timestamp':time, 'signature':signature}
    r = rq.get(baseurl+"/fapi/v2/account", headers=headers, params=params)
    wallet = r.json()
    balance = float(wallet['totalWalletBalance']) + float(wallet['totalUnrealizedProfit'])

    return balance

positions = get_open_positions(api_key, secret_key, baseurl)

for position in positions:

    if float(position['entryPrice']) < float(position['markPrice']) and float(position['unRealizedProfit']) > 0:
        side = "Long"
    elif float(position['entryPrice']) > float(position['markPrice']) and float(position['unRealizedProfit']) > 0:
        side = "Short"
    elif float(position['entryPrice']) < float(position['markPrice']) and float(position['unRealizedProfit']) < 0:
        side = "Short"
    elif float(position['entryPrice']) > float(position['markPrice']) and float(position['unRealizedProfit']) < 0:
        side = "Long"
    else:
        side = "Both"

    if position['symbol'] == 'BTCUSDT':
        btc = pd.DataFrame({'Symbol': ['BTC'], 'Side': side, 'Quantity': [position['positionAmt']], 'Enter Price': [position['entryPrice']], 'Mark Price': [position['markPrice']], 'Unrealized PnL': [float(position['unRealizedProfit'])]})
    elif position['symbol'] == 'ETHUSDT':
        eth = pd.DataFrame({'Symbol': ['ETH'], 'Side': side, 'Quantity': [position['positionAmt']], 'Enter Price': [position['entryPrice']], 'Mark Price': [position['markPrice']], 'Unrealized PnL': [float(position['unRealizedProfit'])]})
    elif position['symbol'] == 'LTCUSDT':
        ltc = pd.DataFrame({'Symbol': ['LTC'], 'Side': side, 'Quantity': [position['positionAmt']], 'Enter Price': [position['entryPrice']], 'Mark Price': [position['markPrice']], 'Unrealized PnL': [float(position['unRealizedProfit'])]})

df = btc.append(eth).append(ltc)
df = df.reset_index()
df.drop('index', axis='columns', inplace=True)
df = df.style.applymap(color, subset=['Unrealized PnL'])

table = st.table(df)

balance = round(get_balance(api_key, secret_key, baseurl), 2)

st.markdown("## Balance: " + str(balance))

