import logging
import random

from kombu import Connection, Exchange, Queue, binding
from typing import Set
from red_moose.common import AppContext, Quote
from red_moose.market_data.top_of_book import TopOfBook
from red_moose.messaging.rabbit_consumer import SimpleConsumer
from red_moose.iqfeed.client import IQFeedClient
from red_moose.rm_enums import IBMarketDataTypes

log = logging.getLogger(__name__)


class TWSQuotes(SimpleConsumer):
    # 1 is live, 3 is delayed
    MARKETDATATYPES = {IBMarketDataTypes.LIVE, IBMarketDataTypes.DELAYED}

    def __init__(self, conn: Connection, exchange: Exchange, queue: Queue, **kwargs):
        # tob is IQfeed ticker -> Quote
        self.tob = TopOfBook()
        self.marketDataType: Set[IBMarketDataTypes] = kwargs.get('marketDataType', TWSQuotes.MARKETDATATYPES)
        super().__init__(conn, exchange, queue)

    @property
    def top_of_book(self):
        return self.tob

    @classmethod
    def create(cls, exchange_name, *routing_keys, queue_name=f'tws_quotes_q{random.randint(1, 1000)}', **kwargs):
        # rk = 'ib.ticker.update'
        exchange = Exchange(exchange_name, type='topic', durable=False, auto_delete=True)
        conn = Connection(AppContext().rabbit_env_url())
        queue = Queue(name=queue_name,
                      exchange=exchange,
                      bindings=[binding(exchange, routing_key=routing_key) for routing_key in routing_keys],
                      auto_delete=True,
                      durable=False,
                      exclusive=True)
        marketDataType: Set[IBMarketDataTypes] = kwargs.get('marketDataType', TWSQuotes.MARKETDATATYPES)
        return cls(conn, exchange, queue, marketDataType=marketDataType)

    def on_message(self, body, message):
        # this is a pickle autodecoded from ib_insync.Ticker
        # convert to Quote object and add to top of book
        if body.marketDataType in self.marketDataType:
            log.info(body)
            symbol = IQFeedClient.get_iq_ticker(body.contract)
            self.tob.addQuote(Quote.from_Ticker(body, symbol))
        super().on_message(body, message)

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        pass


class IQFeedQuotes(SimpleConsumer):
    def __init__(self, conn: Connection, exchange: Exchange, queue: Queue):
        # tob is IQfeed ticker -> Quote
        self.tob = TopOfBook()
        super().__init__(conn, exchange, queue)

    @property
    def top_of_book(self):
        return self.tob

    @classmethod
    def create(cls, queue_name=f'iqfeed_quotes_q{random.randint(1, 1000)}'):
        exchange = Exchange('iqfeed', type='fanout', durable=True)
        conn = Connection(AppContext().rabbit_env_url())
        queue = Queue(name=queue_name,
                      exchange=exchange,
                      bindings=[binding(exchange)],
                      auto_delete=True,
                      durable=False,
                      exclusive=True)
        return cls(conn, exchange, queue)

    def on_message(self, body, message):
        log.info(body)
        # this is a decoded json ie Dict body from Quote
        self.tob.addQuote(Quote.from_dict(body))
        super().on_message(body, message)

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        pass
