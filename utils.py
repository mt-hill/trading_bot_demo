import pandas as pd
import plotly_express as px
from bot import get_price_data
from datetime import datetime, timedelta

trades = pd.read_csv(".data/trades.csv")

def get_balance():
    global balance
    if trades['Side'].iloc[-1] == 'Buy':
        balance = trades['Size (USDT/BTC)'].iloc[-1]
    else:
        balance = trades['Size (USDT/BTC)'].iloc[-2]   
    return round(balance,2)

def profit_loss():
    global pnl
    pnl = balance - trades['Size (USDT/BTC)'].iloc[0]
    return round(pnl,2)

def profit_loss_pct():
    balance = get_balance()
    pnl_pct = (balance/1000-1)*100
    return round(pnl_pct,2)

def total_trades():
    global total
    total = len(trades)//2
    return total

def total_wins():
    global wins
    wins = len(trades[trades['PnL($)'] > 0])
    return wins

def win_pct():
    winpct = wins/total*100
    return round(winpct,2)

def current_trade():
    if trades['Side'].iloc[-1] == 'Sell':
        return False
    else:
        buyPrice = trades['Price'].iloc[-1]
        takeProfit = trades['Price'].iloc[-1]*1.0084
        stopLoss = trades['Price'].iloc[-1]*0.94
        return buyPrice, round(takeProfit,2), round(stopLoss,2)
    
def equity_curve_chart():
    equity_curve = px.line(x=trades['Date'][::2], y=trades['Size (USDT/BTC)'][::2])
    equity_curve.update_layout(xaxis_title='Date', yaxis_title='Capital $')
    equity_curve.update_traces(line=dict(color='#00ffd9'))
    return equity_curve

def current_price():
    timeframe = pd.to_datetime(datetime.now()) - timedelta(hours=1)
    recent_prices = get_price_data(str(timeframe))
    latest_price = recent_prices['Close'].iloc[-1]
    return latest_price
