import pypath
from red_moose.ib.price_feed_publisher import IBPriceFeedPublisher
from red_moose.market_data.top_of_book import TWSTopOfBook
from red_moose.ib.client import IBClient

i = IBClient(clientId=0)
ib_TopOfBook = TWSTopOfBook.create_from_portfolio(i)
ib_TopOfBook.reqMktData()
i._ib.sleep(3)

ib_publisher = IBPriceFeedPublisher(ib_TopOfBook)

i._ib.run()
