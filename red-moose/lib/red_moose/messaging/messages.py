from typing import Optional

import attr
import time
import json
import pickle
import uuid

import ib_insync as ibc
from red_moose.rm_enums import IBSecType


@attr.s(auto_attribs=True, slots=True)
class Message:
    sender: str
    sending_time: int = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.sending_time = int(time.time())

    def to_json(self):
        return json.dumps(attr.asdict(self))

    @classmethod
    def from_json(cls, s, *popattrs):
        d = json.loads(s)
        return cls.from_dict(d, *popattrs)

    @classmethod
    def from_dict(cls, d, *popattrs):
        popattrs += ("sending_time",)
        name_vals = [(p, d.pop(p)) for p in popattrs]
        obj = cls(**d)
        for n, v in name_vals:
            setattr(obj, n, v)
        return obj


@attr.s(auto_attribs=True, slots=True)
class Pickle(Message):
    pickle_str: str = attr.ib(init=False, default="")

    def store_pickle(self, obj):
        encoded = pickle.dumps(obj, protocol=0)
        self.pickle_str = encoded.decode()

    def load_pickle(self):
        encoded = self.pickle_str.encode()
        return pickle.loads(encoded)

    @classmethod
    def from_json(cls, s, *popattrs):
        return super().from_json(s, "pickle_str", *popattrs)


@attr.s(auto_attribs=True, slots=True)
class SimpleMessage(Message):
    body: str


@attr.s(auto_attribs=True, slots=True)
class Request(Message):
    request_id: str = attr.ib(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.request_id = uuid.uuid1().hex

    @classmethod
    def from_json(cls, s, *popattrs):
        return super().from_json(s, "request_id", *popattrs)


@attr.s(auto_attribs=True, slots=True)
class PickleRequest(Pickle):
    request_id: str = attr.ib(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.request_id = uuid.uuid1().hex

    @classmethod
    def from_json(cls, s, *popattrs):
        return super().from_json(s, "request_id", *popattrs)


@attr.s(auto_attribs=True, slots=True)
class Response(Message):
    request_id: str


@attr.s(auto_attribs=True, slots=True)
class ConIdReq(Request):
    con_id: int


@attr.s(auto_attribs=True, slots=True)
class PositionMsg(Message):
    account_id: str
    con_id: int
    pos_id: Optional[int] = None
    sec_type: str = "OPT"
    currency: Optional[str] = None
    asset_category: Optional[str] = None
    symbol: Optional[str] = None
    underlying_symbol: Optional[str] = None
    underlying_con_id: Optional[int] = None
    report_date: Optional[str] = None
    strike: Optional[float] = None
    expiry: Optional[int] = None
    put_call: Optional[str] = None
    listing_exchange: Optional[str] = None
    position: Optional[float] = None
    mkt_price: Optional[float] = None
    position_value: Optional[float] = None
    open_price: Optional[float] = None
    cost_basis_price: Optional[float] = None
    cost_basis_money: Optional[str] = None
    percent_of_nav: Optional[float] = None
    fifo_pnl_unrealized: Optional[float] = None
    side: Optional[str] = None

    @classmethod
    def from_ibc(cls, position: ibc.Position, sender: str):
        contract = position.contract
        if contract.lastTradeDateOrContractMonth:
            expiry = int(contract.lastTradeDateOrContractMonth)
        else:
            expiry = None
        return PositionMsg(sender,
                           position.account,
                           position.contract.conId,
                           sec_type=contract.secType,
                           currency=contract.currency,
                           symbol=contract.symbol,
                           strike=contract.strike,
                           expiry=expiry,
                           put_call=contract.right,
                           listing_exchange=contract.exchange,
                           position=position.position,
                           position_value=position.avgCost * position.position)


@attr.s(auto_attribs=True, slots=True)
class IBContract(Message):
    symbol: str
    con_id: int
    exchange: str
    currency: str
    sec_type: str

    @classmethod
    def from_ibc(cls, contract: ibc.Contract, sender: str):
        if contract.secType == "STK":
            return IBStock.from_ibc(contract, sender)
        elif contract.secType == "OPT":
            return IBStock.from_ibc(contract, sender)


@attr.s(auto_attribs=True, slots=True)
class IBStock(IBContract):
    sec_type: str = IBSecType.STK.name

    @classmethod
    def from_ibc(cls, contract: ibc.Contract, sender: str):
        return IBContract(sender,
                          contract.symbol,
                          contract.conId,
                          contract.exchange,
                          contract.currency,
                          contract.secType)


@attr.s(auto_attribs=True, slots=True)
class IBOption(IBContract):
    expiration: str
    strike: float
    right: str
    multiplier: str
    sec_type: str = IBSecType.OPT.name

    @classmethod
    def from_ibc(cls, contract: ibc.Contract, sender: str):
        return IBOption(sender,
                        contract.symbol,
                        contract.conId,
                        contract.exchange,
                        contract.currency,
                        contract.lastTradeDateOrContractMonth,
                        contract.strike,
                        contract.right,
                        contract.multiplier)


@attr.s(auto_attribs=True, slots=True)
class IBOrder(Message):
    order_id: int
    action: str
    quantity: float
    order_type: str
    account: str

    @classmethod
    def from_ibc(cls, order: ibc.Order, sender: str):
        return IBOrder(sender,
                       order.orderId,
                       order.action,
                       order.totalQuantity,
                       order.orderType,
                       order.account)


@attr.s(auto_attribs=True, slots=True)
class IBOrderStatus(Message):
    status: str
    filled: int
    remaining: int

    @classmethod
    def from_ibc(cls, status: ibc.OrderStatus, sender: str):
        state = 'done' if status.status in status.DoneStates else 'active'
        return IBOrderStatus(sender, state, status.filled, status.remaining)


@attr.s(auto_attribs=True, slots=True)
class IBTrade(Message):
    contract: IBContract
    order: IBOrder
    status: IBOrderStatus

    @classmethod
    def from_ibc(cls, trade: ibc.Trade, sender: str):
        contract = IBContract.from_ibc(trade.contract, sender)
        order = IBOrder.from_ibc(trade.order, sender)
        status = IBOrderStatus.from_ibc(trade.orderStatus, sender)
        return IBTrade(sender, contract, order, status)

    @classmethod
    def from_json(cls, s, *popattrs):
        j = json.loads(s)
        j['order'] = IBOrder.from_dict(j['order'])
        j['contract'] = IBContract.from_dict(j['contract'])
        j['status'] = IBOrderStatus.from_dict(j['status'])
        return super().from_dict(j)


@attr.s(auto_attribs=True, slots=True)
class IBPlaceTrade(Request):
    action: str
    account: str
    quantity: float
    top_price: float
    bottom_price: float

    sec_type: str = ''
    con_id: int = 0
    symbol: str = ''
    exchange: str = ''
    currency: str = ''
    expiration: str = ''
    strike: float = 0.0
    right: str = ''
    multiplier: float = 0.0


# ============= Coordinator =============

@attr.s(auto_attribs=True, slots=True)
class IBUserMsg(Request):
    trading_mode: str
    ib_username: str
    ib_password: str = ""


@attr.s(auto_attribs=True, slots=True)
class IBUserStatusMsg(Response):
    user_status: str


@attr.s(auto_attribs=True, slots=True)
class RequestStatusMsg(Request):
    # todo: remove
    status: str
    details: str = ""
