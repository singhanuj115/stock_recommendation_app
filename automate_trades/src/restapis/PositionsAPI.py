from flask.views import MethodView
import json
import logging
from core.Controller import Controller


class PositionsAPI(MethodView):
    def get(self):
        broker_handle = Controller.get_broker_login().getBrokerHandle()
        positions = broker_handle.positions()
        logging.info('User positions => %s', positions)
        return json.dumps(positions)
