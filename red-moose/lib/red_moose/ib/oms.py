import typing
import ib_insync
from red_moose.rm_types import OrderId, ContractId, Symbol


class OrderManager:
    def __init__(self, *args, **kwargs):
        self.orders: typing.Dict[OrderId, ib_insync.Trade] = dict()

    def addOrder(self, trade: ib_insync.Trade):
        if trade.orderStatus.status in ib_insync.OrderStatus.DoneStates:
            self.orders.pop(trade.order.permId, None)
        else:
            self.orders[trade.order.permId] = trade

    def getOrder(self, order_id: OrderId) -> ib_insync.Trade:
        return self.orders.get(order_id)

    def hasContract(self, contract_id: ContractId) -> bool:
        # do we hold a position in this specific contract
        return contract_id in {o.contract.conId for o in self.orders.values()}

    def hasUnderlying(self, underlying_symbol: Symbol) -> bool:
        """ used to determine if we have a position for a common underlying
            ie. pass in GOOG and will return true if hold GOOG or GOOG options
        Args:
            underlying_symbol:
        Returns:
              bool
        """
        return underlying_symbol in {o.contract.symbol for o in self.orders.values()}
