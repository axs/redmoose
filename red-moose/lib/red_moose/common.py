import contextlib
import decimal
import datetime
import json
import logging
import os
import time
from functools import wraps
from typing import Callable
import attr
import numpy as np
from ib_insync import Ticker
from red_moose.persistence.dbutils import DBUtils

from typing import NewType, Dict

Json = NewType('Json', str)

log = logging.getLogger(__name__)


class ISubscription:
    def subscribe(self, listener: Callable):
        raise NotImplementedError

    def unsubscribe(self, listener: Callable):
        raise NotImplementedError

    def subscribe_decorator(self, listener: Callable):
        """ can only be used by functions not methods
        Args:
            listener:

        Returns:
        """
        self.subscribe(listener)

        @wraps(listener)
        def listener_wrapper(*args):
            return listener(*args)

        return listener_wrapper

    def __iadd__(self, listener: Callable):
        self.subscribe(listener)
        return self

    def __isub__(self, listener: Callable):
        self.unsubscribe(listener)
        return self


@contextlib.contextmanager
def timer(name="duration"):
    start = time.time()
    yield
    duration = time.time() - start
    log.info("{0}: {1} second(s)".format(name, duration))


class Singleton(type):
    # class blah(metaclass=Singleton):
    #       pass
    def __new__(typ, name, bas, clsd):
        cls = super().__new__(typ, name, bas, clsd)
        cls.instance = None
        return cls

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


class AppContext(metaclass=Singleton):
    def __init__(self):
        self._db_connection = None
        self._db_conf = None
        self._sqlalchemy_engine = None
        self._iq_feed_conf = None
        self._quandl_conf = None
        self._rabbit_conf = None
        self._street_trade_date = None

    @staticmethod
    def read_conf(cfg_name):
        cfg = os.path.join(os.path.dirname(__file__), f"../../conf/{cfg_name}.json")
        return json.load(open(cfg))

    @property
    def db_connection(self):
        if self._db_connection is None:
            self._db_connection = DBUtils.connection(self.db_conf)
        return self._db_connection

    @property
    def sqlalchemy_engine(self):
        if self._sqlalchemy_engine is None:
            self._sqlalchemy_engine = DBUtils.sqlalchemy_engine(self.db_conf)
        return self._sqlalchemy_engine

    @property
    def street_trade_date(self):
        return self._street_trade_date

    @street_trade_date.setter
    def street_trade_date(self, value):
        self._street_trade_date = value

    @property
    def quandl_conf(self):
        if self._quandl_conf is None:
            self._quandl_conf = AppContext.read_conf("quandl")
        return self._quandl_conf

    @property
    def db_conf(self):
        if self._db_conf is None:
            self._db_conf = AppContext.read_conf("postgres")
        return self._db_conf

    @property
    def iq_feed_conf(self):
        if self._iq_feed_conf is None:
            self._iq_feed_conf = AppContext.read_conf("iqfeed")
        return self._iq_feed_conf

    @property
    def rabbit_conf(self):
        if self._rabbit_conf is None:
            self._rabbit_conf = AppContext.read_conf("rabbit")
        return self._rabbit_conf

    def rabbit_env_url(self):
        d = self.rabbit_conf[os.environ.get('SIXENV', 'dev')]
        return f"amqp://{d.get('user')}:{d.get('password')}@{d.get('host')}/{d.get('virtual_host')}"

    def rabbit_dev_url(self):
        d = self.rabbit_conf['dev']
        return f"amqp://{d.get('user')}:{d.get('password')}@{d.get('host')}/{d.get('virtual_host')}"

    def rabbit_prod_url(self):
        d = self.rabbit_conf['prod']
        return f"amqp://{d.get('user')}:{d.get('password')}@{d.get('host')}/{d.get('virtual_host')}"

    def rabbit_staging_url(self):
        d = self.rabbit_conf['staging']
        return f"amqp://{d.get('user')}:{d.get('password')}@{d.get('host')}/{d.get('virtual_host')}"


@attr.s(auto_attribs=True, slots=True)
class XBar:
    open: float
    close: float
    high: float
    low: float
    start_time: attr.ib(default=0)
    end_time: attr.ib(default=0)


