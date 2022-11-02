class Topics:
    # ib - ib-bridge
    # ps - polar-shark
    # rm - red-moose

    # topics on the `ib-user` exchange
    COORDINATOR_USER_START = 'coordinator.user.start'  # IBUserMsg; ps listens
    COORDINATOR_USER_STOP = 'coordinator.user.stop'  # IBUserMsg; ps listens
    COORDINATOR_USER_STATUS_REQUEST = 'coordinator.user.status.request'  # IBUserMsg; ps listens
    COORDINATOR_USER_STATUS = 'coordinator.user.status'  # IBUserStatusMsg; ps delivers

    # ==== USER-SPECIFIC ====
    # topics on the `{ib-username}-{trading-mode}.comm` exchanges

    IB_PNL_SINGLE_REQUEST = 'ib.pnl.single.request'  # (acc: str, model-code: str, con-id: int); ib listens
    IB_PNL_SINGLE_CANCEL = 'ib.pnl.single.cancel'  # (acc: str, model-code: str, con-id: int); ib listens
    IB_PNL_SINGLE_UPDATE = 'ib.pnl.single.update'  # ib_insync.PnLSingle pickle; ib delivers

    IB_POSITIONS_REQUEST = 'ib.positions.request'  # Request; ib listens
    IB_POSITION_UPDATE = 'ib.position.update'  # PositionMsg; ib delivers

    IB_STATUS_UPDATE = 'ib.status.update'  # polar_shark.comm.messages.StatusMsg pickle; ib delivers
    IB_ERROR_EVENT = 'ib.error.event'  # polar_shark.comm.messages.ErrorMsg pickle; ib delivers

    IB_TICKER_REQUEST = 'ib.ticker.request'  # ConIdReq; ib listens
    IB_TICKER_CANCEL = 'ib.ticker.cancel'  # ConIdReq; ib listens
    IB_TICKER_UPDATE = 'ib.ticker.update'  # ib_insync.Ticker pickle; ib delivers

    IB_TRADES_REQUEST = 'ib.trades.request'  # Request; ib listens
    IB_TRADE_UPDATE = 'ib.trade.update'  # IBTrade; ib delivers
    IB_TRADE_SUBMIT = 'ib.trade.submit'  # IBPlaceTrade; ib listens

    DASH_UPDATES = 'dash.update'  # JSON of polar_shark.dash.helpers.utils.DashPosition; ps delivers

    # ========================

    # topics on the `commands` exchange
    IQ_TICKER_REQUEST = 'IQFEED_TICKER_REQ'  # symbol str; rm listens - delivered on `iqfeed` echange
    TRADES_ORPHANS = 'orphans.update'
    PRICE_ARBITRATION_KEY = 'verify.prices'
