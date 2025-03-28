import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
import numpy as np
import datetime as dt
import numba

# For interactive plots (optional)
#import plotly.graph_objects as go

# Todos:
# - Implement more tickers belonging to diff. market classes (Value vs. Growth)
# - Implement AI API and fetch more data such as current market sentiment, analysis for last week/month/quarter etc.
# - Implement Dashboards such as current market analysis, next week/month/quarter forecasts, strategy analysis, risk management etc.
# - Find/implement more Trading Stategies and automatically backtest them
# - Build a dockerized AI trading infrastructure (running 24/7 with market and risk dashboards, and automated trading execution functionalities)

def prepare_signals(data, short_window, period_RSI):
    # Calculate 1-day returns
    data['Daily_Returns'] = data['Close'].pct_change(1)
    data['Var'] = data['Close'].rolling(window=short_window).var()

    data['Diff'] = data['Close'].diff()
    data['Gain'] = data.Diff.mask(data.Diff < 0, 0.0)
    data['Loss'] = -data.Diff.mask(data.Diff > 0, -0.0)

    # Calculate RSI
    # Avg. losses and gains for length = period_RSIs
    data['AVG_gain'] = rma(data.Gain.to_numpy(), period_RSI)
    data['AVG_loss'] = rma(data.Loss.to_numpy(), period_RSI)

    #df['rs'] = df.avg_gain / df.avg_loss
    #df['rsi'] = 100 - (100 / (1 + df.rs))

    data['RSI'] = 100.0 - (100.0 / (1.0 + data.AVG_gain / data.AVG_loss ))
    data['RSI_Returns'] = data['RSI'].pct_change(1)

    # Bollinger Bands
    # Todo implement 10 period Bollinger where period \in (minute, hour, day)
    data['20 Day MA'] = data['Close'].rolling(window=20).mean()
    data['20 Day STD'] = data['Close'].rolling(window=20).std()
    data['Upper Band'] = data['20 Day MA'] + (data['20 Day STD'] * 2)
    data['Lower Band'] = data['20 Day MA'] - (data['20 Day STD'] * 2)

    # Simple Moving Averages
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()

    # Exponential Moving Averages
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

    # Moving Average Convergence Divergence
    data['MACD_line'] = data['EMA_12'] - data['EMA_26']
    data['Signal_line'] = data['MACD_line'].ewm(span=9, adjust=False).mean()
    data['MACD_Hist'] = data['MACD_line'] - data['Signal_line']

    return data

def strategy_bollinger_hold(data, short_window, long_window):
    # Generate trading signals
    data['Signal'] = 0

    data['Close 1d'] = data['Close'].rolling(window=1).mean()
    data.loc[data['Close 1d'] > data['Upper Band'], 'Signal'] = -1
    data.loc[data['Close 1d'] < data['Lower Band'], 'Signal'] = 1

    # Buy stock after first buy signal and hold until sell signal
    signal_change = 0

    for index, row in data.iterrows():
        if row['Signal'].values[0] == 1:
            if signal_change == 0:
                signal_change = 1
                print(signal_change)
                print(f"Buy signal on date: {index}")
        elif row['Signal'].values[0] == -1:
            if signal_change == 1:
                signal_change = 0
                print(signal_change)
                print(f"Sell signal on date: {index}")
        if signal_change == 1:
            data.loc[index,"Signal"] = 1

    print(f"Number of holding days: {len(data.loc[data["Signal"] == 1])}")

    # Generate trading orders
    data['Position'] = data['Signal'].diff()

    # Calculate returns
    data['Returns'] = data['Close'].pct_change().dropna()
    data['Strategy_Returns'] = data['Signal'].shift(1) * data['Returns'].dropna()

    return data

def strategy_bollinger(data, short_window, long_window):
    # Generate trading signals
    data['Signal'] = 0

    data['Close 1d'] = data['Close'].rolling(window=1).mean()
    data.loc[data['Close 1d'] > data['Upper Band'], 'Signal'] = -1
    data.loc[data['Close 1d'] < data['Lower Band'], 'Signal'] = 1

    # Generate trading orders
    data['Position'] = data['Signal'].diff()

    # Calculate returns
    data['Returns'] = data['Close'].pct_change().dropna()
    data['Strategy_Returns'] = data['Signal'].shift(1) * data['Returns'].dropna()

    return data

def strategy_moving_averages(data, short_window, long_window):
    # Calculate short and long moving averages
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()

    # Generate trading signals
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1
    data.loc[data['Short_MA'] < data['Long_MA'], 'Signal'] = -1

    # Generate trading orders
    data['Position'] = data['Signal'].diff()

    # Calculate returns
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Signal'].shift(1) * data['Returns']

    return data

def rma(x, n):
    """Running moving average"""
    a = np.full_like(x, np.nan)
    a[n] = x[1:n+1].mean()
    for i in range(n+1, len(x)):
        a[i] = (a[i-1] * (n - 1) + x[i]) / n
    return a

