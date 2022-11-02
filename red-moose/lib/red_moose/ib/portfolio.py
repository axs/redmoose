import typing
import ib_insync
from red_moose.rm_types import ContractId, Symbol


class Portfolio:
    def __init__(self, *args, **kwargs):
        self.positions: typing.Dict[ContractId, ib_insync.Position] = dict()

    def addPosition(self, position: ib_insync.Position):
        if position.position == 0:
            self.positions.pop(position.contract.conId, None)
        else:
            self.positions[position.contract.conId] = position

    def getPosition(self, contract_id: ContractId) -> ib_insync.Position:
        return self.positions.get(contract_id)

    def hasContract(self, contract_id: ContractId) -> bool:
        # do we hold a position in this specific contract
        return contract_id in self.positions

    def hasUnderlying(self, underlying_symbol: Symbol) -> bool:
        """ used to determine if we have a position for a common underlying
            ie. pass in GOOG and will return true if hold GOOG or GOOG options
        Args:
            underlying_symbol:
        Returns:
              bool
        """
        return underlying_symbol in {o.contract.symbol for o in self.positions.values()}

    def handleExecution(self, trade: ib_insync.Trade):
        # ib_insync.OrderStatus.DoneStates
        pass
