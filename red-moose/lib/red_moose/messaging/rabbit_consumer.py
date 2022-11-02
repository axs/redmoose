import abc

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from kombu.mixins import ConsumerProducerMixin
from red_moose.rm_enums import ContentType


class SimpleConsumer(ConsumerMixin, abc.ABC):

    def __init__(self, connection: Connection, exchange: Exchange, queue: Queue):
        """
        Args:
            connection:
            exchange:
            queue:
        """
        self.connection = connection
        self.exchange = exchange  # Exchange('iqfeed',type='fanout')
        self.q = queue

    def get_consumers(self, consumer, channel):
        return [
            consumer(queues=[self.q], callbacks=[self.on_message], accept={'json', 'pickle'}, prefetch_count=10),
        ]

    @abc.abstractmethod
    def on_message(self, body, message):
        message.ack()


class RabbitRelay(ConsumerProducerMixin, abc.ABC):
    def __init__(self, connection):
        self.connection = connection
        self.rpc_queue = Queue('rpc_queue')

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[self.rpc_queue],
            on_message=self.on_message,
            accept={ContentType.JSON.value, ContentType.PYTHON_SERIALIZE.value},
            prefetch_count=10,
        )]

    @abc.abstractmethod
    def message_handler(self, message_payload):
        ...

    def on_message(self, message):
        n = message.payload['n']
        result = self.message_handler(n)

        self.producer.publish(
            {'result': result},
            exchange='',
            routing_key=message.properties['reply_to'],
            correlation_id=message.properties['correlation_id'],
            serializer='json',
            retry=True,
        )
        message.ack()
