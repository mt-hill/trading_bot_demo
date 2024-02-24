import pandas as pd
from binance import Client
client = Client()
from datetime import timedelta

def main_loop():
    ### GETS PREVIOUS PRICE
    old_prices = pd.read_csv(".data/prices.csv")
    old_prices = old_prices.set_index("Time")
    time = pd.to_datetime(old_prices.index[-1]) - timedelta(hours=12)

    ### GETS AND SORT NEW PRICE DATA
    new_prices = get_price_data(str(time))
    new_prices_cleaned = sort_new_prices(new_prices)
    
    ### GETS CURRENT CAPITAL AND STATUS
    current_status = get_status()
    capital, position = current_status[0], current_status[1]

    ### RUNS TRADING CONDITIONS
    trading_loop(new_prices_cleaned, capital, position)
    
    ### ADDS UPDATED PRICE DATA TO CSV
    updated_prices = pd.concat([old_prices, new_prices_cleaned])
    updated_prices.to_csv(".data/prices.csv")


### TRADING LOGIC AND CONDITIONS
def trading_loop(df, capital, position):
    for index,row in df.iterrows():
        if not position:
            if row['diff'] > 0.016:
                buy_price = row.Close
                date = index
                side = "Buy"
                coins = capital / buy_price
                pnl = 0
                pct = 0
                add_trades(date, side, buy_price, capital, pnl, pct)
                position = True
        if position:
            retrieved_buy_price = get_buy_price()
            if row.Close >= retrieved_buy_price * 1.0084:
                sell_price = row.Close
                date = index
                side = "Sell"
                pnl = (coins * sell_price) - capital
                capital = coins * sell_price
                pct = (sell_price/retrieved_buy_price) - 1
                add_trades(date, side, sell_price, coins, pnl, pct)
                position = False
            elif row.Close <= retrieved_buy_price * 0.94:
                sell_price = row.Close
                date = index
                side = "Sell"
                pnl = (coins * sell_price) - capital
                capital = coins * sell_price
                pct = (sell_price/retrieved_buy_price) - 1
                add_trades(date, side, sell_price, coins, pnl, pct)
                position = False

    ### UPDATE STATUS CSV        
    update_status(capital, position)      

### GETS PRICE DATA FROM BINANCE API
def get_price_data(start):
    frame = pd.DataFrame(client.get_historical_klines('BTCUSDT',
                                                     '1m',
                                                     start))
    frame = frame.iloc[:,0:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit = 'ms')
    frame = frame.astype(float)
    return frame

### CLEANS NEW PRICE DATA AND ADDS TWELVE HOUR CHANGE COLUMN
def sort_new_prices(new_prices):
    new_prices['twelve'] = new_prices.Close.shift(720)
    new_prices.dropna(inplace=True)
    new_prices['diff'] = new_prices['Close']/new_prices['twelve'] - 1
    return new_prices

### GET LAST BUY PRICE
def get_buy_price():
    trades = pd.read_csv(".data/trades.csv")
    buy_price = trades['Price'].iloc[-1]
    return buy_price
### GETS AND RETURNS STATUS
def get_status():
    status = pd.read_csv(".data/status.csv")
    position = status['position'].iloc[0]
    capital = status['capital'].iloc[0]
    return capital, position

### UPDATES STATUS IN CSV
def update_status(capital, position):
    status = pd.read_csv(".data/status.csv")
    status['capital'] = capital
    status['position'] = position
    status.to_csv(".data/status.csv", index=False)

### ADDS TRADES TO CSV
def add_trades(date, side, price, capital, pnl, pct):
    df = pd.DataFrame([date, side, price, capital, pnl, pct])
    df = df.T
    df.to_csv('.data/trades.csv', mode='a', index=False, header=False)

