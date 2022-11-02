import pypath
from red_moose.iqfeed.client import IQFeedClient
from red_moose.iqfeed.listeners import QuoteListener
import threading
from red_moose.market_data.top_of_book import IQTopOfBook
from red_moose.common import AppContext, Quote
from red_moose.iqfeed.symbol_request_consumer import IQFeedSymbolRequests
from kombu import Connection, Exchange, Queue, binding
from kombu.mixins import ConsumerMixin
import pyiqfeed
from red_moose.ib.client import IBClient
import sys   ,time

# i = IBClient()
# contracts = {portfolio_item.contract for portfolio_item in i._ib.portfolio()}

# IB_conid_IQ_ticker_map = {contract.conId: IQFeedClient.get_iq_ticker(contract) for contract in contracts}

# print(IB_conid_IQ_ticker_map.values())
# sys.exit(2)

q = QuoteListener("Level 1 Listener")
i = IQFeedClient()
t = IQTopOfBook()


@t.subscribe_decorator
def mylistener(data):
    print()
    print(f"mylistener {data}")
    print()


# x = threading.Thread(target=i.get_level_1_quotes_and_trades, args=(['MSFT'], 30, q))
# y = threading.Thread(target=i.get_level_1_quotes_and_trades, args=(['AAPL'], 30, q))
# y.start()
# x.start()

# i.get_live_interval_bars('AAPL',bar_len=5,seconds=1)

"""
e = Exchange('commands', type='direct')
rr = IQFeedSymbolRequests(Connection(AppContext().rabbit_dev_url()),
                          Exchange('commands', type='direct'),
                          Queue(name='iqfeeder_req',
                                routing_key='IQFEED_TICKER_REQ',
                                exclusive=True,
                                exchange=e)
                          )
"""
quote_conn = pyiqfeed.QuoteConn(name="red_moose-lvl1")
y = threading.Thread(target=i.get_level_1_quotes_and_trades, args=(quote_conn, ['IBM'], 30, q))
y.start()
#i.get_level_1_quotes_and_trades(quote_conn,['AAPL', 'MSFT'], 30, q)
print('here')

time.sleep(2)
print('XXXXXXXXXXXXXXXXXXXhere')

quote_conn.refresh('MSFT')
quote_conn.watch('AMZN')
quote_conn.watch('GOOGL')
quote_conn.request_watches()
