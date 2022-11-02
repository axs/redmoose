import pypath
from red_moose.iqfeed.client import IQFeedClient
from ib_insync import Option


def test_symbology():
    ib_opt = Option(conId=439398131, symbol='AMZN',
                    lastTradeDateOrContractMonth='20121020',
                    strike=19, right='P',
                    multiplier='100', primaryExchange='AMEX', currency='USD', localSymbol='AMZN  201002C03000000',
                    tradingClass='AMZN')

    iq_option = IQFeedClient.tws_option2iq_option(ib_opt)
    assert iq_option == 'AMZN1220V19'
