import logging

from kombu import Connection, Exchange, Queue, binding
import ib_insync
import random
from red_moose.rm_enums import ContentType
from red_moose.common import AppContext
from red_moose.messaging.rabbit_consumer import SimpleConsumer
from red_moose.messaging.rabbit_producer import SimpleProducer
from red_moose.messaging.topics import Topics
from red_moose.messaging.messages import Request
from red_moose.ib.oms import OrderManager
from red_moose.ib.portfolio import Portfolio

log = logging.getLogger(__name__)


class TWSOrphanOrders(SimpleConsumer):
    def __init__(self, conn: Connection, exchange: Exchange, queue: Queue):
        self.producer = SimpleProducer(connection_url=AppContext().rabbit_env_url(),
                                       exchange=exchange)
        self.portfolio = Portfolio()
        self.oms = OrderManager()
        super().__init__(conn, exchange, queue)

    @classmethod
    def create(cls, exchange_name, *routing_keys, queue_name=f'orphanorder_q{random.randint(1, 1000)}'):
        exchange = Exchange(exchange_name, type='topic', durable=False, auto_delete=True)
        conn = Connection(AppContext().rabbit_env_url())
        queue = Queue(name=queue_name,
                      exchange=exchange,
                      bindings=[binding(exchange, routing_key=routing_key) for routing_key in routing_keys],
                      auto_delete=True,
                      durable=False,
                      exclusive=True)
        return cls(conn, exchange, queue)

    def on_message(self, body, message):
        log.debug(body)
        if isinstance(body, ib_insync.Trade):
            self._handleTrade(body)
            if not self.portfolio.hasUnderlying(body.contract.symbol):
                self.producer.publish(body, routing_key=Topics.TRADES_ORPHANS,
                                      content_type=ContentType.PYTHON_SERIALIZE.value)
        elif isinstance(body, ib_insync.Position):
            self._handlePosition(body)
        super().on_message(body, message)

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        self.requests()

    def _handleTrade(self, trade: ib_insync.Trade):
        self.oms.addOrder(trade)

    def _handlePosition(self, position: ib_insync.Position):
        self.portfolio.addPosition(position)

    def requestTrades(self):
        log.info('requesting trades')
        self.producer.publish(Request(sender=TWSOrphanOrders.__name__).to_json(),
                              routing_key=Topics.IB_TRADES_REQUEST,
                              content_type=ContentType.JSON.value)

    def requestPositions(self):
        log.info('requesting positions')
        self.producer.publish(Request(sender=TWSOrphanOrders.__name__).to_json(),
                              routing_key=Topics.IB_POSITIONS_REQUEST,
                              content_type=ContentType.JSON.value)

    def requests(self):
        self.requestPositions()
        self.requestTrades()
