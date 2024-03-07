import math
import uuid
import time
import logging
import calendar
from datetime import datetime, timedelta

from config.Config import get_holidays
from models.Direction import Direction
from trademgmt.TradeState import TradeState


class Utils:
    date_format = "%Y-%m-%d"
    time_format = "%H:%M:%S"
    date_time_format = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def round_off(price):  # Round off to 2 decimal places
        return round(price, 2)

    @staticmethod
    def round_to_nse_price(price):
        x = round(price, 2) * 20
        y = math.ceil(x)
        return y / 20

    @staticmethod
    def is_market_open():
        if Utils.is_today_holiday():
            return False
        now = datetime.now()
        market_start_time = Utils.get_market_start_time()
        market_end_time = Utils.get_market_end_time()
        return market_start_time <= now <= market_end_time

    @staticmethod
    def is_market_closed_for_the_day():
        # This method returns true if the current time is > marketEndTime
        # Please note this will not return true if current time is < marketStartTime on a trading day
        if Utils.is_today_holiday():
            return True
        now = datetime.now()
        market_end_time = Utils.get_market_end_time()
        return now > market_end_time

    @staticmethod
    def wait_till_market_opens(context):
        now_epoch = Utils.get_epoch(datetime.now())
        market_start_time_epoch = Utils.get_epoch(
            Utils.get_market_start_time())
        wait_seconds = market_start_time_epoch - now_epoch
        if wait_seconds > 0:
            logging.info(
                "%s: Waiting for %d seconds till market opens...", context, wait_seconds)
            time.sleep(wait_seconds)

    @staticmethod
    def get_epoch(datetime_obj=None):
        # This method converts given datetimeObj to epoch seconds
        if datetime_obj is None:
            datetime_obj = datetime.now()
        epoch_seconds = datetime.timestamp(datetime_obj)
        return int(epoch_seconds)  # converting double to long

    @staticmethod
    def get_market_start_time(date_time_obj=None):
        return Utils.get_time_of_day(9, 15, 0, date_time_obj)

    @staticmethod
    def get_market_end_time(date_time_obj=None):
        return Utils.get_time_of_day(15, 30, 0, date_time_obj)

    @staticmethod
    def get_time_of_day(hours, minutes, seconds, date_time_obj=None):
        if date_time_obj is None:
            date_time_obj = datetime.now()
        date_time_obj = date_time_obj.replace(
            hour=hours, minute=minutes, second=seconds, microsecond=0)
        return date_time_obj

    @staticmethod
    def get_time_of_to_day(hours, minutes, seconds):
        return Utils.get_time_of_day(hours, minutes, seconds, datetime.now())

    @staticmethod
    def get_today_date_str():
        return Utils.convert_to_date_str(datetime.now())

    @staticmethod
    def convert_to_date_str(datetime_obj):
        return datetime_obj.strftime(Utils.date_format)

    @staticmethod
    def is_holiday(datetime_obj):
        day_of_week = calendar.day_name[datetime_obj.weekday()]
        if day_of_week == 'Saturday' or day_of_week == 'Sunday':
            return True

        date_str = Utils.convert_to_date_str(datetime_obj)
        holidays = get_holidays()
        if date_str in holidays:
            return True
        else:
            return False

    @staticmethod
    def is_today_holiday():
        return Utils.is_holiday(datetime.now())

    @staticmethod
    def generate_trade_id():
        return str(uuid.uuid4())

    @staticmethod
    def calculate_trade_pnl(trade):
        if trade.trade_state == TradeState.ACTIVE:
            if trade.cmp > 0:
                if trade.direction == Direction.LONG:
                    trade.pnl = Utils.round_off(
                        trade.filled_qty * (trade.cmp - trade.entry))
                else:
                    trade.pnl = Utils.round_off(
                        trade.filled_qty * (trade.entry - trade.cmp))
        else:
            if trade.exit > 0:
                if trade.direction == Direction.LONG:
                    trade.pnl = Utils.round_off(
                        trade.filled_qty * (trade.exit - trade.entry))
                else:
                    trade.pnl = Utils.round_off(
                        trade.filled_qty * (trade.entry - trade.exit))
        trade_value = trade.entry * trade.filled_qty
        if trade_value > 0:
            trade.pnl_percentage = Utils.round_off(
                trade.pnl * 100 / trade_value)
        return trade

    @staticmethod
    def prepare_monthly_expiry_futures_symbol(input_symbol):
        expiry_date_time = Utils.get_monthly_expiry_day_date()
        expiry_date_market_end_time = Utils.get_market_end_time(
            expiry_date_time)
        now = datetime.now()
        if now > expiry_date_market_end_time:
            # increasing today date by 20 days to get some day in next month passing to getMonthlyExpiryDayDate()
            expiry_date_time = Utils.get_monthly_expiry_day_date(
                now + timedelta(days=20))
        year2_digits = str(expiry_date_time.year)[2:]
        month_short = calendar.month_name[expiry_date_time.month].upper()[0:3]
        future_symbol = input_symbol + year2_digits + month_short + 'FUT'
        logging.info(
            'prepareMonthlyExpiryFuturesSymbol[%s] = %s', input_symbol, future_symbol)
        return future_symbol

    @staticmethod
    def prepare_weekly_options_symbol(input_symbol, strike, option_type, num_weeks_plus=0):
        expiry_date_time = Utils.get_weekly_expiry_day_date()
        today_market_start_time = Utils.get_market_start_time()
        expiry_day_market_end_time = Utils.get_market_end_time(
            expiry_date_time)
        if num_weeks_plus > 0:
            expiry_date_time = expiry_date_time + \
                timedelta(days=num_weeks_plus * 7)
            expiry_date_time = Utils.get_weekly_expiry_day_date(
                expiry_date_time)
        if today_market_start_time > expiry_day_market_end_time:
            expiry_date_time = expiry_date_time + timedelta(days=6)
            expiry_date_time = Utils.get_weekly_expiry_day_date(
                expiry_date_time)
        # Check if monthly and weekly expiry same
        expiry_date_time_monthly = Utils.get_monthly_expiry_day_date()
        year2_digits = False
        if expiry_date_time == expiry_date_time_monthly:
            week_and_month_expiry_same = True
            logging.info(
                'Weekly and Monthly expiry is same for %s', expiry_date_time)
        year2_digits = str(expiry_date_time.year)[2:]
        option_symbol = None
        if week_and_month_expiry_same:
            month_short = calendar.month_name[expiry_date_time.month].upper()[
                0:3]
            option_symbol = input_symbol + \
                str(year2_digits) + month_short + \
                str(strike) + option_type.upper()
        else:
            m = expiry_date_time.month
            d = expiry_date_time.day
            m_str = str(m)
            if m == 10:
                m_str = "O"
            elif m == 11:
                m_str = "N"
            elif m == 12:
                m_str = "D"
            d_str = ("0" + str(d)) if d < 10 else str(d)
            option_symbol = input_symbol + \
                str(year2_digits) + m_str + d_str + \
                str(strike) + option_type.upper()
        logging.info('prepareWeeklyOptionsSymbol[%s, %d, %s, %d] = %s', input_symbol, strike, option_type, num_weeks_plus,
                     option_symbol)
        return option_symbol

    @staticmethod
    def get_monthly_expiry_day_date(datetime_obj=None):
        if datetime_obj is None:
            datetime_obj = datetime.now()
        year = datetime_obj.year
        month = datetime_obj.month
        # 2nd entry is the last day of the month
        last_day = calendar.monthrange(year, month)[1]
        datetime_expiry_day = datetime(year, month, last_day)
        while calendar.day_name[datetime_expiry_day.weekday()] != 'Thursday':
            datetime_expiry_day = datetime_expiry_day - timedelta(days=1)
        while Utils.is_holiday(datetime_expiry_day):
            datetime_expiry_day = datetime_expiry_day - timedelta(days=1)

        datetime_expiry_day = Utils.get_time_of_day(
            0, 0, 0, datetime_expiry_day)
        return datetime_expiry_day

    @staticmethod
    def get_weekly_expiry_day_date(date_time_obj=None):
        if date_time_obj is None:
            date_time_obj = datetime.now()
        days_to_add = 0
        if date_time_obj.weekday() >= 3:
            days_to_add = -1 * (date_time_obj.weekday() - 3)
        else:
            days_to_add = 3 - date_time_obj.weekday()
        datetime_expiry_day = date_time_obj + timedelta(days=days_to_add)
        while Utils.is_holiday(datetime_expiry_day):
            datetime_expiry_day = datetime_expiry_day - timedelta(days=1)

        datetime_expiry_day = Utils.get_time_of_day(
            0, 0, 0, datetime_expiry_day)
        return datetime_expiry_day

    @staticmethod
    def is_today_weekly_expiry_day():
        expiry_date = Utils.get_weekly_expiry_day_date()
        today_date = Utils.get_time_of_day(0, 0, 0)
        if expiry_date == today_date:
            return True
        return False

    @staticmethod
    def is_today_one_day_before_weekly_expiry_day():
        expiry_date = Utils.get_weekly_expiry_day_date()
        today_date = Utils.get_time_of_day(0, 0, 0)
        if expiry_date - timedelta(days=1) == today_date:
            return True
        return False

    @staticmethod
    def get_nearest_strike_price(price, nearest_multiple=50):
        input_price = int(price)
        remainder = int(input_price % nearest_multiple)
        if remainder < int(nearest_multiple / 2):
            return input_price - remainder
        else:
            return input_price + (nearest_multiple - remainder)
