import pypath
import argparse
import logging
import sys
from red_moose.persistence.persist import FlexQueryResultsWriter
from red_moose.rm_enums import FlexQueryType

logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

desc = """
Load Flex query transactions results to database
"""

parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-t", "--token", help="flex query token")
parser.add_argument("-q", "--queryId", help="flex query queryId")
parser.add_argument("-f", "--flex_type", choices=[i.value for i in FlexQueryType], help="flex query FlexQueryType")
args = parser.parse_args()

log.info(f"Arguments: {args}")

fqr = FlexQueryResultsWriter(token=args.token,
                             queryId=args.queryId,
                             flex_query_type=FlexQueryType[args.flex_type.upper()])
df = fqr.get_flex_results()
fqr.write(df)
