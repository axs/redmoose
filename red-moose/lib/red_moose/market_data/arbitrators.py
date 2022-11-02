import logging
import typing

from red_moose.common import Quote
from red_moose.market_data.top_of_book import TopOfBook
from red_moose.rm_types import Symbol
from red_moose.rm_enums import ContentType
from red_moose.messaging.rabbit_producer import SimpleProducer
from red_moose.messaging.messages import SimpleMessage
from red_moose.messaging.topics import Topics

log = logging.getLogger(__name__)


class PriceArbitrator:
    def __init__(self, iq_TopOfBook: TopOfBook, ib_TopOfBook: TopOfBook, rabbit_producer: SimpleProducer):
        self.producer = rabbit_producer
        self.iq_TopOfBook = iq_TopOfBook
        self.ib_TopOfBook = ib_TopOfBook
        self.iq_TopOfBook += self.IQFeed_listener
        self.ib_TopOfBook += self.IB_listener

    def IB_listener(self, data: typing.Tuple[Symbol, Quote]):
        log.info(f"TWS_TopOfBook my_listener {data}")
        sym = data[0]
        quote = data[1]
        IQ_value = self.iq_TopOfBook.getQuote(sym)
        log.info(f"TWS value  {IQ_value}")
        if IQ_value:
            self.arbitrate(IQ_value, quote)

    def IQFeed_listener(self, data: typing.Tuple[Symbol, Quote]):
        log.info(f"IQ_TopOfBook my_listener {data}")
        sym = data[0]
        quote = data[1]
        TWS_value = self.ib_TopOfBook.getQuote(sym)
        log.info(f"TWS value  {TWS_value}")
        if TWS_value:
            self.arbitrate(quote, TWS_value)

    def arbitrate(self, iq_quote: Quote, ib_ticker: Quote):
        try:
            log.info(f"arbitrate TWS ticker {ib_ticker}")
            log.info(f"arbitrate IQ ticker {iq_quote}")
            if iq_quote.Mid != ib_ticker.Mid:
                msg = f"mid prices differs between IQFeed {iq_quote.Mid} and TWS {ib_ticker.Mid}"
                self.producer.publish(SimpleMessage(sender=__name__,
                                                    body=msg
                                                    ).to_json(),
                                      routing_key=Topics.PRICE_ARBITRATION_KEY,
                                      content_type=ContentType.JSON.value)
                log.warning(msg)
                log.warning(f"IQFeed {iq_quote}")
                log.warning(f"TWS {ib_ticker}")
        except Exception as e:
            log.exception(e)
