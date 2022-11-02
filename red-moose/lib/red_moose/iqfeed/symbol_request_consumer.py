import logging

from kombu import Connection, Exchange, Queue

from red_moose.common import AppContext
from red_moose.iqfeed.rm_connection import RMBaseConnection
from red_moose.messaging.rabbit_consumer import SimpleConsumer
from red_moose.messaging.topics import Topics

log = logging.getLogger(__name__)


class IQFeedSymbolRequests(SimpleConsumer):
    """
    consume/handle messages from commands exchange, IQFEED_TICKER_REQ
    """

    def __init__(self, quote_conn: RMBaseConnection, conn: Connection, exchange: Exchange, queue: Queue):
        self.quote_conn = quote_conn
        super().__init__(conn, exchange, queue)

    @classmethod
    def create(cls, quote_conn: RMBaseConnection):
        exchange = Exchange("commands", type="direct", durable=True)
        conn = Connection(AppContext().rabbit_env_url())
        queue = Queue(exchange=exchange,
                      name='iqfeed_req_sym',
                      auto_delete=True,
                      exclusive=True,
                      routing_key=Topics.IQ_TICKER_REQUEST)
        return cls(quote_conn, conn, exchange, queue)

    def on_message(self, body, message):
        log.info(message)
        log.info(body)
        try:
            self.quote_conn.watch(body)
        except Exception as e:
            log.exception(e)
        super().on_message(body, message)
