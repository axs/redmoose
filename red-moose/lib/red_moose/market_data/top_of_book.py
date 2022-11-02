import logging
import typing

import ib_insync

from red_moose.common import Singleton, Quote, ISubscription
from red_moose.ib.client import IBClient
from red_moose.rm_collections import ObservableDict
from red_moose.rm_types import BookListener, Symbol

log = logging.getLogger(__name__)


class TopOfBook(ISubscription):
    def __init__(self):
        self._book = ObservableDict()

    def subscribe(self, listener: BookListener):
        self._book.subscribe_to_setitem(listener)

    def unsubscribe(self, listener: BookListener):
        self._book.unsubscribe_from_setitem(listener)

    def addQuote(self, quote: Quote):
        """ only set quote if price of bid/ask changed
        IQFeed symbol is numpy bytes from pyiqfeed lib
        Args:
            quote:
        """
        if quote.Symbol in self._book and quote.bid_ask_changed(self._book[quote.Symbol]):
            self._book[quote.Symbol] = quote
        else:
            self._book[quote.Symbol] = quote

    def getQuote(self, symbol: Symbol) -> Quote:
        return self._book.get(symbol)

    def subscribe_decorator(self, listener: BookListener):
        return self._book.subscribe_decorator(listener)


class IQTopOfBook(TopOfBook, metaclass=Singleton):
    pass


class TWSTopOfBook(ISubscription, metaclass=Singleton):
    def __init__(self, ib_client: IBClient, contracts: typing.Set[ib_insync.Contract]):
        self.ib_client = ib_client
        self.contracts = contracts

    @classmethod
    def create_from_portfolio(cls, ib_client: IBClient):
        contracts = ib_client.position_contracts()
        log.info(contracts)
        return cls(ib_client, contracts)

    def reqMktData(self):
        for contract in self.contracts:
            log.info(f"subscribing to market data for {contract}")
            self.ib_client._ib.reqMktData(contract, '', False, False)

    def subscribe(self, listener: BookListener):
        self.ib_client._ib.pendingTickersEvent += listener

    def unsubscribe(self, listener: BookListener):
        self.ib_client._ib.pendingTickersEvent -= listener

    def getQuote(self, contract: ib_insync.Contract) -> ib_insync.Ticker:
        """ ib_insync keeps a TopOfBook accessible by calling ticker(contract)
        Args:
            contract:

        Returns:
        """
        return self.ib_client._ib.ticker(contract)
