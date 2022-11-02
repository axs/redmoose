import abc
from typing import Union

from pyiqfeed.conn import QuoteConn, BarConn
from pyiqfeed.listeners import SilentQuoteListener, SilentBarListener
from red_moose.iqfeed.client import IQFeedClient
from red_moose.rm_enums import IQFeedSubscription


class RMBaseConnection(abc.ABC):
    def __init__(self, feedCon: Union[QuoteConn, BarConn], **kwargs):
        """ Common Interface for iqfeed *Conn objects
        Args:
            feedCon:
        """
        self.conn = feedCon
        self.watching = set()
        self.bar_kwargs = kwargs.get('bar_kwargs', {})
        self.run_for = 60 * 60 * 24 * 3

    @abc.abstractmethod
    def watch(self, ticker, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe(self, *args, **kwargs):
        pass

    @classmethod
    def create(cls, iqsubscription: IQFeedSubscription):
        if iqsubscription == IQFeedSubscription.QUOTES_TRADES:
            return RMConnection(QuoteConn(name="red_moose-lvl1"))
        elif iqsubscription == IQFeedSubscription.BARS:
            return RMBarConnection(BarConn(name="red_moose-interval-bars"))
        elif iqsubscription == IQFeedSubscription.TRADES:
            return RMTradeConnection(QuoteConn(name="red_moose-lvl1"))

    def watchlist(self):
        return self.watching


class RMConnection(RMBaseConnection):
    def watch(self, ticker, **kwargs):
        self.conn.watch(ticker, **kwargs)
        for w in self.watching:
            self.conn.refresh(w)
        self.watching.add(ticker)

    def subscribe(self, iqclient: IQFeedClient, tickers, relay: Union[SilentQuoteListener, SilentBarListener]):
        iqclient.get_level_1_quotes_and_trades(self.conn, tickers, self.run_for, relay)


class RMBarConnection(RMBaseConnection):
    def watch(self, ticker, **kwargs):
        self.conn.watch(**dict(symbol=ticker,
                               interval_len=5,
                               interval_type='s',
                               update=1,
                               lookback_bars=10))
        self.watching.add(ticker)

    def subscribe(self, iqclient: IQFeedClient, tickers, relay: Union[SilentQuoteListener, SilentBarListener]):
        iqclient.get_live_interval_bars(self.conn, tickers, 10, self.run_for, relay)


class RMTradeConnection(RMConnection):
    def watch(self, ticker, **kwargs):
        self.conn.trades_watch(ticker)
        self.watching.add(ticker)

    def subscribe(self, iqclient: IQFeedClient, tickers, relay: Union[SilentQuoteListener, SilentBarListener]):
        iqclient.get_trades_only(self.conn, tickers, self.run_for, relay)
