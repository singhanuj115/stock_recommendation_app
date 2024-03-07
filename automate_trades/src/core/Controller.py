import logging

from config.Config import get_broker_app_config
from models.BrokerAppDetails import BrokerAppDetails
from loginmgmt.ZerodhaLogin import ZerodhaLogin


class Controller:
    broker_login = None  # static variable
    broker_name = None  # static variable

    @staticmethod
    def handle_broker_login(args):
        broker_app_config = get_broker_app_config()

        broker_app_details = BrokerAppDetails(broker_app_config['broker'])
        broker_app_details.set_client_id(broker_app_config['clientID'])
        broker_app_details.set_app_key(broker_app_config['appKey'])
        broker_app_details.set_app_secret(broker_app_config['appSecret'])

        logging.info('handleBrokerLogin app_key %s',
                     broker_app_details.app_key)
        Controller.broker_name = broker_app_details.broker
        if Controller.broker_name == 'zerodha':
            Controller.broker_login = ZerodhaLogin(broker_app_details)
        # Other brokers - not implemented
        # elif Controller.brokerName == 'fyers':
        # Controller.brokerLogin = FyersLogin(brokerAppDetails)

        redirect_url = Controller.broker_login.login(args)
        return redirect_url

    @staticmethod
    def get_broker_login():
        return Controller.broker_login

    @staticmethod
    def get_broker_name():
        return Controller.broker_name
