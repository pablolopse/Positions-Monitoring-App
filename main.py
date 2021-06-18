import streamlit as st
import datetime as dt
import hmac
import hashlib
import requests as rq
import pandas as pd
from math import trunc
import math
import time

api_key = "TOBIugMMe8cncoZ3Zb8NUpxGFuCuirjY4YoM4pQTqZDiRwoNAMXUAJo1qyvcPFGF"
secret_key = "Zl1PGmwYmpKUc0CGJ6PreKNYwz2ZsGvssPh6WzLTFr8UZ23GQ0T8QEvzWmnU6I1o"
baseurl = "https://fapi.binance.com"

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

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

def update_graph():
    df = pd.read_csv("balance.csv")
    df = pd.DataFrame({"date":[dt.date.today()], "balance":[0]})
    pd.DataFrame.to_csv("")
def update_data():
    positions = get_open_positions(api_key, secret_key, baseurl)
    btc, eth, ltc = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
            btc = pd.DataFrame({'Symbol': ['BTC'], 'Side': side, 'Quantity': ["$" + "{:.2f}".format(float(position['isolatedWallet']), 2)], 'Enter Price': ["$" + "{:.2f}".format(truncate(float(position['entryPrice']), 2))], 'Mark Price': ["$" + "{:.2f}".format(truncate(float(position['markPrice']), 2))], 'Unrealized PnL ($)': [float(position['unRealizedProfit'])]})
        elif position['symbol'] == 'ETHUSDT':
            eth = pd.DataFrame({'Symbol': ['ETH'], 'Side': side, 'Quantity': ["$" + "{:.2f}".format(float(position['isolatedWallet']), 2)], 'Enter Price': ["$" + "{:.2f}".format(truncate(float(position['entryPrice']), 2))], 'Mark Price': ["$" + "{:.2f}".format(truncate(float(position['markPrice']), 2))], 'Unrealized PnL ($)': [float(position['unRealizedProfit'])]})
        elif position['symbol'] == 'LTCUSDT':
            ltc = pd.DataFrame({'Symbol': ['LTC'], 'Side': side, 'Quantity': ["$" + "{:.2f}".format(float(position['isolatedWallet']), 2)], 'Enter Price': ["$" + "{:.2f}".format(truncate(float(position['entryPrice']), 2))], 'Mark Price': ["$" + "{:.2f}".format(truncate(float(position['markPrice']), 2))], 'Unrealized PnL ($)': [float(position['unRealizedProfit'])]})
            
    df = btc.append(eth).append(ltc)
    df = df.reset_index()
    df.drop('index', axis='columns', inplace=True)
    df = df.style.applymap(color, subset=['Unrealized PnL ($)'])

    return df


st.title("Binance Open Positions")
placeholderT = st.empty()
placeholderB = st.empty()

st.write("")
st.write("")
st.write("")

st.text("Made by Pablo López")

while True:
    try:
        df = update_data()
        balance = get_balance(api_key, secret_key, baseurl)
    except:
        pass
    placeholderT.table(df)
    left_column, right_column = placeholderB.beta_columns(2)
    balance = round(get_balance(api_key, secret_key, baseurl), 2)
    left_column.markdown("<h1 style='text-align: left; color: white;'>Balance</h1>", unsafe_allow_html=True)
    right_column.markdown("<h1 style='text-align: right; color: yellow;'>"+str(balance)+"</h1>", unsafe_allow_html=True)
    time.sleep(30)
