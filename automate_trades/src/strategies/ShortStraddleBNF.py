import logging
from datetime import datetime

from instruments.Instruments import Instruments
from models.Direction import Direction
from models.ProductType import ProductType
from strategies.BaseStrategy import BaseStrategy
from utils.Utils import Utils
from trademgmt.Trade import Trade
from trademgmt.TradeManager import TradeManager


# Each strategy has to be derived from BaseStrategy
class ShortStraddleBNF(BaseStrategy):
    __instance = None

    @staticmethod
    def get_instance():  # singleton class
        if ShortStraddleBNF.__instance is None:
            ShortStraddleBNF()
        return ShortStraddleBNF.__instance

    def __init__(self):
        if ShortStraddleBNF.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ShortStraddleBNF.__instance = self
        # Call Base class constructor
        super().__init__("ShortStraddleBNF")
        # Initialize all the properties specific to this strategy
        self.product_type = ProductType.MIS
        self.symbols = []
        self.sl_percentage = 30
        self.target_percentage = 0
        self.start_timestamp = Utils.get_time_of_day(11, 0,
                                                     0)  # When to start the strategy. Default is Market start time
        self.stop_timestamp = Utils.get_time_of_day(14, 0,
                                                    0)  # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = Utils.get_time_of_day(
            14, 30, 0)  # Square off time
        # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.capital = 100000
        self.leverage = 0
        # (1 CE + 1 PE) Max number of trades per day under this strategy
        self.max_trades_per_day = 2
        self.is_fno = True  # Does this strategy trade in FnO or not
        # Applicable if is_fno is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.capital_per_set = 100000

    def can_trade_today(self):
        # Even if you remove this function canTradeToday() completely its same as allowing trade every day
        return True

    def process(self):
        now = datetime.now()
        if now < self.start_timestamp:
            return
        if len(self.trades) >= self.max_trades_per_day:
            return

        # Get current market price of Nifty Future
        future_symbol = Utils.prepare_monthly_expiry_futures_symbol(
            'BANKNIFTY')
        quote = self.get_quote(future_symbol)
        if quote is None:
            logging.error('%s: Could not get quote for %s',
                          self.get_name(), future_symbol)
            return

        atm_strike = Utils.get_nearest_strike_price(
            quote.last_traded_price, 100)
        logging.info('%s: Nifty CMP = %f, ATMStrike = %d',
                     self.get_name(), quote.last_traded_price, atm_strike)

        atmce_symbol = Utils.prepare_weekly_options_symbol(
            "BANKNIFTY", atm_strike, 'CE')
        atmpe_symbol = Utils.prepare_weekly_options_symbol(
            "BANKNIFTY", atm_strike, 'PE')
        logging.info('%s: ATMCESymbol = %s, ATMPESymbol = %s',
                     self.get_name(), atmce_symbol, atmpe_symbol)
        # create trades
        self.generate_trades(atmce_symbol, atmpe_symbol)

    def generate_trades(self, atmce_symbol, atmpe_symbol):
        num_lots = self.calculate_lots_per_trade()
        quote_atmce_symbol = self.get_quote(atmce_symbol)
        quote_atmpe_symbol = self.get_quote(atmpe_symbol)
        if quote_atmce_symbol is None or quote_atmpe_symbol is None:
            logging.error(
                '%s: Could not get quotes for option symbols', self.get_name())
            return

        self.generate_trade(atmce_symbol, num_lots,
                            quote_atmce_symbol.last_traded_price)
        self.generate_trade(atmpe_symbol, num_lots,
                            quote_atmpe_symbol.last_traded_price)
        logging.info('%s: Trades generated.', self.get_name())

    def generate_trade(self, option_symbol, num_lots, last_traded_price):
        trade = Trade(option_symbol)
        trade.strategy = self.get_name()
        trade.is_options = True
        trade.direction = Direction.SHORT  # Always short here as option selling only
        trade.product_type = self.product_type
        trade.place_market_order = True
        trade.requested_entry = last_traded_price
        # setting this to strategy timestamp
        trade.timestamp = Utils.get_epoch(self.start_timestamp)

        isd = Instruments.get_instrument_data_by_symbol(
            option_symbol)  # Get instrument data to know qty per lot
        trade.qty = isd['lot_size'] * num_lots

        trade.stop_loss = Utils.round_to_nse_price(
            trade.requested_entry + trade.requested_entry * self.sl_percentage / 100)
        trade.target = 0  # setting to 0 as no target is applicable for this trade

        trade.intraday_square_off_timestamp = Utils.get_epoch(
            self.square_off_timestamp)
        # Hand over the trade to TradeManager
        TradeManager.add_new_trade(trade)

    def should_place_trade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if not super().should_place_trade(trade, tick):
            return False
        # We don't have any condition to be checked here for this strategy just return True
        return True

    def get_trailing_sl(self, trade):
        if trade is None:
            return 0
        if trade.entry == 0:
            return 0
        last_traded_price = TradeManager.get_last_traded_price(
            trade.tradingSymbol)
        if last_traded_price == 0:
            return 0

        trail_sl = 0
        profit_points = int(trade.entry - last_traded_price)
        if profit_points >= 5:
            factor = int(profit_points / 5)
            trail_sl = Utils.round_to_nse_price(
                trade.initial_stop_loss - factor * 5)
        logging.info('%s: %s Returning trail SL %f',
                     self.get_name(), trade.trading_symbol, trail_sl)
        return trail_sl
