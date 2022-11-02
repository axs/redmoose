import attr
import datetime
import logging
import time
import typing
import pyiqfeed as iq
from ib_insync import Contract, Option
from red_moose.common import AppContext, Quote
from red_moose.rm_types import IQFeedListener, Symbol, ContractId
from red_moose.rm_enums import IBSecType

log = logging.getLogger(__name__)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class OptionMonthSymbol:
    Call: str
    Put: str

    def lookup_by_right(self, right: str):
        if right.upper() == 'C':
            return self.Call
        elif right.upper() == 'P':
            return self.Put
        else:
            return None


class IQFeedClient:
    def __init__(self):
        self.iq_feed_conf = AppContext().iq_feed_conf
        try:
            self.launch()
        except Exception as e:
            log.exception(e)

    @staticmethod
    def quote_fields():
        # possible fields a quote message can have. We only need some
        return sorted(list(iq.QuoteConn.quote_msg_map.keys()))

    def launch(self):
        svc = iq.FeedService(product=self.iq_feed_conf.get('PRODUCTID'),
                             version="Debugging",
                             login=self.iq_feed_conf.get('USER'),
                             password=self.iq_feed_conf.get('PASSWORD'))
        svc.launch(headless=False)

    def get_daily_data(self, ticker: Symbol, num_days: int):
        hist_conn = iq.HistoryConn(name="red_moose-daily-data")
        hist_listener = iq.VerboseIQFeedListener("History Bar Listener")
        hist_conn.add_listener(hist_listener)

        with iq.ConnConnector([hist_conn]):
            try:
                daily_data = hist_conn.request_daily_data(ticker, num_days)
                log.info(daily_data)
            except (iq.NoDataError, iq.UnauthorizedError) as err:
                log.info("No data returned because {0}".format(err))

    def Xget_historical_bar_data(self, ticker: Symbol, bar_len: int, bar_unit: str,
                                 num_bars: int):
        """Shows how to get interval bars."""
        hist_conn = iq.HistoryConn(name="red_moose-historical-bars")
        hist_listener = iq.VerboseBarListener("History Bar Listener")
        hist_conn.add_listener(hist_listener)

        with iq.ConnConnector([hist_conn]):
            # look at conn.py for request_bars, request_bars_for_days and
            # request_bars_in_period for other ways to specify time periods etc
            try:
                bars = hist_conn.request_bars(ticker=ticker,
                                              interval_len=bar_len,
                                              interval_type=bar_unit,
                                              max_bars=num_bars)
                log.info(bars)

                today = datetime.date.today()
                start_date = today - datetime.timedelta(days=10)
                start_time = datetime.datetime(year=start_date.year,
                                               month=start_date.month,
                                               day=start_date.day,
                                               hour=0,
                                               minute=0,
                                               second=0)
                end_time = datetime.datetime(year=today.year,
                                             month=today.month,
                                             day=today.day,
                                             hour=23,
                                             minute=59,
                                             second=59)
                bars = hist_conn.request_bars_in_period(ticker=ticker,
                                                        interval_len=bar_len,
                                                        interval_type=bar_unit,
                                                        bgn_prd=start_time,
                                                        end_prd=end_time)
                log.debug(bars)
            except (iq.NoDataError, iq.UnauthorizedError) as err:
                log.info("No data returned because {0}".format(err))

    def get_historical_bar_data(self, ticker: Symbol, bar_len: int, bar_unit: str,
                                num_bars: int):
        """Shows how to get interval bars."""
        hist_conn = iq.HistoryConn(name="red_moose-historical-bars")
        hist_listener = iq.VerboseBarListener("History Bar Listener")
        hist_conn.add_listener(hist_listener)

        with iq.ConnConnector([hist_conn]):
            # look at conn.py for request_bars, request_bars_for_days and
            # request_bars_in_period for other ways to specify time periods etc
            bars = None
            try:
                bars = hist_conn.request_bars(ticker=ticker,
                                              interval_len=bar_len,
                                              interval_type=bar_unit,
                                              max_bars=num_bars)
                log.debug(bars)
            except (iq.NoDataError, iq.UnauthorizedError) as err:
                log.info("No data returned because {0}".format(err))
            return bars

    def get_level_1_quotes_and_trades(self,
                                      quote_conn: iq.QuoteConn,
                                      tickers: typing.List[Symbol],
                                      seconds: int,
                                      listener: IQFeedListener):
        """Get level 1 quotes and trades for ticker for seconds seconds."""

        # listener =  QuoteListener("Level 1 Listener")  #
        # quote_listener = listener("Level 1 Listener")
        quote_conn.add_listener(listener)
        with iq.ConnConnector([quote_conn]):
            # all_fields = sorted(list(iq.QuoteConn.quote_msg_map.keys()))
            # quote_conn.select_update_fieldnames(all_fields)
            quote_conn.select_update_fieldnames(Quote.iqfeed_fields())
            for ticker in tickers:
                quote_conn.watch(ticker)
            time.sleep(seconds)
            for ticker in tickers:
                quote_conn.unwatch(ticker)
            quote_conn.remove_listener(listener)

    def get_regional_quotes(self, ticker: Symbol, seconds: int):
        """Get level 1 quotes and trades for ticker for seconds seconds."""

        quote_conn = iq.QuoteConn(name="red_moose-regional")
        quote_listener = iq.VerboseQuoteListener("Regional Listener")
        quote_conn.add_listener(quote_listener)

        with iq.ConnConnector([quote_conn]):
            quote_conn.regional_watch(ticker)
            time.sleep(seconds)
            quote_conn.regional_unwatch(ticker)

    def get_trades_only(self,
                        quote_conn: iq.QuoteConn,
                        tickers: typing.List[Symbol],
                        seconds: int,
                        listener: IQFeedListener):
        quote_conn.add_listener(listener)
        with iq.ConnConnector([quote_conn]):
            quote_conn.select_update_fieldnames(Quote.iqfeed_fields())
            for ticker in tickers:
                quote_conn.trades_watch(ticker)
            time.sleep(seconds)
            for ticker in tickers:
                quote_conn.unwatch(ticker)
            quote_conn.remove_listener(listener)

    def get_live_interval_bars(self,
                               bar_conn: iq.BarConn,
                               tickers: typing.List[Symbol],
                               bar_len: int,
                               seconds: int,
                               bar_listener: IQFeedListener):
        """Get real-time interval bars"""
        # bar_conn = iq.BarConn(name='red_moose-interval-bars')
        # bar_listener = iq.VerboseBarListener("Bar Listener")
        bar_conn.add_listener(bar_listener)

        with iq.ConnConnector([bar_conn]):
            for ticker in tickers:
                bar_conn.watch(symbol=ticker,
                               interval_len=bar_len,
                               interval_type='s',
                               update=1,
                               lookback_bars=10)
            time.sleep(seconds)

    def get_tickdata(self, ticker: Symbol, max_ticks: int, num_days: int):
        """Show how to read tick-data"""

        hist_conn = iq.HistoryConn(name="red_moose-tickdata")
        hist_listener = iq.VerboseIQFeedListener("History Tick Listener")
        hist_conn.add_listener(hist_listener)

        # Look at conn.py for request_ticks, request_ticks_for_days and
        # request_ticks_in_period to see various ways to specify time periods
        # etc.

        with iq.ConnConnector([hist_conn]):
            # Get the last 10 trades
            try:
                tick_data = hist_conn.request_ticks(ticker=ticker,
                                                    max_ticks=max_ticks)
                log.debug(tick_data)

                # Get the last num_days days trades between 10AM and 12AM
                # Limit to max_ticks ticks else too much will be log.debuged on screen
                bgn_flt = datetime.time(hour=10, minute=0, second=0)
                end_flt = datetime.time(hour=12, minute=0, second=0)
                tick_data = hist_conn.request_ticks_for_days(ticker=ticker,
                                                             num_days=num_days,
                                                             bgn_flt=bgn_flt,
                                                             end_flt=end_flt,
                                                             max_ticks=max_ticks)
                log.debug(tick_data)

                # Get all ticks between 9:30AM 5 days ago and 9:30AM today
                # Limit to max_ticks since otherwise too much will be log.debuged on
                # screen
                today = datetime.date.today()
                sdt = today - datetime.timedelta(days=5)
                start_tm = datetime.datetime(year=sdt.year,
                                             month=sdt.month,
                                             day=sdt.day,
                                             hour=9,
                                             minute=30)
                edt = today
                end_tm = datetime.datetime(year=edt.year,
                                           month=edt.month,
                                           day=edt.day,
                                           hour=9,
                                           minute=30)

                tick_data = hist_conn.request_ticks_in_period(ticker=ticker,
                                                              bgn_prd=start_tm,
                                                              end_prd=end_tm,
                                                              max_ticks=max_ticks)
                log.debug(tick_data)
            except (iq.NoDataError, iq.UnauthorizedError) as err:
                log.exception("No data returned because {0}".format(err))

    def get_reference_data(self):
        """Markets, SecTypes, Trade Conditions etc"""
        table_conn = iq.TableConn(name="red_moose-reference-data")
        table_listener = iq.VerboseIQFeedListener("Reference Data Listener")
        table_conn.add_listener(table_listener)
        with iq.ConnConnector([table_conn]):
            table_conn.update_tables()
            log.debug("Markets:")
            log.debug(table_conn.get_markets())
            log.debug("")

            log.debug("Security Types:")
            log.debug(table_conn.get_security_types())
            log.debug("")

            log.debug("Trade Conditions:")
            log.debug(table_conn.get_trade_conditions())
            log.debug("")

            log.debug("SIC Codes:")
            log.debug(table_conn.get_sic_codes())
            log.debug("")

            log.debug("NAIC Codes:")
            log.debug(table_conn.get_naic_codes())
            log.debug("")
            table_conn.remove_listener(table_listener)

    def get_ticker_lookups(self, ticker: Symbol):
        lookup_conn = iq.LookupConn(name="red_moose-Ticker-Lookups")
        lookup_listener = iq.VerboseIQFeedListener("TickerLookupListener")
        lookup_conn.add_listener(lookup_listener)

        with iq.ConnConnector([lookup_conn]):
            syms = lookup_conn.request_symbols_by_filter(
                search_term=ticker, search_field='s')
            log.debug("Symbols with %s in them" % ticker)
            log.debug(syms)
            log.debug("")

            sic_symbols = lookup_conn.request_symbols_by_sic(83)
            log.debug("Symbols in SIC 83:")
            log.debug(sic_symbols)
            log.debug("")

            naic_symbols = lookup_conn.request_symbols_by_naic(10)
            log.debug("Symbols in NAIC 10:")
            log.debug(naic_symbols)
            log.debug("")
            lookup_conn.remove_listener(lookup_listener)

    def get_equity_option_chain(self, ticker: Symbol):
        lookup_conn = iq.LookupConn(name="red_moose-Eq-Option-Chain")
        lookup_listener = iq.VerboseIQFeedListener("EqOptionListener")
        lookup_conn.add_listener(lookup_listener)
        with iq.ConnConnector([lookup_conn]):
            # noinspection PyArgumentEqualDefault
            e_opt = lookup_conn.request_equity_option_chain(
                symbol=ticker,
                opt_type='pc',
                month_codes="".join(iq.LookupConn.call_month_letters +
                                    iq.LookupConn.put_month_letters),
                near_months=None,
                include_binary=True,
                filt_type=0, filt_val_1=None, filt_val_2=None)
            log.debug("Currently trading options for %s" % ticker)
            log.debug(e_opt)
            lookup_conn.remove_listener(lookup_listener)

    def get_futures_chain(self, ticker: Symbol):
        lookup_conn = iq.LookupConn(name="red_moose-Futures-Chain")
        lookup_listener = iq.VerboseIQFeedListener("FuturesChainLookupListener")
        lookup_conn.add_listener(lookup_listener)
        with iq.ConnConnector([lookup_conn]):
            f_syms = lookup_conn.request_futures_chain(
                symbol=ticker,
                month_codes="".join(iq.LookupConn.futures_month_letters),
                years="67",
                near_months=None,
                timeout=None)
            log.debug("Futures symbols with underlying %s" % ticker)
            log.debug(f_syms)
            lookup_conn.remove_listener(lookup_listener)

    def get_futures_spread_chain(self, ticker: Symbol):
        lookup_conn = iq.LookupConn(name="red_moose-Futures-Spread-Lookup")
        lookup_listener = iq.VerboseIQFeedListener("FuturesSpreadLookupListener")
        lookup_conn.add_listener(lookup_listener)
        with iq.ConnConnector([lookup_conn]):
            f_syms = lookup_conn.request_futures_spread_chain(
                symbol=ticker,
                month_codes="".join(iq.LookupConn.futures_month_letters),
                years="67",
                near_months=None,
                timeout=None)
            log.debug("Futures Spread symbols with underlying %s" % ticker)
            log.debug(f_syms)
            lookup_conn.remove_listener(lookup_listener)

    def get_futures_options_chain(self, ticker: Symbol):
        lookup_conn = iq.LookupConn(name="red_moose-Futures-Options-Chain")
        lookup_listener = iq.VerboseIQFeedListener("FuturesOptionLookupListener")
        lookup_conn.add_listener(lookup_listener)
        with iq.ConnConnector([lookup_conn]):
            f_syms = lookup_conn.request_futures_option_chain(
                symbol=ticker,
                month_codes="".join(iq.LookupConn.call_month_letters +
                                    iq.LookupConn.put_month_letters),
                years="67",
                near_months=None,
                timeout=None)
            log.debug("Futures Option symbols with underlying %s" % ticker)
            log.debug(f_syms)
            lookup_conn.remove_listener(lookup_listener)

    def get_news(self):
        news_conn = iq.NewsConn("red_moose-News-Conn")
        news_listener = iq.VerboseIQFeedListener("NewsListener")
        news_conn.add_listener(news_listener)

        with iq.ConnConnector([news_conn]):
            cfg = news_conn.request_news_config()
            log.debug("News Configuration:")
            log.debug(cfg)
            log.debug("")

            log.debug("Latest 10 headlines:")
            headlines = news_conn.request_news_headlines(
                sources=[], symbols=[], date=None, limit=10)
            log.debug(headlines)
            log.debug("")

            story_id = headlines[0].story_id
            story = news_conn.request_news_story(story_id)
            log.debug("Text of story with story id: %s:" % story_id)
            log.debug(story.story)
            log.debug("")

            today = datetime.date.today()
            week_ago = today - datetime.timedelta(days=7)

            counts = news_conn.request_story_counts(
                symbols=["AAPL", "IBM", "TSLA"],
                bgn_dt=week_ago, end_dt=today)
            log.debug("Number of news stories in last week for AAPL, IBM and TSLA:")
            log.debug(counts)
            log.debug("")

    @staticmethod
    def get_iq_ticker(contract: Contract) -> Symbol:
        """
        Args:
            contract:

        Returns: IQFeed symbol
        """
        tws2iq_contratcs = {
            'NG': 'NGT',
            'CL': 'QCL',
            'GC': 'QGC',
        }

        if contract.secType == IBSecType.STK.name:
            return contract.symbol
        elif contract.secType == IBSecType.FUT.name:
            if contract.symbol in tws2iq_contratcs:
                code = tws2iq_contratcs[contract.symbol] + contract.localSymbol[-2:]
            else:
                code = '@' + contract.localSymbol
            if code[-1] == '9':
                code = code[:-1] + '19'
            else:
                code = code[:-1] + '2' + code[-1]
            return code
        elif contract.secType == IBSecType.CASH.name:
            code = contract.symbol + contract.currency + 'SN.COMP'
            return code
        elif contract.secType == IBSecType.OPT.name:
            return IQFeedClient.tws_option2iq_option(contract)

        raise Exception(f'{contract.secType} is not implemented for IQ')

    @staticmethod
    def ibconid_IQ_ticker_map(contracts: typing.Iterable[Contract]) -> typing.Dict[ContractId, Symbol]:
        return {contract.conId: IQFeedClient.get_iq_ticker(contract) for contract in contracts}

    @staticmethod
    def option_months_table() -> typing.Tuple[OptionMonthSymbol, ...]:
        """http://www.iqfeed.net/symbolguide/index.cfm
        tuple index is the month number
        """
        return (
            OptionMonthSymbol(Call=None, Put=None),
            OptionMonthSymbol(Call='A', Put='M'),
            OptionMonthSymbol(Call='B', Put='N'),
            OptionMonthSymbol(Call='C', Put='O'),
            OptionMonthSymbol(Call='D', Put='P'),
            OptionMonthSymbol(Call='E', Put='Q'),
            OptionMonthSymbol(Call='F', Put='R'),
            OptionMonthSymbol(Call='G', Put='S'),
            OptionMonthSymbol(Call='H', Put='T'),
            OptionMonthSymbol(Call='I', Put='U'),
            OptionMonthSymbol(Call='J', Put='V'),
            OptionMonthSymbol(Call='K', Put='W'),
            OptionMonthSymbol(Call='L', Put='X'),
        )

    @staticmethod
    def tws_option2iq_option(ib_opt: typing.Union[Option, Contract]):
        iq_opt_month_labels = IQFeedClient.option_months_table()

        strike = ib_opt.strike
        ticker = ib_opt.symbol
        expiry = datetime.datetime.strptime(ib_opt.lastTradeDateOrContractMonth, "%Y%m%d")
        month_label = iq_opt_month_labels[expiry.month].lookup_by_right(ib_opt.right)
        year = expiry.year % 100
        day = expiry.day
        strike = int(strike) if strike % 1 == 0 else strike
        return f"{ticker}{year}{day}{month_label}{strike}"
