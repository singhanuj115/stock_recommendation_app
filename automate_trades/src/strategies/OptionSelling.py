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
class OptionSelling(BaseStrategy):
    __instance = None

    @staticmethod
    def get_instance():  # singleton class
        if OptionSelling.__instance is None:
            OptionSelling()
        return OptionSelling.__instance

    def __init__(self):
        if OptionSelling.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            OptionSelling.__instance = self
        # Call Base class constructor
        super().__init__("OptionSelling")
        # Initialize all the properties specific to this strategy
        self.product_type = ProductType.MIS
        self.symbols = []
        self.sl_percentage = 50
        self.target_percentage = 0
        self.start_timestamp = Utils.get_time_of_day(9, 30,
                                                     0)  # When to start the strategy. Default is Market start time
        self.stop_timestamp = Utils.get_time_of_day(14, 30,
                                                    0)  # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.square_off_timestamp = Utils.get_time_of_day(
            15, 15, 0)  # Square off time
        # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.capital = 100000
        self.leverage = 0
        # (1 CE + 1 PE) Max number of trades per day under this strategy
        self.max_trades_per_day = 2
        self.is_fno = True  # Does this strategy trade in FnO or not
        # Applicable if is_fno is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.capital_per_set = 100000

    def canTradeToday(self):
        if Utils.is_today_one_day_before_weekly_expiry_day():
            logging.info('%s: Today is one day before weekly expiry date hence going to trade this strategy',
                         self.get_name())
            return True
        if Utils.is_today_weekly_expiry_day():
            logging.info(
                '%s: Today is weekly expiry day hence going to trade this strategy today', self.get_name())
            return True
        logging.info(
            '%s: Today is neither day before expiry nor expiry day. Hence NOT going to trade this strategy today',
            self.get_name())
        return False

    def process(self):
        now = datetime.now()
        if now < self.start_timestamp:
            return
        if len(self.trades) >= self.max_trades_per_day:
            return

        # Get current market price of Nifty Future
        future_symbol = Utils.prepare_monthly_expiry_futures_symbol('NIFTY')
        quote = self.get_quote(future_symbol)
        if quote is None:
            logging.error('%s: Could not get quote for %s',
                          self.get_name(), future_symbol)
            return

        atm_strike = Utils.get_nearest_strike_price(
            quote.last_traded_price, 50)
        logging.info('%s: Nifty CMP = %f, ATMStrike = %d',
                     self.get_name(), quote.last_traded_price, atm_strike)

        atm_plus50_ce_symbol = Utils.prepare_weekly_options_symbol(
            "NIFTY", atm_strike + 50, 'CE')
        atm_minus50_pe_symbol = Utils.prepare_weekly_options_symbol(
            "NIFTY", atm_strike - 50, 'PE')
        logging.info('%s: ATMPlus50CE = %s, ATMMinus50PE = %s', self.get_name(), atm_plus50_ce_symbol,
                     atm_minus50_pe_symbol)
        # create trades
        self.generate_trades(atm_plus50_ce_symbol, atm_minus50_pe_symbol)

    def generate_trades(self, atm_plus50_ce_symbol, atm_minus50_pe_symbol):
        num_lots = self.calculate_lots_per_trade()
        quote_atm_plus50_ce_symbol = self.get_quote(atm_plus50_ce_symbol)
        quote_atm_minus50_pe_symbol = self.get_quote(atm_minus50_pe_symbol)
        if quote_atm_plus50_ce_symbol is None or quote_atm_minus50_pe_symbol is None:
            logging.error(
                '%s: Could not get quotes for option symbols', self.get_name())
            return

        self.generate_trade(atm_plus50_ce_symbol, num_lots,
                            quote_atm_plus50_ce_symbol.last_traded_price)
        self.generate_trade(atm_minus50_pe_symbol, num_lots,
                            quote_atm_minus50_pe_symbol.last_traded_price)
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
