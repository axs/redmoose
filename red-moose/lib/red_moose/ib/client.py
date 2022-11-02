import weakref
from random import randint
import typing

import ib_insync
from red_moose.common import Position
from red_moose.rm_enums import IBSecType

import logging

log = logging.getLogger(__name__)


class IBClient:
    def __init__(self, **kwargs):
        self._ib = ib_insync.IB()
        host = kwargs.get('host', '127.0.0.1')
        port = kwargs.get('port', 7497)
        clientId = kwargs.get('clientId', randint(9000, 9999))
        self._ib.connect(host, port, clientId=clientId)
        self._ib.reqMarketDataType(3)
        weakref.finalize(self, self._ib.disconnect)

    @property
    def ib(self):
        return self._ib

    def portfolio(self, **kwargs) -> typing.List[Position]:
        positions = []
        portfolio = self._ib.portfolio()
        for portfolio_item in portfolio:
            log.info(portfolio_item)
            # contract_details = self.ib.reqContractDetails(portfolio_item.contract)
            position = Position(account=portfolio_item.account,
                                quantity=portfolio_item.position,
                                sec_type=portfolio_item.contract.secType,
                                sec_id=portfolio_item.contract.secId,
                                sec_id_type=portfolio_item.contract.secIdType,
                                avg_cost=portfolio_item.averageCost,
                                market_value=portfolio_item.marketValue,
                                market_price=portfolio_item.marketPrice,
                                realized_pnl=portfolio_item.realizedPNL,
                                unrealized_pnl=portfolio_item.unrealizedPNL,
                                contract_id=portfolio_item.contract.conId
                                )
            positions.append(position)
        return positions

    def position_contracts(self) -> typing.Set[ib_insync.Contract]:
        """ need to set contract exchange explicitly so ReqMktData works
        Returns: a set of Contracts that portfolio holds
        """
        contracts = set()
        wanted = {IBSecType.STK.name, IBSecType.OPT.name}
        for portfolio_item in self._ib.portfolio():
            c = portfolio_item.contract
            if c.secType not in wanted:
                continue
            if c.secType == IBSecType.STK.name:
                c.exchange = "SMART"
            else:
                c.exchange = c.primaryExchange
            contracts.add(c)
        return contracts
