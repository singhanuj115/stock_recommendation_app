import logging
import threading
import time

from instruments.Instruments import Instruments
from trademgmt.TradeManager import TradeManager

from strategies.SampleStrategy import SampleStrategy
from strategies.BNFORB30Min import BNFORB30Min
from strategies.OptionSelling import OptionSelling
from strategies.ShortStraddleBNF import ShortStraddleBNF


class Algo:
    is_algo_running = None

    @staticmethod
    def start_algo():
        if Algo.is_algo_running:
            logging.info("Algo has already started..")
            return

        logging.info("Starting Algo...")
        Instruments.fetch_instruments()

        # start trade manager in a separate thread
        tm = threading.Thread(target=TradeManager.run)
        tm.start()

        # sleep for 2 seconds for TradeManager to get initialized
        time.sleep(5)

        # start running strategies: Run each strategy in a separate thread
        threading.Thread(target=SampleStrategy.get_instance().run).start()
        # threading.Thread(target=BNFORB30Min.get_instance().run).start()
        # threading.Thread(target=OptionSelling.get_instance().run).start()
        # threading.Thread(target=ShortStraddleBNF.get_instance().run).start()

        Algo.is_algo_running = True
        logging.info("Algo started.")
