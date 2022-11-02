import logging
import time

import numpy as np
from typing import Sequence
import pyiqfeed as iq
from red_moose.rm_enums import ContentType
from red_moose.common import AppContext
from red_moose.common import Quote
from red_moose.market_data.top_of_book import IQTopOfBook
from red_moose.messaging.rabbit_producer import SimpleProducer

log = logging.getLogger(__name__)


class QuoteListener(iq.SilentQuoteListener):
    def __init__(self, name: str, **kwargs):
        """
        :param name:
        :param kwargs:
            interval:  sleep between quotes
        """
        self.interval = kwargs.get('interval', 0.5)
        self._topofbook = IQTopOfBook()
        super().__init__(name)

    def process_update(self, update: np.array) -> None:
        log.info("%s: Data Update" % self._name)
        try:
            q = Quote(*update[0])
            log.info(q)
            self._topofbook.addQuote(q)
            time.sleep(self.interval)
        except TypeError as t:
            log.exception(t)

    def process_watched_symbols(self, symbols: Sequence[str]) -> None:
        """List of all watched symbols when requested."""
        log.info(symbols)


class IQFeedRelayListener(iq.SilentQuoteListener, iq.SilentBarListener):
    def __init__(self, name: str, **kwargs):
        """Relay quotes to rabbitmq
        """
        context = AppContext()
        self.dev_producer = SimpleProducer(connection_url=context.rabbit_dev_url())
        self.prod_producer = SimpleProducer(connection_url=context.rabbit_prod_url())
        self.staging_producer = SimpleProducer(connection_url=context.rabbit_staging_url())
        self.interval = kwargs.get('interval', 0.05)
        super().__init__(name)

    def process_update(self, update: np.array) -> None:
        log.debug("%s: Data Update" % self._name)
        try:
            q = Quote(*update[0])
            self._publish(q)
            time.sleep(self.interval)
        except TypeError as t:
            log.exception(t)

    def _publish(self, quote: Quote):
        msg = quote.to_json()
        self.dev_producer.publish(msg, content_type=ContentType.JSON.value)
        self.prod_producer.publish(msg, content_type=ContentType.JSON.value)
        self.staging_producer.publish(msg, content_type=ContentType.JSON.value)

    def process_watched_symbols(self, symbols: Sequence[str]) -> None:
        """List of all watched symbols when requested."""
        for symbol in symbols:
            log.info(symbol)

    def process_live_bar(self, bar_data: np.array) -> None:
        """
        Args:
            bar_data:
                    [(b'SPY', '2020-10-13', 59465000000, 350.45, 350.45, 350.45, 350.45, 71614932, 800, 0)]
        """
        for bar in bar_data:
            try:
                q = Quote(Symbol=bar[0],
                          Bid=0,
                          Ask=0,
                          Last=bar[6],
                          Open=bar[3],
                          High=bar[4],
                          Low=bar[5],
                          timestamp=bar[2],
                          TotalVolume=bar[8])
                self._publish(q)
            except Exception as e:
                log.exception(e)

        log.debug(bar_data)
