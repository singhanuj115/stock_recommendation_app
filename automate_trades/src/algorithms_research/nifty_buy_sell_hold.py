"""Class for Nifty buy sell hold"""
from collections import Counter
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from src.algorithms_research import fetch_nse_50_tickers, create_directory
from nsepy.history import get_history

from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


class BuySellHold:
    def __init__(self):
        self.tickers = None
        self.root_dir = "/Users/anujsingh/automate_trades/src/algorithms_research/"
        create_directory(self.root_dir + "data/")
        self.data_dir = "/Users/anujsingh/automate_trades/src/algorithms_research/data/"

    def get_data_from_nse(self, tickers, nse_directory):
        try:
            self.tickers = tickers
            create_directory(self.data_dir + nse_directory)

            start = dt.datetime.today() - dt.timedelta(100)
            end = dt.datetime.today()

            for ticker in self.tickers:
                print("Fetching the", ticker)
                if not os.path.exists(self.data_dir + nse_directory + '{}.csv'.format(ticker)):
                    try:
                        df_nse = get_history(symbol=ticker, start=start, end=end)
                        # df_nse = web.DataReader(ticker + ".NS", 'yahoo', start, end)
                    except Exception as e:
                        continue

                    df_nse.to_csv(self.data_dir + nse_directory + '{}.csv'.format(ticker))
                    print("Don't have {}".format(ticker))
                else:
                    print("Already have {}".format(ticker))
        except FileNotFoundError:
            return

    def compile_data(self, nse_directory):
        main_df = pd.DataFrame()

        for count, ticker in enumerate(self.tickers):
            df = pd.read_csv(self.data_dir + nse_directory + '{}.csv'.format(ticker))

            df.set_index('Date', inplace=True)

            columns_to_be_dropped = ['Symbol', 'Series', 'Prev Close', 'Open',
                                     'High', 'Low', 'Last', 'VWAP', 'Volume',
                                     'Turnover', 'Trades', 'Deliverable Volume',
                                     '%Deliverble']

            # columns_to_be_dropped = ['Open', 'High', 'Low', 'Volume', 'Close']

            df.rename(columns={'Close': ticker}, inplace=True)
            df.drop(columns=columns_to_be_dropped, axis=1, inplace=True)
            df.fillna(0, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')

            if count % 10 == 0:
                print(count)

        print(main_df.head())
        main_df.to_csv(self.data_dir + nse_directory + 'nifty50_joined_closes.csv')

    def visualize_data(self, nse_directory):
        df = pd.read_csv(self.data_dir + nse_directory + 'nifty50_joined_closes.csv')
        df_corr = df.corr()
        df_corr.to_csv(self.data_dir + 'corelation_data.csv')
        print(df_corr.head())

        data = df_corr.values
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        heatmap = ax.pcolor(data, cmap='Spectral')
        fig.colorbar(heatmap)
        ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
        ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)

        ax.invert_yaxis()
        ax.xaxis.tick_top()

        column_labels = df_corr.columns
        row_labels = df_corr.index

        ax.set_xticklabels(column_labels)
        ax.set_yticklabels(row_labels)
        plt.xticks(rotation=90)
        heatmap.set_clim(-1, 1)
        plt.tight_layout()
        plt.show()

    def process_data_for_labels(self, ticker):
        hm_days = 7
        df = pd.read_csv(self.data_dir + nse_directory + 'nifty50_joined_closes.csv', index_col=0)
        tickers = df.columns.values.tolist()
        df.fillna(0, inplace=True)

        for i in range(1, hm_days + 1):
            df['{}_{}d'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]

        df.fillna(0, inplace=True)
        return tickers, df

    @staticmethod
    def buy_sell_hold(*args):
        cols = [c for c in args]
        requirement = 0.030
        for col in cols:
            if col > requirement:
                return 1
            if col < -requirement:
                return -1
        return 0

    def extract_feature_sets(self, ticker):
        tickers, df = self.process_data_for_labels(ticker)

        df['{}_target'.format(ticker)] = list(map(self.buy_sell_hold,
                                                  df['{}_1d'.format(ticker)],
                                                  df['{}_2d'.format(ticker)],
                                                  df['{}_3d'.format(ticker)],
                                                  df['{}_4d'.format(ticker)],
                                                  df['{}_5d'.format(ticker)],
                                                  df['{}_6d'.format(ticker)],
                                                  df['{}_7d'.format(ticker)]))

        df.to_csv(self.data_dir + "exported_feature_sets.csv")

        values = df['{}_target'.format(ticker)].values.tolist()
        str_values = [str(i) for i in values]
        print('Data Spread: ', Counter(str_values))
        df.fillna(0, inplace=True)

        df = df.replace([np.inf, -np.inf], np.nan)
        df.dropna(inplace=True)

        df_vals = df[[ticker for ticker in tickers]]
        df_vals = df_vals.replace([np.inf, -np.inf], np.nan)
        df_vals.fillna(0, inplace=True)

        X = df_vals.values
        y = df['{}_target'.format(ticker)].values

        return X, y, df

    def do_ml(self, ticker):
        X, y, df = self.extract_feature_sets(ticker)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

        clf = RandomForestClassifier()

        estimator = [('LR',
                      LogisticRegression(solver='lbfgs',
                                         max_iter=80, multi_class="auto")),
                     ('SVC', SVC(gamma='auto', probability=True)), ('DTC', DecisionTreeClassifier())]

        #     clf = VotingClassifier(estimators = estimator, voting ='soft')

        clf.fit(X_train, y_train)

        confidence = clf.score(X_test, y_test)
        print("Accuracy", confidence)

        predictions = clf.predict(X_test)

        print("Predicted Spread: ", Counter(predictions))

        return confidence


nse_directory = "nse_data_50/"
tickers = fetch_nse_50_tickers()

buy_sell_hold_obj = BuySellHold()
# buy_sell_hold_obj.get_data_from_nse(tickers, nse_directory)
# buy_sell_hold_obj.compile_data(nse_directory)
# buy_sell_hold_obj.visualize_data(nse_directory)
buy_sell_hold_obj.do_ml("ADANIPORTS")
