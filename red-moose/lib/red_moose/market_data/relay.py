import logging
import threading

from red_moose.iqfeed.client import IQFeedClient
from red_moose.iqfeed.listeners import IQFeedRelayListener
from red_moose.iqfeed.rm_connection import RMBaseConnection
from red_moose.iqfeed.symbol_request_consumer import IQFeedSymbolRequests

log = logging.getLogger(__name__)


class IQFeedRelay:
    tickers = ['VIX.XO', 'NDX.X', 'INDU.X', 'SPX.XO']

    def __init__(self, quote_conn: RMBaseConnection):
        """ IQFeedRelay connects to IQfeed, attaches listener, and subscribes to rabbitmq commands
        Args:
            quote_conn: implementation of RMBaseConnection
        """
        self.relay = IQFeedRelayListener("Level 1 Listener", )
        self.i = IQFeedClient()
        self.quote_conn = quote_conn
        self.iqfeed_req_rabbitconsumer = IQFeedSymbolRequests.create(quote_conn)

    @staticmethod
    def start(quote_conn: RMBaseConnection):
        iq_relay = IQFeedRelay(quote_conn)
        iqfeed_req_thread = threading.Thread(target=iq_relay.iqfeed_req_rabbitconsumer.run)
        iqfeed_req_thread.start()
        quote_conn.subscribe(iq_relay.i,
                             IQFeedRelay.tickers,
                             iq_relay.relay)
