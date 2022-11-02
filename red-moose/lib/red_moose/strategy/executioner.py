import abc
import logging
import weakref

import numpy as np
from ib_insync import IB, LimitOrder, Contract

from red_moose.ib.oms import OrderManager
from red_moose.rm_enums import Side

log = logging.getLogger(__name__)


class Strategy(abc.ABC):
    def __init__(self, ib: IB):
        self.ib = ib
        self.oms = OrderManager()
        self.ib.execDetailsEvent += self.onFill
        self.ib.orderStatusEvent += self.onOrderStatus
        weakref.finalize(self, self.cancelOrders)

    def onFill(self, *args):
        log.info(args)

    def onOrderStatus(self, trade):
        log.info(trade)
        self.oms.addOrder(trade)

    def cancelOrders(self):
        for trade in self.oms.orders.values():
            try:
                print('')
                log.info(f"cancelling {trade}")
                print(f"cancelling {trade}")
                self.ib.cancelOrder(trade.order)
            except Exception as e:
                print(e)
                log.exception(e)

    @abc.abstractmethod
    def execute(self):
        pass


class ClosePosition(Strategy):
    """
    import ib_insync

    ib = IB()
    ib.connect(clientId=0)
    c = ClosePosition(Side.BUY, 1232, 63.23, 62.89, Stock('XLU', exchange='ARCA', currency='USD'), ib)
    c.execute()
    ib.run()
    """

    def __init__(self,
                 action: Side,
                 account: str,
                 totalQuantity,
                 topPrice,
                 bottomPrice,
                 contract: Contract,
                 ib: IB,
                 **kwargs):
        self.action = action
        self.account = account
        self.totalQuantity = totalQuantity
        self.topPrice = topPrice
        self.bottomPrice = bottomPrice
        self.contract = contract
        self.chunks = kwargs.get('chunks', 5)
        super().__init__(ib)

    def execute(self):
        for qty, price in zip(self.randomize_qty(), self.scale_prices()):
            o = LimitOrder(self.action.name, qty, price, account=self.account)
            self.ib.placeOrder(self.contract, o)

    def randomize_qty(self):
        weights = np.random.random(self.chunks)
        weights /= weights.sum()
        random_qty = np.round(self.totalQuantity * weights)
        rs = random_qty.sum()
        if rs < self.totalQuantity:
            random_qty[0] += 1
        elif rs > self.totalQuantity:
            random_qty[0] -= 1
        assert random_qty.sum() == self.totalQuantity
        return random_qty

    def scale_prices(self):
        return np.linspace(self.topPrice, self.bottomPrice, self.chunks).round(2)
