import enum


class IQFeedSubscription(enum.Enum):
    QUOTES_TRADES = enum.auto()
    TRADES = enum.auto()
    BARS = enum.auto()


class WriterType(enum.Enum):
    POSTGRES = enum.auto()
    PARQUET = enum.auto()
    FLEX = enum.auto()


class FlexQueryType(enum.Enum):
    TRANSACTIONS = 'transactions'
    POSITIONS = 'positions'


class Side(enum.IntEnum):
    BUY = 0
    SELL = 1

    def flip(self):
        return Side(self ^ 1)


class IBMarketDataTypes(enum.Enum):
    LIVE = 1
    DELAYED = 3


class ContentType(enum.Enum):
    JSON = "application/json"
    PYTHON_SERIALIZE = 'application/x-python-serialize'


class IBSecType(enum.Enum):
    STK = 'Stock (or ETF)'
    OPT = 'Option'
    FUT = 'Future'
    IND = 'Index'
    FOP = 'Futures option'
    CASH = 'Forex pair'
    CFD = 'CFD'
    BAG = 'Combo'
    WAR = 'Warrant'
    BOND = 'Bond'
    CMDTY = 'Commodity'
    NEWS = 'News'
    FUND = 'Mutual fund'


class IQFeedIntervalType(enum.Enum):
    SECONDS = 's'
    VOLUME = 'v'
    TICKS = 't'
