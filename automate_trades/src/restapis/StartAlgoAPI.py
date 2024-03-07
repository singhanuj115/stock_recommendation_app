from flask.views import MethodView
import json
import logging
import threading
from config.Config import get_system_config
from core.Algo import Algo


class StartAlgoAPI(MethodView):
    @staticmethod
    def post():
        # start algo in a separate thread
        x = threading.Thread(target=Algo.start_algo())
        x.start()
        system_config = get_system_config()
        home_url = system_config['homeUrl'] + '?algoStarted=true'
        logging.info('Sending redirect url %s in response', home_url)
        resp_data = {'redirect': home_url}
        return json.dumps(resp_data)
