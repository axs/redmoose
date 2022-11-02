import enum


class RoutingKey(enum.Enum):
    # PnL Single
    IB_PNL_SINGLE_REQUEST = 'ib.pnl.single.request'  #: request pnl
    IB_PNL_SINGLE_CANCEL = 'ib.pnl.single.cancel'  #: cancel pnl
    IB_PNL_SINGLE_UPDATE = 'ib.pnl.single.update'  #: receive pnl update
    # Positions
    IB_POSITIONS_REQUEST = 'ib.positions.request'  #: request all positions
    IB_POSITIONS_UPDATE = 'ib.position.update'  #: receive position update
    # Status Updates
    IB_STATUS_UPDATE = 'ib.status.update'  #: receive status update
    IB_ERROR_EVENT = 'ib.error.event'  #: receive error event
    # Tickers
    IB_TICKER_REQUEST = 'ib.ticker.request'  #: request ticker
    IB_TICKER_CANCEL = 'ib.ticker.cancel'  #: cancel ticker
    IB_TICKER_UPDATE = 'ib.ticker.update'  #: receive ticker update
    # Trades
    IB_TRADE_REQUEST = 'ib.trades.request'  #: request all open trades
    IB_TRADE_UPDATE = 'ib.trade.update'  #: receive trade update
    IB_TRADE_SUBMIT = 'ib.trade.submit'  #: submit trade

    @staticmethod
    def updates():
        return 


 


def from_json(cls, s, *popattrs):
    # from_json(s,"sending_time","request_id", "blah"):
    d = json.loads(s)
    name_vals = [ (p, d.pop(p)) for p in popattrs]
    obj = cls(**d)
    for n,v in name_vals:
        setattr(obj,n,v)
    return obj



@attr.s(auto_attribs=True, slots=True)
class Request(Json):
    request_id: str = attr.ib(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.request_id = uuid.uuid1().hex

    @classmethod
    def from_json(cls, s):
        d = json.loads(s)
        sending_time = d.pop("sending_time")
        request_id = d.pop("request_id")
        obj = cls(**d)
        obj.sending_time = sending_time
        obj.request_id = request_id
        return obj


@attr.s(auto_attribs=True, slots=True)
class Response(Json):
    request_id: str


@attr.s(auto_attribs=True, slots=True)
class IBPosition(Pickle):
    pass


@attr.s(auto_attribs=True, slots=True)
class IBContract(Message):
    symbol: str
    con_id: int
    exchange: str
    currency: str
    sec_type: str

    @classmethod
    def from_ibc(cls, contract: ibc.Contract, sender: str):
        if isinstance(contract, ibc.Stock):
            return IBStock.from_ibc(contract, sender)
        elif isinstance(contract, ibc.Option):
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

    @classmethod
    def from_ibc(cls, order: ibc.Order, sender: str):
        return IBOrder(sender, order.orderId, order.action, order.totalQuantity)


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
