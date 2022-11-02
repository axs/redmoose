import typing
from red_moose.common import Position, Quote
import ib_insync
import pandas as pd
import pyiqfeed as iq

PersistentRecord = typing.Union[Position, ib_insync.PortfolioItem, Quote]
IQFeedListener = typing.Union[iq.listeners.SilentIQFeedListener, iq.listeners.VerboseIQFeedListener]
Symbol = typing.NewType('Symbol', str)
ContractId = typing.NewType('ContractId', int)
OrderId = typing.NewType('OrderId', int)
BookListener = typing.NewType('BookListener', typing.Callable)
OptionProfileResults = typing.NewType('OptionProfileResults', pd.DataFrame)

T = typing.TypeVar('T')  # Any type.
KT = typing.TypeVar('KT')  # Key type.
VT = typing.TypeVar('VT')  # Value type.
T_co = typing.TypeVar('T_co', covariant=True)  # Any type covariant containers.
V_co = typing.TypeVar('V_co', covariant=True)  # Any type covariant containers.
VT_co = typing.TypeVar('VT_co', covariant=True)  # Value type covariant containers.
