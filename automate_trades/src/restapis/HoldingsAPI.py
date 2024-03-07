from flask.views import MethodView
import json
import logging
from core.Controller import Controller


class HoldingsAPI(MethodView):
    def get(self):
        broker_handle = Controller.get_broker_login().get_broker_handle()
        holdings = broker_handle.holdings()
        logging.info('User holdings => %s', holdings)
        return json.dumps(holdings)
