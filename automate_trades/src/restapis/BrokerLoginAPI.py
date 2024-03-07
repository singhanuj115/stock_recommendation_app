from flask.views import MethodView
from flask import request, redirect

from core.Controller import Controller


class BrokerLoginAPI(MethodView):
    @staticmethod
    def get():
        redirect_url = Controller.handle_broker_login(request.args)
        return redirect(redirect_url, code=302)
