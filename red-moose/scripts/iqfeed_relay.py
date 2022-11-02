import pypath
import argparse
import logging
import sys

from red_moose.iqfeed.rm_connection import RMBaseConnection
from red_moose.market_data.relay import IQFeedRelay
from red_moose.rm_enums import IQFeedSubscription

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Relay IQFeed to rabbitmq
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-s", "--subscription", choices=[i.name for i in IQFeedSubscription], help="IQFeedSubscription")
args = parser.parse_args()

log.info(f"Arguments: {args}")

iq_conn = RMBaseConnection.create(IQFeedSubscription[args.subscription])
IQFeedRelay.start(iq_conn)
