import pypath
import threading
import argparse
import logging
import sys

from red_moose.market_data.arbitrators import PriceArbitrator
from red_moose.market_data.quotes_consumer import TWSQuotes, IQFeedQuotes
from red_moose.messaging.rabbit_producer import SimpleProducer
from red_moose.common import AppContext
from red_moose.rm_enums import IBMarketDataTypes
from kombu import Exchange

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Price arbitration IQFeed vs TWS
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-e", "--exchange", help="RabbitMQ exchange")
args = parser.parse_args()

log.info(f"Arguments: {args}")

producer = SimpleProducer(connection_url=AppContext().rabbit_env_url(),
                          exchange=Exchange(args.exchange,
                                            type="topic",
                                            durable=False,
                                            auto_delete=True))

tws_consumer = TWSQuotes.create(args.exchange, 'ib.ticker.update', marketDataType={IBMarketDataTypes.LIVE})
iqfeed_consumer = IQFeedQuotes.create()

pa = PriceArbitrator(iqfeed_consumer.top_of_book, tws_consumer.top_of_book, producer)

tws_consumer_thread = threading.Thread(target=tws_consumer.run)
tws_consumer_thread.start()

iqfeed_consumer_thread = threading.Thread(target=iqfeed_consumer.run)
iqfeed_consumer_thread.start()
