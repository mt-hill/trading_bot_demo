import streamlit as st
import pandas as pd
from utils import *
from bot import main_loop

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

######### SIDEBAR SECTION
with st.sidebar:
    st.markdown("# **:orange[BTC Trading Bot Demo]**")
    st.markdown("*This is a demonstration of a crypto algorithic trading bot. For demo purposes, some features are disabled. Please read the notes below.*")
    with st.expander("Notes", expanded=False):
        st.write('''
                 :orange[***IMPORTANT***]

                *This app executes paper trades based on real BTC price action. It is mimicking real trades. The win rate is accurate and the strategy could be profitable.*
                 
                *It's a basic strategy created for demostration purposes. It doesn't take into consideration slippage and trading fees.*

                *If you have any enquires such as hiring or working with me, contact me below.*                
                 ''')
        st.write('''
                 :orange[***LINKS***]
            > *Full Documentation: [Github](https://github.com/mt-hill)* 
              *Contact: [mattyhill@outlook.com](mailto:mattyhill@outlook.com)*''')
    
    st.divider()
    
    with st.expander("Bot Status", expanded=True):
        st.write(f''' 
            Connected to Exchange: **:green[True]**
                    
            Actively Trading: **:green[{status['botactive'].iloc[-1]}]**
        ''')
        st.button("Stop Bot", use_container_width=True)
    
    with st.expander("Bot Settings", expanded=False):
        with st.form("Settings", border=False):
            st.text_input("Buying Condition", 0.00)
            me = st.columns(2)
            with me[0]:
                st.text_input("Take Profit (%)", 0.00)
            with me[1]:
                st.text_input("Stop Loss (%)", 0.00)
            st.slider("Risk per trade (%)", 0, 100, status['risk'].iloc[-1])
            update_settings = st.form_submit_button(label='Update Settings', use_container_width=True)

    with st.expander("API Credentials", expanded=False):
        with st.form("API Keys", border=False):
            st.text_input("Enter API Key", status['apikey'].iloc[-1],type="password")
            st.text_input("Enter API Secret", status['apisecret'].iloc[-1],type='password')
            update_api_keys = st.form_submit_button(label='Update API Credentials', use_container_width=True)
        


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
        st.button("Close Position", use_container_width=True)
        st.metric(label="Current Price", value=current_price(), delta="")
        st.metric(label="Buy Price", value=current[0], delta="")
        st.metric(label="Take Profit", value=current[1], delta="")
        st.metric(label="Stop Loss", value=current[2], delta="")
