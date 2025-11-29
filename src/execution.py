from .config import Config

class OrderExecutor:
    def __init__(self, client=None):
        self.client = client
        self.env = Config.ENV

    def execute_order(self, instrument, units, stop_loss=None, take_profit=None):
        """
        Execute an order.
        If ENV is 'mock' or client is None, print to stdout.
        """
        if self.env == "mock" or self.client is None:
            print(f"[MOCK EXECUTION] Order: {instrument} Units: {units} SL: {stop_loss} TP: {take_profit}")
            return {"id": "mock_order_id", "instrument": instrument, "units": units}
        
        # Real API call would go here
        # data = {
        #     "order": {
        #         "instrument": instrument,
        #         "units": str(units),
        #         "type": "MARKET",
        #         "positionFill": "DEFAULT"
        #     }
        # }
        # ...
        print(f"[REAL EXECUTION] Not implemented yet for safety. Order: {instrument} Units: {units}")
        return {}
