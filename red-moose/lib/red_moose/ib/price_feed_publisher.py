import logging
import typing

import ib_insync
from kombu import Exchange

from red_moose.common import AppContext, Quote
from red_moose.market_data.top_of_book import TWSTopOfBook
from red_moose.messaging.rabbit_producer import SimpleProducer
from red_moose.rm_enums import ContentType


log = logging.getLogger(__name__)


class IBPriceFeedPublisher:
    def __init__(self, ib_TopOfBook: TWSTopOfBook):
        self.ib_TopOfBook = ib_TopOfBook
        self.ib_TopOfBook += self.IB_listener
        context = AppContext()
        self.producer = SimpleProducer(connection_url=context.rabbit_env_url(),
                                       exchange=Exchange("twspricefeed", type="fanout"))

    def IB_listener(self, data: typing.Set[ib_insync.Ticker]):
        for ticker in data:
            mid = (ticker.bid + ticker.ask) / 2.
            log.info(f"TWS_listener IBPriceFeedPublisher {ticker.contract.localSymbol} {mid} ")
            quote = Quote(
                Bid=ticker.bid,
                BidSize=ticker.bidSize,
                Ask=ticker.ask,
                AskSize=ticker.askSize,
                Last=ticker.last,
                LastSize=ticker.lastSize,
                Symbol=ticker.contract.localSymbol,
                timestamp=ticker.time.timestamp(),
                contract_id=ticker.contract.conId,
                exchange=ticker.contract.exchange
            )
            self.producer.publish(quote.to_json(), content_type=ContentType.JSON.value)
