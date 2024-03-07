import logging
import json

from kiteconnect import KiteTicker

from ticker.BaseTicker import BaseTicker
from instruments.Instruments import Instruments
from models.TickData import TickData


class ZerodhaTicker(BaseTicker):
    def __init__(self):
        super().__init__("zerodha")

    def start_ticker(self):
        broker_app_details = self.broker_login.get_broker_app_details()
        access_token = self.broker_login.get_access_token()
        if access_token is None:
            logging.error(
                'ZerodhaTicker startTicker: Cannot start ticker as accessToken is empty')
            return

        ticker = KiteTicker(broker_app_details.app_key, access_token)
        ticker.on_connect = self.on_connect
        ticker.on_close = self.on_close
        ticker.on_error = self.on_error
        ticker.on_reconnect = self.on_reconnect
        ticker.on_noreconnect = self.on_noreconnect
        ticker.on_ticks = self.on_ticks
        ticker.on_order_update = self.on_order_update

        logging.info('ZerodhaTicker: Going to connect..')
        self.ticker = ticker
        self.ticker.connect(threaded=True)

    def stop_ticker(self):
        logging.info('ZerodhaTicker: stopping..')
        self.ticker.close(1000, "Manual close")

    def register_symbols(self, symbols):
        tokens = []
        for symbol in symbols:
            isd = Instruments.get_instrument_data_by_symbol(symbol)
            token = isd['instrument_token']
            logging.info(
                'ZerodhaTicker registerSymbol: %s token = %s', symbol, token)
            tokens.append(token)

        logging.info('ZerodhaTicker Subscribing tokens %s', tokens)
        self.ticker.subscribe(tokens)

    def unregister_symbols(self, symbols):
        tokens = []
        for symbol in symbols:
            isd = Instruments.get_instrument_data_by_symbol(symbol)
            token = isd['instrument_token']
            logging.info(
                'ZerodhaTicker unregisterSymbols: %s token = %s', symbol, token)
            tokens.append(token)

        logging.info('ZerodhaTicker Unsubscribing tokens %s', tokens)
        self.ticker.unsubscribe(tokens)

    def on_ticks(self, ws, broker_ticks):
        # convert broker specific Ticks to our system specific Ticks (models.TickData) and pass to super class function
        ticks = []
        for bTick in broker_ticks:
            isd = Instruments.get_instrument_data_by_token(
                bTick['instrument_token'])
            trading_symbol = isd['tradingsymbol']
            tick = TickData(trading_symbol)
            tick.last_traded_price = bTick['last_price']
            tick.last_traded_quantity = bTick['last_quantity']
            tick.avg_traded_price = bTick['average_price']
            tick.volume = bTick['volume']
            tick.total_buy_quantity = bTick['buy_quantity']
            tick.total_sell_quantity = bTick['sell_quantity']
            tick.open = bTick['ohlc']['open']
            tick.high = bTick['ohlc']['high']
            tick.low = bTick['ohlc']['low']
            tick.close = bTick['ohlc']['close']
            tick.change = bTick['change']
            ticks.append(tick)

        self.on_new_ticks(ticks)

    def on_connect(self, ws, response):
        self.onConnect()

    def on_close(self, ws, code, reason):
        self.onDisconnect(code, reason)

    def on_error(self, ws, code, reason):
        self.onError(code, reason)

    def on_reconnect(self, ws, attemptsCount):
        self.onReconnect(attemptsCount)

    def on_noreconnect(self, ws):
        self.onMaxReconnectsAttempt()

    def on_order_update(self, ws, data):
        self.onOrderUpdate(data)
