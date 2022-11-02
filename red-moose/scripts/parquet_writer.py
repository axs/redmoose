import pypath
from red_moose.persistence.persist import ParquetPositionWriter
from red_moose.ib.client import IBClient
import logging
import argparse
import datetime as dt
import sys

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Get positions from IB and append them to parquet file
"""

today = dt.datetime.utcnow().strftime('%Y%m%d')
parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--file", help="filename", default=f'{today}_positions.parquet')
args = parser.parse_args()

log.info(f"Arguments: {args}")

ib = IBClient()
ppw = ParquetPositionWriter(destination_filename=args.file)
ppw.write(ib._ib.portfolio())
