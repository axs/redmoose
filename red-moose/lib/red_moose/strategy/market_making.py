import logging
from decimal import Decimal as D
from math import floor, ceil

log = logging.getLogger(__name__)


class MarketMaking:
    def __init__(self, **kwargs):
        self._vol_to_spread_multiplier = D('1.8')  # greater than 1
        self._min_spread = D('.30')  # pct
        self._max_spread = D('.60')  # pct

        self._time_left = .01
        self._closing_time = 1.0

        self._price = D('68.88')
        self._balance = D('100')
        self._target_inventory = D('100')
        self._quote_balance = D('600')

        self._q_adjustment_factor = D('1')  # D("1e5") / inventory_in_base
        self._vol = D('.92')
        self._inventory_risk_aversion = D('.35')  # risk aversion
        self._kappa = D('12.1')  # orderbook lquidity. smaller -> wider spread
        self._price_quantum = D('.01')

    @property
    def min_limit_bid(self):
        return self.price * (1 - self._max_spread * self.spread_inflation_due_to_volatility)

    @property
    def max_limit_bid(self):
        return self.price * (1 - self._min_spread * self.spread_inflation_due_to_volatility)

    @property
    def min_limit_ask(self):
        return self.price * (1 + self._min_spread * self.spread_inflation_due_to_volatility)

    @property
    def max_limit_ask(self):
        return self.price * (1 + self._max_spread * self.spread_inflation_due_to_volatility)

    @property
    def spread_inflation_due_to_volatility(self):
        return max(self._vol_to_spread_multiplier * self.vol, self.price * self._min_spread) / (
                self.price * self._min_spread)

    @property
    def inventory_in_base(self):
        return self._quote_balance / self._price + self._balance

    @property
    def mid_price_variance(self):
        return self.vol ** 2

    @property
    def q(self):
        return (self.balance - D(str(self.target_inventory))) * self._q_adjustment_factor

    @property
    def inventory_risk_aversion(self):
        return self._inventory_risk_aversion

    @inventory_risk_aversion.setter
    def inventory_risk_aversion(self, v):
        self._inventory_risk_aversion = v

    @property
    def vol(self):
        return self._vol

    @vol.setter
    def vol(self, v):
        self._vol = v

    @property
    def target_inventory(self):
        return self._target_inventory

    @target_inventory.setter
    def target_inventory(self, v):
        self._target_inventory = v

    @property
    def quote_balance(self):
        return self._quote_balance

    @quote_balance.setter
    def quote_balance(self, v):
        self._quote_balance = v

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, v):
        self._balance = v

    @property
    def time_left(self):
        return self._time_left

    @time_left.setter
    def time_left(self, v):
        self._time_left = v

    @property
    def closing_time(self):
        return self._closing_time

    @closing_time.setter
    def closing_time(self, v):
        self._closing_time = v

    @property
    def kappa(self):
        return self._kappa

    @kappa.setter
    def kappa(self, v):
        self._kappa = v

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, v):
        self._price = v

    @property
    def time_left_fraction(self):
        return D(str(self.time_left / self.closing_time))

    def tick_up(self, some__price):
        return (ceil(some__price / self._price_quantum) + 1) * self._price_quantum

    def tick_down(self, some__price):
        return (floor(some__price / self._price_quantum) - 1) * self._price_quantum

    def market_proposal(self):
        self._reserved_price = self._price - (
                self.q * self.inventory_risk_aversion * self.mid_price_variance * self.time_left_fraction)
        self._optimal_spread = (self.inventory_risk_aversion * self.mid_price_variance *
                                self.time_left_fraction + 2 *
                                D(1 + self.inventory_risk_aversion / self.kappa).ln() /
                                self.inventory_risk_aversion)

        ask = self._reserved_price + self._optimal_spread / 2
        bid = self._reserved_price - self._optimal_spread / 2

        return bid, ask

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )


class SimpleMarketMaking:
    """k = 0 - 1
       b = current inventory
       b0 = initial inventory
    """

    @staticmethod
    def bid(k, b, b0):
        if b > b0:
            return 1
        return 1 - k + ((b / b0) ** 2) * k

    @staticmethod
    def ask(k, b, b0):
        if b > b0:
            return 1
        return 1 / (1 - k + ((b / b0) ** 2) * k)


if __name__ == '__main__':
    mm = MarketMaking()
    b, a = mm.market_proposal()
    print(f"{b} / {a}")
    print(mm)
