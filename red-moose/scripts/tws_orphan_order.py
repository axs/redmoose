import pypath
import argparse
import logging
import sys

from red_moose.ib.tws_orphan_orders import TWSOrphanOrders

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Check TWS Orphan Orders

tws_orphan_order.py -e petiop345-paper.ib-comm -r trades-update -r position-update  
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-e", "--exchange", help="Exchange Name", required=True)
parser.add_argument("-r", "--routing_key", action='append', help="Routing Key", required=True)
args = parser.parse_args()

log.info(f"Arguments: {args}")

orphan_orders_runner = TWSOrphanOrders.create(args.exchange, *args.routing_key)
orphan_orders_runner.run()
