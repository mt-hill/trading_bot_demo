import streamlit as st
import pandas as pd
import plotly_express as px
from bot import main_loop, get_price_data
from datetime import datetime, timedelta

st.set_page_config(
    page_title="BTC Trading Bot Demo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #252525;
    padding: 5px 15px;
    border-radius: 10px;
    margin-bottom: 7px;
    margin-top: 7px; 
}        
@media (min-width: 768px) {
  hr {
    display: none;
  }
}

</style>
""", unsafe_allow_html=True)

main_loop()

trades = pd.read_csv('.data/trades.csv')
status = pd.read_csv('.data/status.csv')

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
    if not recent_prices.empty:
        latest_price = recent_prices['Close'].iloc[-1]
        return latest_price
    else:
        return None 

######### SIDEBAR SECTION
with st.sidebar:
    st.markdown("# **:orange[BTC Trading Bot Demo]**")
    with st.expander("Notes", expanded=True):
        st.write('''
                 *This is not a fully functional trading bot but rather a simulated version showing the capabilities of an actual trading bot.*

                 *The bot simulates real trades by executing paper trades based on BTC price action.*

                 *For more info, please read the full documentation or contact me for any enquiries.*''')
    
        st.write('''
                > *Full Docs: [https://github.com/mt-hill/algo_trading_bot_demo](https://github.com/mt-hill/algo_trading_bot_demo/)*
                        
                > *Email: [mth.developer@outlook.com](mailto:mth.developer@outlook.com)*
                 ''')
    st.divider()
    
    with st.expander("Bot Status", expanded=False):
        st.write(f''' 
            Connected to Exchange: **:green[True]**
                    
            Actively Trading: **:green[{status['botactive'].iloc[-1]}]**
        ''')
        st.button("Stop Bot", use_container_width=True, disabled=True)
    
    with st.expander("Bot Settings", expanded=False):
        with st.form("Settings", border=False):
            st.text_input("Buying Condition", 0.00)
            me = st.columns(2)
            with me[0]:
                st.text_input("Take Profit (%)", 0.00)
            with me[1]:
                st.text_input("Stop Loss (%)", 0.00)
            st.slider("Risk per trade (%)", 0, 100, status['risk'].iloc[-1])
            update_settings = st.form_submit_button(label='Update Settings', use_container_width=True, disabled=True)

    with st.expander("API Credentials", expanded=False):
        with st.form("API Keys", border=False):
            st.text_input("Enter API Key", status['apikey'].iloc[-1],type="password")
            st.text_input("Enter API Secret", status['apisecret'].iloc[-1],type='password')
            update_api_keys = st.form_submit_button(label='Update API Credentials', use_container_width=True, disabled=True)
        
######### MAIN SECTION
col = st.columns((2,6,2), gap='medium')
with col[0]:
    st.divider()
    st.markdown(" ### **Account Overview**")
    st.metric(label='Balance (USDT)', value=f'${get_balance()}', delta='')
    st.metric(label='Profit/Loss ($)', value=f'${profit_loss()}', delta=f'{profit_loss_pct()}%')
    st.metric(label='Total Trades', value=total_trades(), delta='')
    st.metric(label='Total Wins', value=total_wins(), delta=f'{win_pct()}%')
with col[1]:
    st.divider()
    st.markdown(' ### Equity Curve')
    st.plotly_chart(equity_curve_chart(), use_container_width=True)
    with st.expander("View Trade History"):
        st.dataframe(trades,use_container_width=True)
with col[2]:
    st.divider()
    st.markdown("### Current Position")
    current = current_trade()
    if current == False:
        st.error("Not in a position, conditions not met")
    else:
        st.button("Close Position", use_container_width=True, disabled=True)
        st.metric(label="Current Price", value=current_price(), delta="")
        st.metric(label="Buy Price", value=current[0], delta="")
        st.metric(label="Take Profit", value=current[1], delta="")
        st.metric(label="Stop Loss", value=current[2], delta="")