if __name__ == '__main__':
    # Time parameters for trading strategy
    # Todo: Implement trading singlas for various periods \in (minute, hour, day) and optimize by ML
    period_length = "15m" #not used yet, currenty YF data is only daily
    period_RSI = 10 # No. of days used for RSI calculation
    period_lag = 5 # Not used yet (Q: Is there an optimal lag duration when trades should be executed?)

    # Define cut off point for trading strategy
    max_abs_return = 0.1 #not used yet

    # Define the ticker symbol
    ticker = 'BTC-USD'

    # Fetch historical data starting from January 1, 2020
    ticker_data = yf.download(ticker, start='2020-01-01', end='2025-03-06', interval='1d')

    # Display the first few rows of the data
    print(ticker_data.head())

    # Set the short and long windows
    short_window = 50 #should be equal to period_RSI?
    long_window = 200

    # Prepare signals
    signal_data = prepare_signals(ticker_data, short_window, period_RSI)

    # Print the first few rows including signal results
    print(signal_data.head())

    # Plot signals
    plt.figure(figsize=(12, 8))
    plt.plot(signal_data['Close'], label='Closing Price', color='blue')
    plt.plot(signal_data['20 Day MA'], label='20 Day MA', color='red')
    plt.plot(signal_data['Upper Band'], label='Upper Band', color='grey')
    plt.plot(signal_data['Lower Band'], label='Lower Band', color='grey')
    plt.plot(signal_data['SMA_10'], label='10 Day SMA', color='green')
    plt.plot(signal_data['SMA_50'], label='50 Day SMA', color='orange')
    plt.plot(signal_data['SMA_200'], label='200 Day SMA', color='violet')
    plt.title('Bollinger Bands and Simple Moving Averages for ' + ticker)
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot Exponential Moving Averages
    plt.figure(figsize=(12, 8))
    plt.plot(signal_data['Close'], label='Closing Price', color='blue')
    plt.plot(signal_data['EMA_12'], label='12 Day EMA', color='red')
    plt.plot(signal_data['EMA_26'], label='26 Day EMA', color='green')
    plt.title('Exponential Moving Averages for ' + ticker)
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.show()

    # Plot Moving Average Convergence Divergence
    plt.figure(figsize=(12, 8))
    plt.plot(signal_data['MACD_line'], label='MACD Line', color='red')
    plt.plot(signal_data['Signal_line'], label='Signal Line', color='blue')
    plt.bar(signal_data.index, signal_data['MACD_Hist'], label='MACD Histogram', color='grey')
    plt.title('Moving Average Convergence Divergence for ' + ticker)
    plt.legend()
    plt.show()

    # Apply a hold strategy where one stock of S is bought when S > Lower Band
    # The stock is hold until S > Higher Band
    signal_data = strategy_bollinger_hold(signal_data, short_window, long_window)
    #print(signal_data[signal_data['Signal'] < 0]['Upper Band'])
    #print(signal_data[signal_data['Signal'] < 0]['Close'])

    # Calculate cumulative returns
    signal_data['Cumulative_Returns'] = (1 + signal_data['Returns']).cumprod()
    signal_data['Cumulative_Strategy_Returns'] = (1 + signal_data['Strategy_Returns']).cumprod()

    # Calculate and print the overall returns
    overall_returns = signal_data['Cumulative_Returns'].iloc[-1] - 1
    strategy_returns = signal_data['Cumulative_Strategy_Returns'].iloc[-1] - 1

    print(f"Overall returns: {overall_returns:.2%}")
    print(f"Strategy returns: {strategy_returns:.2%}")


    # Compare strategies
    plt.figure(figsize=(12, 8))
    plt.plot(signal_data.index, signal_data['Cumulative_Returns'], label='Buy and Hold')
    plt.plot(signal_data.index, signal_data['Cumulative_Strategy_Returns'], label='MA Crossover Strategy')
    plt.title('BTC-USD Trading Strategy: Buy and Hold vs "Bollinger Hold"')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Sanity checks for 2025 subperiod in data (see if signals work by comparing, e.g., to tradingview)
    signal_data = signal_data[signal_data.index.year == 2025]

    # Calculate moments
    print(signal_data['RSI'].mean()) #.reset_index(drop=True)
    signal_data['RSI_Var'] = signal_data['RSI'].rolling(window=5).var()
    #print(s.mean(), s.var(ddof=1), s.skew(), s.kurtosis())

    # Find days where RSI variance was gt 60
    print(signal_data[signal_data['RSI_Var']>60])

    # Plot RSI return and variance
    plt.figure(figsize=(12, 8))
    plt.plot(signal_data.index, signal_data['RSI_Returns']*10, label='RSI Returns')
    plt.plot(signal_data.index, signal_data['RSI_Var'], label='RSI 5-day Var')
    plt.title('BTC-USD: Daily RSI Return and Variance')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.legend()
    plt.grid(True)
    plt.show()
