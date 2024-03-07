import logging
from kiteconnect import KiteConnect

from config.Config import get_system_config
from loginmgmt.BaseLogin import BaseLogin


class ZerodhaLogin(BaseLogin):
    def __init__(self, broker_app_details):
        BaseLogin.__init__(self, broker_app_details)

    def login(self, args):
        logging.info('==> ZerodhaLogin .args => %s', args)
        system_config = get_system_config()
        broker_handle = KiteConnect(api_key=self.broker_app_details.app_key)
        if 'request_token' in args:
            request_token = args['request_token']
            logging.info('Zerodha requestToken = %s', request_token)
            session = broker_handle.generate_session(
                request_token, api_secret=self.broker_app_details.app_secret)

            access_token = session['access_token']
            access_token = access_token
            logging.info('Zerodha accessToken = %s', access_token)
            broker_handle.set_access_token(access_token)

            logging.info(
                'Zerodha Login successful. accessToken = %s', access_token)

            # set broker handle and access token to the instance
            self.set_broker_handle(broker_handle)
            self.set_access_token(access_token)

            # redirect to home page with query param loggedIn=true
            home_url = system_config['homeUrl'] + '?loggedIn=true'
            logging.info('Zerodha Redirecting to home page %s', home_url)
            redirect_url = home_url
        else:
            login_url = broker_handle.login_url()
            logging.info('Redirecting to zerodha login url = %s', login_url)
            redirect_url = login_url

        return redirect_url