@attr.s(auto_attribs=True, slots=True)
class Position:
    account: str
    quantity: float
    sec_type: str
    sec_id_type: str
    contract_id: int
    sec_id: str
    avg_cost: float
    market_value: float
    realized_pnl: float
    unrealized_pnl: float
    market_price: float
    street_trade_date: datetime.datetime = attr.ib(default=datetime.datetime.utcnow())


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.datetime64):
            return str(obj)
        elif isinstance(obj, np.timedelta64):
            return obj.item().total_seconds()
        elif isinstance(obj, datetime.timedelta):
            return obj.microseconds
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return super(NpEncoder, self).default(obj)


def attr_to_json(attr_inst, **kwargs):
    return json.dumps(attr.asdict(attr_inst, **kwargs), cls=NpEncoder)


@attr.s(auto_attribs=True, slots=True)
class Quote:
    def sym_decode(sym):
        if type(sym) != str:
            return sym.decode()
        return sym

    Symbol: str = attr.ib(converter=sym_decode)
    Bid: float
    Ask: float
    Last: float
    Open: float = attr.ib(default=None)
    High: float = attr.ib(default=None)
    Low: float = attr.ib(default=None)
    BidSize: int = attr.ib(converter=int, default=0)
    AskSize: int = attr.ib(converter=int, default=0)
    LastSize: int = attr.ib(converter=int, default=0)
    BidTime: int = attr.ib(default=None)
    AskTime: int = attr.ib(default=None)
    LastTime: int = attr.ib(default=None)
    VWAP: float = attr.ib(default=None)
    TotalVolume: int = attr.ib(default=None)
    # above attr are used by IQfeed and must be in same order as iqfeed_fields
    contract_id: int = attr.ib(default=None)
    exchange: str = attr.ib(default=None)
    timestamp: int = attr.ib(default=None)

    @staticmethod
    def iqfeed_fields():
        """IQfeed fields have spaces
        XXX keep in same order as attributes
        """
        return ('Symbol',
                'Bid',
                'Ask',
                'Last',
                'Open', 'High', 'Low')

    def bid_ask_changed(self, other):
        return self.Bid != other.Bid or self.Ask != other.Ask

    @property
    def Mid(self):
        return (self.Bid + self.Ask) / 2.0

    # @property
    # def WeightedMid(self):
    #    return ((self.Bid * self.AskSize) + (self.Ask * self.BidSize)) / (self.BidSize + self.AskSize)

    def to_json(self, **kwargs):
        return attr_to_json(self, **kwargs)

    @staticmethod
    def from_json(quote_string: Json):
        """
        Args:
            quote_string:

        Returns: Quote object
        """
        return Quote(**json.loads(quote_string))

    @staticmethod
    def from_dict(quote_dict: Dict):
        """
        Args:
            quote_dict

        Returns: Quote object
        """
        return Quote(**quote_dict)

    @staticmethod
    def from_Ticker(ticker: Ticker, ticker_symbol=None):
        """
        Args:
            quote_string:

        Returns: Quote object
        """
        sym = ticker_symbol if ticker_symbol else ticker.contract.localSymbol
        tstamp = ticker.time.timestamp() if ticker.time else 0
        return Quote(
            Bid=ticker.bid,
            BidSize=ticker.bidSize,
            Ask=ticker.ask,
            AskSize=ticker.askSize,
            Last=ticker.last,
            LastSize=ticker.lastSize,
            Symbol=sym,
            timestamp=tstamp,
            contract_id=ticker.contract.conId,
            exchange=ticker.contract.exchange
        )


@attr.s(auto_attribs=True, slots=True)
class Bar:
    def sym_decode(sym):
        if type(sym) != str:
            return sym.decode()
        return sym

    def time_decode(t):
        if isinstance(t, datetime.timedelta):
            return str(t.microseconds)
        elif isinstance(t, np.timedelta64):
            return t.item().total_seconds()
        else:
            return t

    Symbol: str = attr.ib(converter=sym_decode)
    Date: str
    Time: int = attr.ib(converter=time_decode)
    Open: float
    High: float
    Low: float
    Close: float
    TotalVolume: int
    PeriodVolume: int
    NumTrades: int

    def to_json(self, **kwargs):
        return attr_to_json(self, **kwargs)
