import datetime
from ib_insync import IB, TradeLogEntry, Stock, Trade, Order, Fill, Execution, CommissionReport, TradeLogEntry, Future, \
    PortfolioItem, OrderStatus, Ticker, TickData, Position, Option

t = Trade(contract=Stock(conId=3691937, symbol='AMZN',
                         right='?', exchange='SMART',
                         currency='USD', localSymbol='AMZN',
                         tradingClass='NMS'),
          order=Order(orderId=-2, permId=520925220, action='BUY',
                      totalQuantity=100.0, orderType='MKT'
                      , lmtPrice=0.0, auxPrice=0.0, tif='DAY',
                      ocaType=3, openClose='', eTradeOnly=False,
                      firmQuoteOnly=False, volatilityType=0,
                      deltaNeutralOrderType='None', referencePriceType=0, account='DU2680628', clearingIntent='IB',
                      adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True),
          orderStatus=OrderStatus(orderId=-2, status='PreSubmitted', filled=0.0,
                                  remaining=100.0
                                  , avgFillPrice=0.0, permId=520925220, parentId=0, lastFillPrice=0.0, clientId=0,
                                  whyHeld='', mktCapPrice=0.0),
          fills=[Fill(contract=Stock(conId=3691937, symbol='AMZN', right='?',
                                     exchange='SMART', currency='USD',
                                     localSymbol='AMZN', tradingClass='NMS'),
                      execution=Execution(execId='0000e0d5.5f8688d9.01.01',
                                          time=datetime.datetime(2020, 9, 24, 14, 42, 8,
                                                                 tzinfo=datetime.timezone.utc),
                                          acctNumber='DU2680628', exchange='NYSENAT', side='BOT', shares=100.0,
                                          price=3011.92,
                                          permId=520925220, clientId=0, orderId=-2, liquidation=0, cumQty=100.0,
                                          avgPrice=3011.92, orderRef='', evRule='',
                                          evMultiplier=0.0,
                                          modelCode='', lastLiquidity=2),
                      commissionReport=CommissionReport(execId='', commission=0.0, currency='', realizedPNL=0.0,
                                                        yield_=0.0, yieldRedemptionDate=0),
                      time=datetime.datetime(2020, 9, 24, 14, 42, 12, 95953, tzinfo=datetime.timezone.utc))]
          , log=[TradeLogEntry(time=datetime.datetime(2020, 9, 24, 14, 42, 11, 792935, tzinfo=datetime.timezone.utc),
                               status='Inactive', message=''),
                 TradeLogEntry(time=datetime.datetime(2020, 9, 24, 14, 42, 11, 822937, tzinfo=datetime.timezone.utc),
                               status='PreSubmitted', message=''),
                 TradeLogEntry(time=datetime.datetime(2020, 9, 24, 14, 42, 12, 95953, tzinfo=datetime.timezone.utc),
                               status='PreSubmitted', message='Fill 100.0@3011.92')])

mktdata = ({Ticker(
    contract=Stock(conId=320227571, symbol='QQQ', right='0', exchange='SMART', primaryExchange='NASDAQ', currency='USD',
                   localSymbol='QQQ', tradingClass='NMS'),
    time=datetime.datetime(2020, 9, 30, 13, 1, 9, 648290, tzinfo=datetime.timezone.utc),
    marketDataType=3,
    bid=275.98,
    bidSize=10,
    ask=276.02,
    askSize=111,
    last=275.99,
    lastSize=2,
    prevBid=276.0, prevBidSize=7, prevAsk=276.07,
    prevAskSize=10, prevLast=276.01, prevLastSize=1, volume=7899, open=0.0, close=275.95, ticks=[
        TickData(time=datetime.datetime(2020, 9, 30, 13, 1, 9, 648290, tzinfo=datetime.timezone.utc), tickType=66,
                 price=275.98, size=10),
        TickData(time=datetime.datetime(2020, 9, 30, 13, 1, 9, 648290, tzinfo=datetime.timezone.utc), tickType=70,
                 price=276.02, size=111)])},)

p = Position(account='DU2721389',
             contract=Option(conId=443758230, symbol='AAPL', lastTradeDateOrContractMonth='20201023', strike=115.0,
                             right='P', multiplier='100', currency='USD', localSymbol='AAPL  201023P00115000',
                             tradingClass='AAPL'), position=10.0, avgCost=63.7338)

spp = Position(account='DU2735246',
               contract=Stock(conId=208813719, symbol='GOOGL', exchange='NASDAQ', currency='USD', localSymbol='GOOGL',
                              tradingClass='NMS'), position=100.0, avgCost=1598.87)

tt = Trade(contract=Stock(conId=265598, symbol='AAPL', right='?', exchange='SMART', currency='USD', localSymbol='AAPL',
                          tradingClass='NMS'),
           order=Order(permId=1337122343, action='BUY', totalQuantity=100.0, orderType='LMT', lmtPrice=78.26,
                       auxPrice=0.0, tif='GTC', ocaType=3, rule80A='0', openClose='', eTradeOnly=False,
                       firmQuoteOnly=False, volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0,
                       account='DU2735246', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0,
                       dontUseAutoPriceForHedge=True, usePriceMgmtAlgo=True),
           orderStatus=OrderStatus(orderId=0, status='Submitted', filled=0.0, remaining=100.0, avgFillPrice=0.0,
                                   permId=1337122343, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='',
                                   mktCapPrice=0.0), fills=[], log=[
        TradeLogEntry(time=datetime.datetime(2020, 10, 23, 15, 53, 34, 625653, tzinfo=datetime.timezone.utc),
                      status='Submitted', message='')])

oy = Trade(
    contract=Stock(conId=208813720, symbol='GOOG', right='?', exchange='SMART', currency='USD', localSymbol='GOOG',
                   tradingClass='NMS'),
    order=Order(permId=1337122348, action='SELL', totalQuantity=100.0, orderType='LMT', lmtPrice=1669.45, auxPrice=0.0,
                tif='DAY', ocaType=3, rule80A='0', openClose='', eTradeOnly=False, firmQuoteOnly=False,
                volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='DU2735246',
                clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True,
                usePriceMgmtAlgo=True),
    orderStatus=OrderStatus(orderId=0, status='Submitted', filled=0.0, remaining=100.0, avgFillPrice=0.0,
                            permId=1337122348, parentId=0, lastFillPrice=0.0, clientId=0, whyHeld='', mktCapPrice=0.0),
    fills=[], log=[TradeLogEntry(time=datetime.datetime(2020, 10, 23, 15, 53, 34, 626452, tzinfo=datetime.timezone.utc),
                                 status='Submitted', message='')])
