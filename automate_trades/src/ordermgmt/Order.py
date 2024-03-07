class Order:
    def __init__(self, order_input_params=None):
        self.trading_symbol = order_input_params.trading_symbol if order_input_params is not None else ""
        self.exchange = order_input_params.exchange if order_input_params is not None else "NSE"
        self.product_type = order_input_params.product_type if order_input_params is not None else ""
        self.order_type = order_input_params.order_type if order_input_params is not None else ""  # LIMIT/MARKET/SL-LIMIT/SL-MARKET
        self.price = order_input_params.price if order_input_params is not None else 0
        self.trigger_price = order_input_params.trigger_price if order_input_params is not None else 0  # Applicable in case of SL orders
        self.qty = order_input_params.qty if order_input_params is not None else 0
        self.order_id = None  # The order id received from broker after placing the order
        self.order_status = None  # One of the status defined in ordermgmt.OrderStatus
        self.average_price = 0  # Average price at which the order is filled
        self.filled_qty = 0  # Filled quantity
        self.pending_qty = 0  # Qty - Filled quantity
        self.order_place_timestamp = None  # Timestamp when the order is placed
        self.last_order_update_timestamp = None  # Applicable if you modify the order Ex: Trailing SL
        self.message = None  # In case any order rejection or any other error save the response from broker in this field

    def __str__(self):
        return "orderId=" + str(self.order_id) + ", orderStatus=" + str(self.order_status) \
               + ", symbol=" + str(self.trading_symbol) + ", productType=" + str(self.product_type) \
               + ", orderType=" + str(self.order_type) + ", price=" + str(self.price) \
               + ", triggerPrice=" + str(self.trigger_price) + ", qty=" + str(self.qty) \
               + ", filledQty=" + str(self.filled_qty) + ", pendingQty=" + str(self.pending_qty) \
               + ", averagePrice=" + str(self.average_price)
