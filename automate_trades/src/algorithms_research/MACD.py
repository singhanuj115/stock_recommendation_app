"""Class for MACD buy sell hold"""
import datetime as dt
import pandas_datareader.data as web

from src.algorithms_research import fetch_nse_50_tickers


class MACD:
    def __init__(self, tickers):
        self.tickers = [ticker + ".NS" for ticker in tickers]
        self.adj_close_df = None

    def get_nse_data(self):
        start = dt.datetime.today() - dt.timedelta(100)
        end = dt.datetime.today()

        stock_nse_df = web.DataReader(self.tickers, 'yahoo', start, end)
        self.adj_close_df = stock_nse_df['Adj Close']

    def create_macd_metrics(self):
        for stock_index in self.adj_close_df.columns:
            self.adj_close_df[stock_index + "_MA_Fast"] = self.adj_close_df[stock_index].ewm(span=12,
                                                                                             min_periods=12).mean()
            self.adj_close_df[stock_index + "_MA_Slow"] = self.adj_close_df[stock_index].ewm(span=26,
                                                                                             min_periods=26).mean()
            self.adj_close_df[stock_index + "_MACD"] = self.adj_close_df[stock_index + "_MA_Fast"] - self.adj_close_df[
                stock_index + "_MA_Slow"]
            self.adj_close_df[stock_index + "_Signal"] = self.adj_close_df[stock_index + "_MACD"].ewm(span=9,
                                                                                                      min_periods=9).mean()
            self.adj_close_df[stock_index + '_SMA_10'] = self.adj_close_df[stock_index].rolling(window=10).mean()


tickers = fetch_nse_50_tickers()
macd_obj = MACD(tickers)
