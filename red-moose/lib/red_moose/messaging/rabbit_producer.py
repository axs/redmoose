from kombu import Connection, Exchange, Producer
import logging
import time

log = logging.getLogger(__name__)


class SimpleProducer:
    def __init__(self, **kwargs):
        rabbit_url = kwargs.get('connection_url')
        log.info(rabbit_url)
        conn = Connection(rabbit_url)
        channel = conn.channel()
        exchange = kwargs.get('exchange', Exchange("iqfeed", type="fanout"))
        self.producer = Producer(exchange=exchange, channel=channel)
        # queue = Queue(name="example-queue", exchange=exchange, routing_key="BOB")
        # queue.maybe_bind(conn)
        # queue.declare()

    def publish(self, message, **kwargs):
        # default timestamp if not given
        timestamp = kwargs.pop('timestamp', None) or int(time.time())
        self.producer.publish(message, timestamp=timestamp, **kwargs)
