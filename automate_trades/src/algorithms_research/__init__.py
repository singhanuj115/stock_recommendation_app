import chart_studio
import os
import pandas as pd


def fetch_nse_500_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/ind_nifty500list.csv')['Symbol'])
    return list_of_stock_codes


def fetch_nse_200_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/ind_nifty200list.csv')['Symbol'])
    return list_of_stock_codes


def fetch_nse_100_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/ind_nifty100list.csv')['Symbol'])
    return list_of_stock_codes


def fetch_nse_50_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/ind_nifty50list.csv')['Symbol'])
    return list_of_stock_codes


def fetch_nse_bank_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/niftybanklist.csv')['Symbol'])
    return list_of_stock_codes


def fetch_nse_pharma_tickers():
    list_of_stock_codes = list(pd.read_csv('nifty_list/niftypharmalist.csv')['Symbol'])
    return list_of_stock_codes


def create_directory(directory):
    # Create a directory if it does not exist.
    if not os.path.exists(directory):
        os.makedirs(directory)


def set_chart_studio_credentials():
    chart_studio.tools.set_credentials_file(username='Anuj8826', api_key='WyzvlYB6EYkp1sZ3ki2K')
