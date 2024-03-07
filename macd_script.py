import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import datetime as dt

# Fetch Nifty 50 tickers
def fetch_nifty_50_tickers():
    nifty_50_tickers = ['AAPL', 'MSFT']  # Replace with Nifty 50 tickers
    return nifty_50_tickers

# Fetch stock data for Nifty 50 tickers
def fetch_stock_data(tickers, start, end):
    stock_data = yf.download(tickers, start=start, end=end)
    return stock_data['Adj Close']

# Calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    macd = data.ewm(span=short_window, min_periods=short_window, adjust=False).mean() - \
           data.ewm(span=long_window, min_periods=long_window, adjust=False).mean()
    signal = macd.ewm(span=signal_window, min_periods=signal_window, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# Plot MACD graph
def plot_macd(ticker, data, macd, signal, histogram):
    fig = go.Figure()

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'))

    # MACD Line
    fig.add_trace(go.Scatter(x=data.index, y=macd, mode='lines', name='MACD Line'))

    # Signal Line
    fig.add_trace(go.Scatter(x=data.index, y=signal, mode='lines', name='Signal Line'))

    # Histogram
    fig.add_trace(go.Bar(x=data.index, y=histogram, name='Histogram'))

    fig.update_layout(title=f'MACD Analysis for {ticker}',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=True)

    fig.show()

# Main function
def main():
    start_date = dt.datetime.today() - dt.timedelta(365)  # 1 year of data
    end_date = dt.datetime.today()

    nifty_50_tickers = fetch_nifty_50_tickers()
    for ticker in nifty_50_tickers:
        stock_data = fetch_stock_data(ticker, start_date, end_date)
        macd, signal, histogram = calculate_macd(stock_data)
        plot_macd(ticker, stock_data, macd, signal, histogram)

if __name__ == "__main__":
    main()
